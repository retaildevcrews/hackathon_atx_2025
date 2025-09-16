from __future__ import annotations

import logging
from functools import lru_cache

from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

from config import get_settings

logger = logging.getLogger(__name__)


class ChainService:
    def __init__(self) -> None:
        self.settings = get_settings()
        if not (
            self.settings.azure_openai_api_key
            and self.settings.azure_openai_endpoint
            and self.settings.azure_openai_deployment
        ):
            self.llm = None
            logger.warning("LangChain AzureChatOpenAI not configured; chain calls will be stubbed.")
        else:
            # AzureChatOpenAI expects azure_endpoint and deployment_name
            self.llm = AzureChatOpenAI(
                api_key=self.settings.azure_openai_api_key,
                azure_endpoint=self.settings.azure_openai_endpoint,
                azure_deployment=self.settings.azure_openai_deployment,
                api_version=self.settings.azure_openai_api_version,
                temperature=0.2,
            )
        self.prompt = ChatPromptTemplate.from_messages(
            [
                ("system", "You are a concise assistant. Provide clear, direct answers."),
                ("user", "{input}"),
            ]
        )

    def run(self, user_input: str) -> str:
        if not self.llm:
            return f"[stubbed chain response] {user_input}"
        try:
            chain = self.prompt | self.llm
            result = chain.invoke({"input": user_input})
            return result.content  # type: ignore[attr-defined]
        except Exception as e:  # noqa: BLE001
            logger.exception("LangChain chain invocation failed: %s", e)
            return f"[chain error] {e}"


@lru_cache(maxsize=1)
def get_chain_service() -> ChainService:
    """Return a cached singleton ChainService instance.

    Using an LRU cache avoids re-instantiating the LangChain LLM and prompt
    objects on every request, reducing overhead. Settings are loaded once at
    process start; restart the process to pick up changed environment vars.
    """
    return ChainService()
