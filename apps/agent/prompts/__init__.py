"""
Prompt templates for document evaluation using LangChain.
"""

from .evaluation_prompts import (
    BATCH_EVALUATION_PROMPT,
    SUMMARY_PROMPT,
    get_batch_evaluation_template,
    get_summary_template,
)

__all__ = [
    "BATCH_EVALUATION_PROMPT",
    "SUMMARY_PROMPT",
    "get_batch_evaluation_template",
    "get_summary_template",
]
