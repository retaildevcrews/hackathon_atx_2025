"""Configuration for the evaluation framework."""

import os
from typing import Dict, Any


class Config:
    """Configuration settings for evaluation."""

    # LLM Judge settings (Azure OpenAI)
    JUDGE_MODEL = os.getenv("JUDGE_MODEL", "gpt-4")
    AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
    AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
    AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-08-01-preview")
    JUDGE_TEMPERATURE = float(os.getenv("JUDGE_TEMPERATURE", "0.1"))
    JUDGE_MAX_TOKENS = int(os.getenv("JUDGE_MAX_TOKENS", "2000"))

    # Agent settings
    AGENT_ENDPOINT = os.getenv("AGENT_ENDPOINT", "http://localhost:8000/evaluate")
    AGENT_TIMEOUT = int(os.getenv("AGENT_TIMEOUT", "60"))

    # Evaluation settings
    DATASET_PATH = os.getenv("DATASET_PATH", "evaluation/dataset/test_cases.jsonl")
    REPORTS_DIR = os.getenv("REPORTS_DIR", "evaluation/reports")
    CONSISTENCY_RUNS = int(os.getenv("CONSISTENCY_RUNS", "3"))

    # Scoring thresholds
    MIN_ACCEPTABLE_SCORE = float(os.getenv("MIN_ACCEPTABLE_SCORE", "70.0"))
    HIGH_PERFORMANCE_THRESHOLD = float(os.getenv("HIGH_PERFORMANCE_THRESHOLD", "85.0"))

    @classmethod
    def get_judge_config(cls) -> Dict[str, Any]:
        """Get configuration for the LLM judge (Azure OpenAI)."""
        return {
            "model": cls.JUDGE_MODEL,
            "api_key": cls.AZURE_OPENAI_API_KEY,
            "azure_endpoint": cls.AZURE_OPENAI_ENDPOINT,
            "api_version": cls.AZURE_OPENAI_API_VERSION,
            "temperature": cls.JUDGE_TEMPERATURE,
            "max_tokens": cls.JUDGE_MAX_TOKENS,
        }

    @classmethod
    def get_agent_config(cls) -> Dict[str, Any]:
        """Get configuration for the agent endpoint."""
        return {
            "endpoint": cls.AGENT_ENDPOINT,
            "timeout": cls.AGENT_TIMEOUT,
        }
