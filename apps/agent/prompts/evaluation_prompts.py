"""
Evaluation prompt templates for document assessment against rubrics.
"""

from langchain_core.prompts import ChatPromptTemplate


BATCH_EVALUATION_PROMPT = """
You are an expert document evaluator. Evaluate the following document content against ALL the given criteria in a single comprehensive analysis.

Rubric: {rubric_name}
Domain: {domain}

Criteria to Evaluate:
{criteria_details}

Document Content:
{document_content}

For EACH criterion, evaluate the document and provide:
1. Score (1-5 based on the scoring criteria provided for that criterion)
2. Detailed reasoning for the score
3. Specific evidence from the document (with chunk references if applicable)
4. Recommendations for improvement (if score < 5)
5. Confidence level (0.0-1.0) in your evaluation

Consider the relationships between criteria and provide a holistic evaluation that takes into account how different aspects of the document work together.

Output your response as JSON with the following structure:
{{
    "evaluations": [
        {{
            "criterion_id": "string",
            "score": float,
            "reasoning": "string",
            "evidence": ["string1", "string2"],
            "recommendations": ["string1", "string2"],
            "confidence": float
        }}
    ]
}}

IMPORTANT: Include exactly one evaluation object for each criterion provided. Ensure all criterion_ids match exactly.
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
