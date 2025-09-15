"""Evaluation framework package."""

from .evaluator import run_evaluation, Evaluator
from .llm_judge import LLMJudge
from .metrics import EvaluationMetrics
from .config import Config

__version__ = "1.0.0"
__all__ = ["run_evaluation", "Evaluator", "LLMJudge", "EvaluationMetrics", "Config"]