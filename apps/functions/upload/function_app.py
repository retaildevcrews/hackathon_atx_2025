import azure.functions as func
import json
import uuid
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobClient

from ..core.config import load_settings
from ..core.secret import verify_shared_secret, HEADER_NAME
from ..core.sanitizer import sanitize_filename
from ..core.errors import AuthError, ValidationError, SizeLimitError, StorageError
from ..core.logging_utils import get_logger
from ..core.streaming import iter_file_chunks

settings = load_settings()
logger = get_logger(settings.log_level)
if settings.disable_internal_upload_auth:
    logger.warning("auth.bypass.mode ENABLED - not suitable for production")
credential = DefaultAzureCredential()


def main(req: func.HttpRequest) -> func.HttpResponse:  # type: ignore
    try:
        verify_shared_secret(
            req.headers.get(HEADER_NAME),
            settings.internal_upload_key_sha256,
            bypass=settings.disable_internal_upload_auth,
        )

        content_type = req.headers.get("Content-Type", "")
        if "multipart/form-data" not in content_type:
            raise ValidationError("expected multipart/form-data")

        body = req.get_body()
        boundary_token = None
        for part in content_type.split(';'):
            part = part.strip()
            if part.startswith('boundary='):
                boundary_token = part.split('=',1)[1]
        if not boundary_token:
            raise ValidationError("missing boundary")
        boundary = ("--" + boundary_token).encode()

        parts = body.split(boundary)
        file_content = None
        filename = None
        context_type = None
        context_id = None

        for p in parts:
            if not p or p == b'--\r\n' or p == b'--':
                continue
            header_body_split = p.split(b"\r\n\r\n", 1)
            if len(header_body_split) != 2:
                continue
            headers_blob, data_blob = header_body_split
            data_blob = data_blob.rstrip(b"\r\n")
            headers_text_lower = headers_blob.lower()
            if b"content-disposition" in headers_text_lower:
                if b"name=\"file\"" in headers_text_lower:
                    disposition = headers_blob.decode(errors='ignore')
                    for token in disposition.split(';'):
                        token = token.strip()
                        if token.startswith('filename='):
                            raw_fn = token.split('=',1)[1].strip().strip('"')
                            filename = sanitize_filename(raw_fn)
                    file_content = data_blob
                elif b"name=\"contexttype\"" in headers_text_lower:
                    context_type = data_blob.decode(errors='ignore').strip()
                elif b"name=\"contextid\"" in headers_text_lower:
                    context_id = data_blob.decode(errors='ignore').strip()

        if not file_content or filename is None:
            raise ValidationError("missing file field")
        if not context_type or context_type not in settings.allowed_context_types:
            raise ValidationError("invalid contextType")
        if not context_id:
            raise ValidationError("missing contextId")

        size = len(file_content)
        if size > settings.max_bytes:
            raise SizeLimitError(f"file exceeds limit {settings.max_bytes}")

        file_id = str(uuid.uuid4())
        blob_path = f"{context_type}/{context_id}/{file_id}_{filename}"

        from io import BytesIO
        bio = BytesIO(file_content)
        chunks_iter, total, digest = iter_file_chunks(bio, settings.max_bytes)

        if total > settings.max_bytes:
            raise SizeLimitError("file exceeds limit during streaming")

        blob_client = BlobClient(account_url=settings.storage_account_url,
                                 container_name=settings.blob_container,
                                 blob_name=blob_path,
                                 credential=credential)
        try:
            blob_client.upload_blob(data=chunks_iter, overwrite=False)
        except Exception as ex:  # noqa
            logger.error("storage upload failed", extra={"error": str(ex)})
            raise StorageError("upload failed")

        logger.info("upload.success", extra={"path": blob_path, "size": size})
        return func.HttpResponse(
            body=json.dumps({"blobPath": blob_path, "sha256": digest, "size": size}),
            status_code=200,
            mimetype="application/json"
        )

    except AuthError as e:
        return func.HttpResponse(json.dumps({"error": str(e)}), status_code=401, mimetype="application/json")
    except ValidationError as e:
        return func.HttpResponse(json.dumps({"error": str(e)}), status_code=400, mimetype="application/json")
    except SizeLimitError as e:
        return func.HttpResponse(json.dumps({"error": str(e)}), status_code=413, mimetype="application/json")
    except StorageError as e:
        return func.HttpResponse(json.dumps({"error": str(e)}), status_code=502, mimetype="application/json")
    except Exception as e:  # noqa
        logger.error("upload.unhandled", extra={"error": str(e)})
        return func.HttpResponse(json.dumps({"error": "internal error"}), status_code=500, mimetype="application/json")
