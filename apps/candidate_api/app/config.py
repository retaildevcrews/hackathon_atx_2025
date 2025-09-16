from functools import lru_cache
from pydantic_settings import BaseSettings
from pydantic import Field
from dotenv import load_dotenv

# Load .env file if present (mirrors criteria_api & agent behavior)
load_dotenv()


class Settings(BaseSettings):
    cosmos_endpoint: str | None = Field(default=None, alias="COSMOSDB_ENDPOINT")
    cosmos_key: str | None = Field(default=None, alias="COSMOSDB_KEY")
    cosmos_database: str = Field(default="candidates_db", alias="COSMOSDB_DATABASE")
    candidates_container: str = Field(default="candidates", alias="COSMOSDB_CANDIDATES_CONTAINER")
    materials_container: str = Field(default="candidate_materials", alias="COSMOSDB_MATERIALS_CONTAINER")
    storage_connection_string: str | None = Field(default=None, alias="AZURE_STORAGE_CONNECTION_STRING")
    materials_container_name: str = Field(default="candidate-materials", alias="CANDIDATE_MATERIALS_CONTAINER")
    max_file_size_mb: int = Field(default=10, alias="MAX_CANDIDATE_FILE_SIZE_MB")
    allowed_mime_prefixes: str = Field(
        default=(
            "application/pdf,"
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document,"  # DOCX
            "text/plain"
        ),
        alias="ALLOWED_CANDIDATE_MIME_PREFIXES",
    )

    class Config:
        env_file = ".env"
        populate_by_name = True

    def allowed_mime_prefix_list(self) -> list[str]:
        return [p.strip() for p in self.allowed_mime_prefixes.split(",") if p.strip()]


@lru_cache
def get_settings() -> Settings:  # type: ignore
    return Settings()


def get_max_file_size_bytes() -> int:
    return get_settings().max_file_size_mb * 1024 * 1024
