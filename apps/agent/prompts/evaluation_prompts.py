"""
Evaluation prompt templates for document assessment against rubrics.
"""

from langchain_core.prompts import ChatPromptTemplate

SINGLE_EVALUATION_PROMPT = """
You are an expert document evaluator. Evaluate the following document content against the given criterion.

Criterion: {name}
Description: {description}
Weight: {weight}

Scoring Criteria:
{definition}

Document Content:
{document_chunk_content}

Instructions:
- Provide a score strictly following the scale and rules defined in the Scoring Criteria.
- Explain the reasoning in detail, including why the score was chosen.
- Extract specific evidence from the document to support the reasoning. Evidence must be short, direct quotes or paraphrased excerpts, not general summaries.
- If no relevant evidence exists, output an empty list for evidence and explain why in reasoning.
- Output must be **valid JSON only**, with no extra text.

Output structure:
{
    "score": float,
    "reasoning": "string",
    "evidence": ["string1", "string2"]
}
 """


BATCH_EVALUATION_PROMPT = """
You are an expert document evaluator. Evaluate the following document content against ALL the given criteria in a single comprehensive analysis.
Each criterion includes:
- **Criteria Name** – The title or label of the criterion.
- **Weight** – The relative importance of the criterion in the overall evaluation.
- **Description** – A detailed explanation of what the criterion measures.
- **Definition** – Specifies the scoring scale and method to be used for evaluation.


Rubric: {rubric_name}
Description: {rubric_description}

Criteria to Evaluate:
{criteria_details}

Document Content:
{document_content}

INSTRUCTIONS:
- Produce exactly one evaluation object for each criterion listed. Each evaluation.criterion_name must match the input criterion name exactly.
- Score: numeric according to the criterion's scoring_scale (float). Use the scoring_definition provided for each criterion
- Reasoning: provide a concise, detailed explanation for the score. If evidence is missing, explicitly state that in the reasoning.
- Evidence: Extract specific evidence from the document to support the reasoning. Evidence must be short, direct quotes or paraphrased excerpts, not general summaries. If no evidence, return an empty array.
- Holistic view: consider interactions between criteria and how they affect one another. Summarize these interactions in the "overall_reasoning" field.
- **Output must be valid JSON only. No extra text, no comments, and no trailing commas.**

OUTPUT JSON STRUCTURE:
{
  "evaluation": [
    {
      "criterion_name": "string",
      "score": float,
      "reasoning": "string",
      "evidence": ["string1", "string2"]
    }
  ]
}

"""


SUMMARY_PROMPT = """
You are an expert evaluator creating a comprehensive summary of a document evaluation.

Rubric: {rubric_name}
Overall Score: {overall_score:.2f}/5.0

Individual Criterion Evaluations:
{evaluations_summary}

Create a comprehensive summary including:
1. Overall assessment of the document
2. Key strengths (3-5 items)
3. Areas for improvement (3-5 items)
4. Executive summary paragraph

Output as JSON:
{{
    "summary": "string",
    "strengths": ["string1", "string2"],
    "improvements": ["string1", "string2"]
}}
"""


def get_batch_evaluation_template() -> ChatPromptTemplate:
    """Get the batch evaluation prompt template."""
    return ChatPromptTemplate.from_template(BATCH_EVALUATION_PROMPT)


def get_summary_template() -> ChatPromptTemplate:
    """Get the summary prompt template."""
    return ChatPromptTemplate.from_template(SUMMARY_PROMPT)
