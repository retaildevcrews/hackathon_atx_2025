# Criteria API (Python/FastAPI)

A RESTful API for managing criteria (name, description, definition) using Azure CosmosDB.

## Setup

1. Copy `.env.example` to `.env` and fill in your CosmosDB credentials.
2. Install dependencies:
   ```sh
   poetry install
   ```
3. Start the server:
   ```sh
   poetry run uvicorn app.main:app --reload
   ```

## Endpoints

- `GET /criteria` — List all criteria
- `GET /criteria/{id}` — Get a single criterion
- `POST /criteria` — Create a new criterion
- `PUT /criteria/{id}` — Update a criterion
- `DELETE /criteria/{id}` — Delete a criterion

### Rubrics

Rubrics group ordered criteria with optional weights. Composition is stored in the `rubric_criteria` association table.

Key rubric endpoints:

- `GET /rubrics` — List rubrics (criteria returned in defined order)
- `GET /rubrics/{id}` — Retrieve rubric
- `POST /rubrics` — Create draft rubric
- `PUT /rubrics/{id}` — Update draft rubric (reorders/changes replace entire composition)
- `POST /rubrics/{id}/publish` — Publish a rubric (becomes immutable)
- `DELETE /rubrics/{id}` — Delete a draft rubric (cascades association rows)

Positions are reassigned on each update (PUT) based on the order supplied.

## Testing

- Run tests:
  ```sh
  pytest
  ```
