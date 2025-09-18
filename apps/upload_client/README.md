# Upload Client

Lightweight Python client for the Generic Upload Function.

## Install (poetry)
```
cd apps/upload_client
poetry install
```

Or add to another project:
```
poetry add ../apps/upload_client
```

## Usage
```python
from upload_client import UploadClient

client = UploadClient(endpoint="http://localhost:7071", secret="raw-shared-secret")
with open("sample.pdf", "rb") as f:
    result = client.upload("candidate", "123", f, "sample.pdf")
print(result.blob_path, result.sha256)
```

If the server is running with bypass (`DISABLE_INTERNAL_UPLOAD_AUTH=true`), omit the secret.

## Environment Variables
| Name | Purpose | Default |
| ---- | ------- | ------- |
| UPLOAD_ENDPOINT | Base URL of upload function | (required) |
| UPLOAD_SECRET | Raw shared secret (optional if bypass) | *(none)* |
| UPLOAD_TIMEOUT_S | Timeout seconds | 30 |

## Error Mapping
| Exception | Condition |
| --------- | -------- |
| AuthError | 401 unauthorized |
| ValidationError | 400 responses |
| ServerError | >=500 responses |
| UploadError | Network issues, unexpected statuses, JSON errors |

## Future Enhancements
- Streaming multipart without loading full file (current acceptable up to 10MB)
- Async variant using httpx.AsyncClient
- Automatic retry on transient 5xx
