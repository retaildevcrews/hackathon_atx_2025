from __future__ import annotations

import logging
from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    app_name: str = Field(default="agent")
    app_version: str = Field(default="0.1.0")

    azure_openai_api_key: str | None = Field(default=None, alias="AZURE_OPENAI_API_KEY")
    azure_openai_endpoint: str | None = Field(default=None, alias="AZURE_OPENAI_ENDPOINT")
    azure_openai_deployment: str | None = Field(default=None, alias="AZURE_OPENAI_DEPLOYMENT")
    azure_openai_api_version: str | None = Field(default="2024-02-01", alias="AZURE_OPENAI_API_VERSION")

    log_level: str = Field(default="INFO")

    azure_search_endpoint: str | None = Field(default=None, alias="AZURE_SEARCH_ENDPOINT")
    azure_search_api_key: str | None = Field(default=None, alias="AZURE_SEARCH_API_KEY")
    azure_search_index: str | None = Field(default=None, alias="AZURE_SEARCH_INDEX")

    # Criteria API integration
    # Default to local criteria_api dev port; override in container with http://criteria_api:8000
    criteria_api_url: str = Field(default="http://localhost:8000", alias="CRITERIA_API_URL")

    # Evaluation configuration
    max_evaluation_chunks: int = Field(default=10, alias="MAX_EVALUATION_CHUNKS")

    class Config:
        populate_by_name = True
        env_file = ".env"
        case_sensitive = False


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()  # type: ignore[arg-type]


def configure_logging(level: str | None = None) -> None:
    log_level = (level or get_settings().log_level).upper()
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    logging.getLogger("uvicorn.error").setLevel(log_level)
    logging.getLogger("uvicorn.access").setLevel(log_level)


configure_logging()
