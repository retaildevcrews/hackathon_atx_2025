from __future__ import annotations
import hashlib
import httpx
import os
from dataclasses import dataclass
from .exceptions import UploadError, AuthError, ValidationError, ServerError
from typing import BinaryIO, Iterable, Optional

CHUNK_SIZE = 256 * 1024

@dataclass
class UploadResult:
    blob_path: str
    sha256: str
    size: int

class UploadClient:
    """Client for the Generic Upload Function.

    Environment variables respected:
      UPLOAD_ENDPOINT  - Base URL, e.g. https://func.azurewebsites.net
      UPLOAD_SECRET    - Raw shared secret (optional if bypass enabled server-side)
      UPLOAD_TIMEOUT_S - Request timeout seconds (default 30)
    """

    def __init__(self, endpoint: str | None = None, secret: str | None = None, timeout: float | None = None, client: Optional[httpx.Client] = None):
        self.endpoint = (endpoint or os.getenv("UPLOAD_ENDPOINT") or "").rstrip("/")
        if not self.endpoint:
            raise ValueError("endpoint required (arg or UPLOAD_ENDPOINT env)")
        self.secret = secret if secret is not None else os.getenv("UPLOAD_SECRET")
        self.timeout = timeout or float(os.getenv("UPLOAD_TIMEOUT_S", "30"))
        self._client = client or httpx.Client(timeout=self.timeout)

    def close(self):
        self._client.close()

    def _iter_file(self, f: BinaryIO) -> Iterable[bytes]:
        while True:
            chunk = f.read(CHUNK_SIZE)
            if not chunk:
                break
            yield chunk

    def upload(self, context_type: str, context_id: str, file_obj: BinaryIO, filename: str) -> UploadResult:
        if not context_type:
            raise ValidationError("context_type required")
        if not context_id:
            raise ValidationError("context_id required")
        if not filename:
            raise ValidationError("filename required")

        # Read full content only once (file sizes limited to 10MB contract)
        data = file_obj.read()
        size = len(data)
        sha256 = hashlib.sha256(data).hexdigest()

        files = {
            "file": (filename, data),
        }
        form = {
            "contextType": context_type,
            "contextId": context_id,
        }
        headers = {}
        if self.secret:
            headers["X-Internal-Upload-Key"] = self.secret

        url = f"{self.endpoint}/api/upload"
        try:
            resp = self._client.post(url, data=form, files=files, headers=headers)
        except httpx.HTTPError as e:
            raise UploadError(f"network error: {e}") from e

        if resp.status_code == 401:
            raise AuthError("unauthorized (check secret or bypass mode)")
        if resp.status_code == 400:
            raise ValidationError(resp.text or "bad request")
        if resp.status_code >= 500:
            raise ServerError(f"server error {resp.status_code}: {resp.text}")
        if resp.status_code not in (200, 201):
            raise UploadError(f"unexpected status {resp.status_code}: {resp.text}")

        try:
            payload = resp.json()
        except ValueError as e:
            raise UploadError("invalid JSON response") from e

        return UploadResult(
            blob_path=payload.get("blobPath"),
            sha256=payload.get("sha256"),
            size=payload.get("size"),
        )

    def upload_path(self) -> str:
        return f"{self.endpoint}/api/upload"
