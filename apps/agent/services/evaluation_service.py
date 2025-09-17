from __future__ import annotations

import asyncio
import json
import logging
import re
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional

from pypdf import PdfReader
from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

from config import get_settings

logger = logging.getLogger(__name__)

RUBRIC_PATH = Path(__file__).parent.parent / "sample_data" / "tv_rubric.json"
PDF_SAMPLE_PATH = Path(__file__).parent.parent / "sample_data" / "LG_SPEC-SHEET_UM670H_Series_122327_LR[20240131_040303].pdf"

SYSTEM_PROMPT_TEMPLATE = (
    "You are an expert document evaluator. Evaluate the following document content against the given criterion.\n\n"
    "Instructions:\n"
    "- Provide a score strictly following the scale and rules defined in the Scoring Criteria.\n"
    "- Explain the reasoning in detail, including why the score was chosen.\n"
    "- Extract specific evidence from the document to support the reasoning. Evidence must be a single concise quote or paraphrased excerpt string (not a list).\n"
    "- If no relevant evidence exists, use an empty string for evidence and explain why in reasoning.\n"
    "- Output must be ONLY a single JSON object, no preamble or explanation.\n"
    "- Do NOT wrap JSON in markdown fences or backticks. No ``` anywhere.\n"
    "- Begin the response with an opening curly brace and end it with a closing curly brace."
)


def slugify(name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return slug or "item"


@lru_cache(maxsize=1)
def load_rubric() -> Dict[str, Any]:
    with RUBRIC_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


class EvaluationService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.llm: Optional[AzureChatOpenAI]
        if not (
            self.settings.azure_openai_api_key
            and self.settings.azure_openai_endpoint
            and self.settings.azure_openai_deployment
        ):
            self.llm = None
            logger.error("Azure OpenAI not fully configured; evaluation endpoint will 500 on use.")
        else:
            if "realtime" in self.settings.azure_openai_deployment.lower():
                logger.error("Realtime deployment not supported for chat completions evaluation.")
            self.llm = AzureChatOpenAI(
                api_key=self.settings.azure_openai_api_key,
                azure_endpoint=self.settings.azure_openai_endpoint,
                azure_deployment=self.settings.azure_openai_deployment,
                api_version=self.settings.azure_openai_api_version,
                temperature=0,
            )
        # Build a reusable prompt (system + user)
        self.base_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", SYSTEM_PROMPT_TEMPLATE),
                ("user", "{user_content}"),
            ]
        )
        # Chain only if llm configured
        self.chain = (self.base_prompt | self.llm) if self.llm else None

    async def evaluate(self, rubric_name: str | None, model_params: Dict[str, Any] | None, max_concurrency: int | None) -> Dict[str, Any]:
        rubric = load_rubric()
        if rubric_name and rubric.get("rubric_name") != rubric_name:
            raise ValueError(f"Unsupported rubric_name '{rubric_name}'")

        rubric_name_val = rubric.get("rubric_name", "unknown_rubric")
        criteria: List[Dict[str, Any]] = rubric.get("criteria", [])
        rubric_id = rubric_name_val

        # Extract PDF text (no chunking yet)
        pdf_reader = PdfReader(str(PDF_SAMPLE_PATH))
        pdf_text = "\n".join(page.extract_text() or "" for page in pdf_reader.pages)

        if not self.llm or not self.chain:
            raise RuntimeError("Azure OpenAI client not configured")

        semaphore = asyncio.Semaphore(max_concurrency or 5)

        async def eval_single(criterion: Dict[str, Any]) -> Dict[str, Any]:
            async with semaphore:
                c_name = criterion.get("name", "")
                weight = criterion.get("weight")
                description = criterion.get("description")
                definition = criterion.get("definition")
                criterion_id = slugify(c_name)

                def_text_lines: List[str] = []
                if isinstance(definition, dict):
                    for k, v in definition.items():
                        def_text_lines.append(f"{k}: {v}")
                def_text = "\n".join(def_text_lines)

                user_content = (
                    f"Criterion: {c_name}\n"
                    f"Description: {description}\n"
                    f"Weight: {weight}\n\n"
                    f"Scoring Criteria:\n{def_text}\n\n"
                    f"Document Content: <PDF content attached>\n"
                )
                full_user_content = f"{user_content}\n\nFull Document Text:\n{pdf_text}"
                # Allow limited model params per request (temperature, top_p, etc.)
                chain_to_use = self.chain
                if model_params and self.llm:
                    allowed_keys = {"temperature", "top_p", "max_tokens", "presence_penalty", "frequency_penalty", "stop"}
                    bound_args = {k: v for k, v in model_params.items() if k in allowed_keys}
                    if bound_args:
                        chain_to_use = self.base_prompt | self.llm.bind(**bound_args)

                try:
                    logger.debug("sending_prompt", extra={"criterion": c_name, "overrides": list(bound_args.keys()) if 'bound_args' in locals() else []})
                    result = await chain_to_use.ainvoke({"user_content": full_user_content})  # type: ignore[union-attr]
                    raw_response = getattr(result, "content", str(result))  # type: ignore[attr-defined]
                except Exception:
                    logger.exception("Criterion evaluation failed: %s", c_name)
                    raise

                logger.info("raw_model_response", extra={"criterion": c_name, "raw": raw_response})

                def parse_response(content: str) -> Dict[str, Any] | None:
                    # Direct attempt
                    try:
                        return json.loads(content)
                    except Exception:
                        pass
                    # Fenced code block ```json ... ``` or ``` ... ```
                    fence_match = re.search(r"```(?:json)?\n(.*?)```", content, re.DOTALL | re.IGNORECASE)
                    if fence_match:
                        inner = fence_match.group(1).strip()
                        try:
                            return json.loads(inner)
                        except Exception:
                            pass
                    # First JSON object substring heuristic
                    brace_start = content.find('{')
                    brace_end = content.rfind('}')
                    if brace_start != -1 and brace_end != -1 and brace_end > brace_start:
                        snippet = content[brace_start: brace_end + 1]
                        try:
                            return json.loads(snippet)
                        except Exception:
                            pass
                    return None

                parsed_obj = parse_response(raw_response)
                score: Optional[int] = None
                reasoning = ""
                evidence = ""
                if parsed_obj:
                    score_val = parsed_obj.get("score")
                    if isinstance(score_val, int):
                        score = score_val
                    reasoning = parsed_obj.get("reasoning") or ""
                    evidence_field = parsed_obj.get("evidence")
                    if isinstance(evidence_field, list):
                        evidence = " ".join(str(x) for x in evidence_field)
                    elif isinstance(evidence_field, str):
                        evidence = evidence_field
                else:
                    reasoning = raw_response

                entry = {
                    "criterion_id": criterion_id,
                    "criterion_name": c_name,
                    "criterion_description": description,
                    "criterion_definition": definition,
                    "weight": weight,
                    "score": score,
                    "reasoning": reasoning,
                    "evidence": evidence,
                    "document_chunk": None,
                }
                logger.info("parsed_model_response", extra={"criterion": c_name, "parsed": entry})
                return entry

        tasks = [asyncio.create_task(eval_single(c)) for c in criteria]
        results = await asyncio.gather(*tasks)

        effective_model_params = {"temperature": 0}
        if model_params:
            effective_model_params.update(model_params)

        return {
            "rubric_id": rubric_id,
            "rubric_name": rubric_name_val,
            "criteria": results,
            "model_params": effective_model_params,
            "system_prompt_template": SYSTEM_PROMPT_TEMPLATE,
        }


@lru_cache(maxsize=1)
def get_evaluation_service() -> EvaluationService:
    return EvaluationService()
