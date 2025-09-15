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

## Testing

- Run tests:
  ```sh
  pytest
  ```
