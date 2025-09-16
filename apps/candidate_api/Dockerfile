FROM python:3.10-slim

# Use a workspace root that preserves repo structure for path dependency ../shared_utils
WORKDIR /workspace

RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/* \
    && pip install poetry

# Copy only dependency manifests first for better Docker layer caching
COPY apps/shared_utils/pyproject.toml apps/shared_utils/ /workspace/apps/shared_utils/
COPY apps/candidate_api/pyproject.toml apps/candidate_api/poetry.lock* /workspace/apps/candidate_api/

# Install dependencies (shared_utils path dependency is now present via preserved relative path)
WORKDIR /workspace/apps/candidate_api
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root

# Copy the full source (overwrites manifests if changed)
COPY apps/shared_utils /workspace/apps/shared_utils
COPY apps/candidate_api /workspace/apps/candidate_api

EXPOSE 8002
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8002"]
