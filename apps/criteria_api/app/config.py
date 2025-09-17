from pydantic import model_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables.

    Environment Variables:
        ALLOW_ZERO_WEIGHT: If true, zero weights are permitted. (default: False)
        DEFAULT_RUBRIC_WEIGHT: Weight applied when omitted on create/update (default: 1.0)
        MAX_RUBRIC_WEIGHT: Upper bound for a single criterion weight (default: 1_000_000.0)
        RUBRIC_WEIGHT_MIN: Lower bound for a single criterion weight (default: 0.05)
        RUBRIC_WEIGHT_MAX: Upper bound for a single criterion weight (default: 1.0)
        RUBRIC_WEIGHT_STEP: Step increment for a single criterion weight (default: 0.05)
    """

    ALLOW_ZERO_WEIGHT: bool = False
    DEFAULT_RUBRIC_WEIGHT: float = 1.0
    MAX_RUBRIC_WEIGHT: float = 1_000_000.0
    RUBRIC_WEIGHT_MIN: float = 0.05
    RUBRIC_WEIGHT_MAX: float = 1.0
    RUBRIC_WEIGHT_STEP: float = 0.05

    @model_validator(mode="after")
    def validate_default(self):  # type: ignore[override]
        # Validate bounds configuration
        if self.RUBRIC_WEIGHT_STEP <= 0:
            raise ValueError("RUBRIC_WEIGHT_STEP must be > 0")
        if self.RUBRIC_WEIGHT_MAX <= self.RUBRIC_WEIGHT_MIN:
            raise ValueError("RUBRIC_WEIGHT_MAX must be greater than RUBRIC_WEIGHT_MIN")

        # Validate relation with ALLOW_ZERO_WEIGHT (legacy behavior)
        if not self.ALLOW_ZERO_WEIGHT and self.RUBRIC_WEIGHT_MIN <= 0:
            # Keep behavior consistent: if zero not allowed, min must be > 0
            raise ValueError("RUBRIC_WEIGHT_MIN must be > 0 unless ALLOW_ZERO_WEIGHT is true")

        # Validate DEFAULT_RUBRIC_WEIGHT against range and step
        if not (self.RUBRIC_WEIGHT_MIN <= self.DEFAULT_RUBRIC_WEIGHT <= self.RUBRIC_WEIGHT_MAX):
            raise ValueError(
                f"DEFAULT_RUBRIC_WEIGHT must be between {self.RUBRIC_WEIGHT_MIN} and {self.RUBRIC_WEIGHT_MAX}"
            )
        # Step alignment check (tolerant to float error)
        n = round(self.DEFAULT_RUBRIC_WEIGHT / self.RUBRIC_WEIGHT_STEP)
        if abs(self.DEFAULT_RUBRIC_WEIGHT - (n * self.RUBRIC_WEIGHT_STEP)) > 1e-9:
            raise ValueError(
                f"DEFAULT_RUBRIC_WEIGHT must align to RUBRIC_WEIGHT_STEP={self.RUBRIC_WEIGHT_STEP}"
            )
        return self


settings = Settings()
