# Agent Service

Minimal FastAPI service providing an `/invoke` endpoint backed by Azure OpenAI via LangChain (or a stub if not configured) and a `/version` endpoint. Incorporates a stubbed Azure Cognitive Search enrichment (first result snippet appended when configured).

## Endpoints

- `GET /version` - returns service name and version
- `POST /invoke` - JSON body `{ "prompt": "..." }` returns `{ "output": "...", "model": "<deployment>", "stub": true|false }`
- `GET /healthz` - basic health probe

## Environment Variables (.env)

See `.env.example`.

Required for real model invocation:

- `AZURE_OPENAI_API_KEY`
- `AZURE_OPENAI_ENDPOINT` (e.g. <https://my-openai-resource.openai.azure.com>)
- `AZURE_OPENAI_DEPLOYMENT` (chat/completions deployment name)
- `AZURE_OPENAI_API_VERSION` (default 2024-02-01)

If any are missing, responses are stubbed.

Optional Azure Cognitive Search (stubbed if incomplete):

- `AZURE_SEARCH_ENDPOINT` (e.g. https://<your-search>.search.windows.net)
- `AZURE_SEARCH_API_KEY`
- `AZURE_SEARCH_INDEX`

## Local Run (Python)

```bash
cd apps/agent
pip install --upgrade pip poetry
poetry install --no-root
cp .env.example .env  # fill in values
poetry run uvicorn main:app --reload --port 8001
```

## Docker

```bash
cd apps
cp agent/.env.example agent/.env  # fill in values
docker compose up --build agent
```

Then call:

```bash
curl -s http://localhost:8001/version | jq
curl -s -X POST http://localhost:8001/invoke -H 'Content-Type: application/json' -d '{"prompt":"Hello"}' | jq

```

## Project Layout

```
config.py
main.py
models/
  invoke.py
routes/
  invoke.py
services/
  search_service.py
  chain_service.py
```

## Next Steps

- Add validation/testing
- Integrate with criteria API data
- Implement conversation history
- Add auth & telemetry
