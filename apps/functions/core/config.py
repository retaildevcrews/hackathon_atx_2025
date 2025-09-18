import os
from dataclasses import dataclass
from typing import List

@dataclass(frozen=True)
class Settings:
    storage_account_url: str
    blob_container: str
    max_bytes: int
    internal_upload_key_sha256: str
    allowed_context_types: List[str]
    log_level: str = "INFO"
    disable_internal_upload_auth: bool = False


def load_settings() -> Settings:
    storage_account_url = os.getenv("STORAGE_ACCOUNT_URL")
    blob_container = os.getenv("BLOB_CONTAINER")
    max_bytes = int(os.getenv("MAX_BYTES", "10485760"))  # default 10MB
    internal_upload_key_sha256 = os.getenv("INTERNAL_UPLOAD_KEY_SHA256")
    disable_auth = os.getenv("DISABLE_INTERNAL_UPLOAD_AUTH", "false").lower() == "true"
    allowed_context_types = [s.strip() for s in os.getenv("ALLOWED_CONTEXT_TYPES", "").split(",") if s.strip()]
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()

    if not storage_account_url:
        raise ValueError("STORAGE_ACCOUNT_URL missing")
    if not blob_container:
        raise ValueError("BLOB_CONTAINER missing")
    if not disable_auth:
        if not internal_upload_key_sha256 or len(internal_upload_key_sha256) < 40:
            raise ValueError("INTERNAL_UPLOAD_KEY_SHA256 missing or too short (or set DISABLE_INTERNAL_UPLOAD_AUTH=true for demo bypass)")
    else:
        internal_upload_key_sha256 = internal_upload_key_sha256 or ""
    if not allowed_context_types:
        raise ValueError("ALLOWED_CONTEXT_TYPES empty")

    return Settings(
        storage_account_url=storage_account_url,
        blob_container=blob_container,
        max_bytes=max_bytes,
        internal_upload_key_sha256=internal_upload_key_sha256.lower(),
        allowed_context_types=allowed_context_types,
        log_level=log_level,
        disable_internal_upload_auth=disable_auth,
    )
