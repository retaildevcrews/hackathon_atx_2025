"""Configuration for the evaluation framework."""

import os
from typing import Dict, Any


class Config:
    """Configuration settings for evaluation."""
    
    # LLM Judge settings
    JUDGE_MODEL = os.getenv("JUDGE_MODEL", "gpt-4")
    JUDGE_API_KEY = os.getenv("OPENAI_API_KEY")
    JUDGE_BASE_URL = os.getenv("JUDGE_BASE_URL", "https://api.openai.com/v1")
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
        """Get configuration for the LLM judge."""
        return {
            "model": cls.JUDGE_MODEL,
            "api_key": cls.JUDGE_API_KEY,
            "base_url": cls.JUDGE_BASE_URL,
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