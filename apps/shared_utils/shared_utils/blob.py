import os
import logging
from functools import lru_cache
from typing import BinaryIO, Optional
from azure.storage.blob import BlobServiceClient, ContentSettings

logger = logging.getLogger(__name__)

@lru_cache()
def get_blob_settings():
    return {
        "conn_str": os.getenv("AZURE_STORAGE_CONNECTION_STRING", ""),
        "default_container": os.getenv("CANDIDATE_MATERIALS_CONTAINER", "candidate-materials"),
    }

class BlobClientWrapper:
    def __init__(self):
        s = get_blob_settings()
        self.conn_str = s["conn_str"]
        self.enabled = bool(self.conn_str)
        if self.enabled:
            self.service = BlobServiceClient.from_connection_string(self.conn_str)
        else:
            self.service = None
            logger.warning("Blob storage disabled: no AZURE_STORAGE_CONNECTION_STRING set")

    def ensure_container(self, name: Optional[str] = None):
        if not self.enabled:
            return
        cname = name or get_blob_settings()["default_container"]
        try:
            self.service.create_container(cname)  # type: ignore
        except Exception:
            pass

    def upload_bytes(self, data: bytes, blob_path: str, container: Optional[str] = None, content_type: Optional[str] = None) -> str:
        if not self.enabled:
            # Fallback path indicator
            return f"disabled://{blob_path}"
        cname = container or get_blob_settings()["default_container"]
        self.ensure_container(cname)
        blob_client = self.service.get_blob_client(container=cname, blob=blob_path)  # type: ignore
        blob_client.upload_blob(data, overwrite=True, content_settings=ContentSettings(content_type=content_type))
        return blob_client.url

_blob_singleton: Optional[BlobClientWrapper] = None

def get_blob_client() -> BlobClientWrapper:
    global _blob_singleton
    if _blob_singleton is None:
        _blob_singleton = BlobClientWrapper()
    return _blob_singleton
