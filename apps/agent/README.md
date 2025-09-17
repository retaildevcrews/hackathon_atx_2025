# Agent Service

Minimal FastAPI service providing:

- `/invoke` endpoint backed by Azure OpenAI via LangChain (or a stub if not configured)
- `/evaluate_rubric` endpoint performing rubric-based PDF evaluation (one LLM call per criterion)
- `/version` endpoint
- `/healthz` endpoint

It also includes a stubbed Azure Cognitive Search enrichment (first result snippet appended when configured).

## Endpoints

- `GET /version` - returns service name and version
- `POST /invoke` - JSON body `{ "prompt": "..." }` returns `{ "output": "...", "model": "<deployment>", "stub": true|false }`
- `POST /evaluate_rubric` - JSON body:

  ```json
  {
    "document_url": null,
    "rubric_name": "tv_rubric",
    "model_params": {"temperature": 0},
    "max_concurrency": 5
  }
  ```

  Example truncated response:

  ```json
  {
    "rubric_id": "tv_rubric",
    "rubric_name": "tv_rubric",
    "criteria": [
      {
        "criterion_id": "picture-quality",
        "criterion_name": "Picture Quality",
        "criterion_description": "Measures resolution, contrast, color accuracy, and HDR support.",
        "criterion_definition": {"Excellent (5)": "OLED/QLED, 4K/8K, HDR10+, Dolby Vision"},
        "weight": "20%",
        "score": 5,
        "reasoning": "...",
        "evidence": "\"OLED panel with HDR10+ support\"",
        "document_chunk": null
      }
    ],
    "model_params": {"temperature": 0},
    "system_prompt_template": "You are an expert document evaluator..."
  }
  ```json
- `GET /healthz` - basic health probe

## Environment Variables (.env)

See `.env.example`.

Required for real model invocation:

- `AZURE_OPENAI_API_KEY`
- `AZURE_OPENAI_ENDPOINT` (e.g. <https://my-openai-resource.openai.azure.com>)
- `AZURE_OPENAI_DEPLOYMENT` (chat/completions deployment name)
- `AZURE_OPENAI_API_VERSION` (default 2024-02-01)

If any are missing, `/invoke` responses are stubbed. The `/evaluate_rubric` endpoint will return 500 (LLM required) per design.

Note: `/evaluate_rubric` bypasses LangChain and uses the Azure OpenAI client directly, sending the PDF as a base64-encoded `input_file` content block alongside textual instructions.

Optional Azure Cognitive Search (stubbed if incomplete):

- `AZURE_SEARCH_ENDPOINT` (e.g. <https://your-search-name.search.windows.net>)
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

```text
config.py
main.py
models/
  invoke.py
  evaluate.py
routes/
  invoke.py
services/
  search_service.py
  chain_service.py
  evaluation_service.py
```

## Code Quality / Linting

### Ruff (fast style/lint)

```bash
poetry run ruff check .
```

### Black (format)

```bash
poetry run black .
```

### Pylint (deeper static analysis)

Configuration: `.pylintrc` in this directory.

Run on all modules:

```bash
poetry run pylint agent
```

Or target specific files:

```bash
poetry run pylint main.py services/*.py routes/*.py
```

Return code non‑zero indicates issues. Current config intentionally suppresses some warnings (docstrings, broad exceptions) during early scaffolding.

## Next Steps

- Add validation/testing
- Integrate with criteria API data
- Implement conversation history
- Add auth & telemetry
