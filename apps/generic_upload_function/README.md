# Generic Upload Function (GUF)

HTTP Azure Function for internal services to upload small (<=10MB) binary files into a single blob container using managed identity.

## Key Behavior
- Auth: single shared secret (caller holds raw; function stores SHA256) via `X-Internal-Upload-Key` header.
- Request: `POST /api/upload` with `multipart/form-data` containing field `file` and fields: `contextType`, `contextId`.
- Constraints: file <= `MAX_BYTES` (default 10MB), `contextType` must be in `ALLOWED_CONTEXT_TYPES`.
- Blob path: `<contextType>/<contextId>/<uuid>_<sanitized-filename>`
- Response JSON: `{ "blobPath": str, "sha256": str, "size": int }`

## Environment / Settings
| Name | Purpose | Example |
| ---- | ------- | ------- |
| STORAGE_ACCOUNT_URL | Blob service URL | `https://acct.blob.core.windows.net` |
| BLOB_CONTAINER | Target container (must exist) | `uploads` |
| MAX_BYTES | Max upload size in bytes | `10485760` |
| INTERNAL_UPLOAD_KEY_SHA256 | Hex SHA256 of shared secret | *(64 hex chars)* |
| DISABLE_INTERNAL_UPLOAD_AUTH | (Demo only) if `true`, bypass shared-secret auth (WARNING: do not use in prod) | `false` |
| ALLOWED_CONTEXT_TYPES | Comma list allowed context types | `candidate,decision-kit` |
| LOG_LEVEL | Logging level | `INFO` |

## Local Dev
1. Copy `local.settings.json.example` to `local.settings.json` and adjust.
2. Use Azurite (already referenced by `UseDevelopmentStorage=true`). Ensure container exists.
3. Start function host:
   `func start`

### Run in Docker (local)

Build image:
```
docker build -t guf:local .
```

Run with environment variables (example uses Azurite via host network or separate container):
```
docker run --rm -p 7071:80 \
  -e STORAGE_ACCOUNT_URL="http://host.docker.internal:10000/devstoreaccount1" \
  -e BLOB_CONTAINER="uploads" \
  -e MAX_BYTES=10485760 \
  -e INTERNAL_UPLOAD_KEY_SHA256=<hex> \
  -e ALLOWED_CONTEXT_TYPES="candidate,decision-kit" \
  -e LOG_LEVEL=INFO \
  guf:local
```

If using an actual Azure Storage account instead of Azurite, set `STORAGE_ACCOUNT_URL` accordingly and authenticate via managed identity (in Azure) or `az login` + `AzureWebJobsStorage` connection string locally.

### Optional docker-compose snippet
```
version: '3.8'
services:
  azurite:
    image: mcr.microsoft.com/azure-storage/azurite
    command: azurite --blobHost 0.0.0.0
    ports:
      - "10000:10000"
  guf:
    build: .
    environment:
      STORAGE_ACCOUNT_URL: http://azurite:10000/devstoreaccount1
      BLOB_CONTAINER: uploads
      MAX_BYTES: 10485760
      INTERNAL_UPLOAD_KEY_SHA256: <hex>
      ALLOWED_CONTEXT_TYPES: candidate,decision-kit
      LOG_LEVEL: INFO
    ports:
      - "7071:80"
    depends_on:
      - azurite
```

## Sample cURL
```
SECRET=raw-shared-secret
FILE=./sample.pdf
curl -X POST \
  -H "X-Internal-Upload-Key: $SECRET" \
  -F "contextType=candidate" \
  -F "contextId=123" \
  -F "file=@${FILE}" \
  http://localhost:7071/api/upload
```

## Non-Goals (Initial)
- Public/browser direct uploads
- Malware scanning
- Deduplication
- Metadata DB writes (only blob path returned)

## Future Enhancements
- Add optional metadata JSON field
- Integrate scanning service
- SAS + pre-signed upload evolution

---
Implementation status: core upload implemented, auth bypass flag available (set `DISABLE_INTERNAL_UPLOAD_AUTH=true` only for local demos/testing), streaming hash + size enforcement complete, IaC & containerization tracked separately.

### Auth Bypass (Demo Mode)
Set `DISABLE_INTERNAL_UPLOAD_AUTH=true` to allow requests without the `X-Internal-Upload-Key` header. The function logs a prominent warning on startup and per-request bypass usage. This is intended strictly for local demos or ephemeral test environments. In any shared or production environment KEEP THIS FLAG UNSET and provide the hashed secret.

Example (local unsafe demo):
```
DISABLE_INTERNAL_UPLOAD_AUTH=true func start
```

Or Docker:
```
docker run --rm -p 7071:80 \
  -e STORAGE_ACCOUNT_URL="http://host.docker.internal:10000/devstoreaccount1" \
  -e BLOB_CONTAINER="uploads" \
  -e MAX_BYTES=10485760 \
  -e ALLOWED_CONTEXT_TYPES="candidate,decision-kit" \
  -e DISABLE_INTERNAL_UPLOAD_AUTH=true \
  guf:local
```

Security note: when bypass is enabled, anyone who can reach the endpoint can upload arbitrary files within other configured constraints.
