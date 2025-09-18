import hashlib
from .errors import AuthError
from .logging_utils import get_logger

HEADER_NAME = "X-Internal-Upload-Key"

def verify_shared_secret(provided: str | None, expected_sha256_hex: str, bypass: bool = False):
    if bypass:
        logger = get_logger()
        logger.warning("auth.bypass.enabled - DO NOT USE IN PROD")
        return
    if not provided:
        raise AuthError("missing secret header")
    digest = hashlib.sha256(provided.encode("utf-8")).hexdigest()
    if digest.lower() != expected_sha256_hex.lower():
        raise AuthError("invalid shared secret")
