from pydantic import model_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables.

    Environment Variables:
        ALLOW_ZERO_WEIGHT: If true, zero weights are permitted. (default: False)
        DEFAULT_RUBRIC_WEIGHT: Weight applied when omitted on create/update (default: 1.0)
        MAX_RUBRIC_WEIGHT: Upper bound for a single criterion weight (default: 1_000_000.0)
    """

    ALLOW_ZERO_WEIGHT: bool = False
    DEFAULT_RUBRIC_WEIGHT: float = 1.0
    MAX_RUBRIC_WEIGHT: float = 1_000_000.0

    @model_validator(mode="after")
    def validate_default(self):  # type: ignore[override]
        if self.ALLOW_ZERO_WEIGHT:
            if self.DEFAULT_RUBRIC_WEIGHT < 0:
                raise ValueError("DEFAULT_RUBRIC_WEIGHT must be >= 0 when zero allowed")
        else:
            if self.DEFAULT_RUBRIC_WEIGHT <= 0:
                raise ValueError("DEFAULT_RUBRIC_WEIGHT must be > 0 unless zero allowed")
        return self


settings = Settings()
