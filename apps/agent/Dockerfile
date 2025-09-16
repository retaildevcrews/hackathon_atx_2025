# syntax=docker/dockerfile:1
FROM python:3.10-slim AS base

WORKDIR /app

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

ENV POETRY_VERSION=1.8.3

# Install Poetry
RUN pip install --no-cache-dir "poetry==$POETRY_VERSION"

# Copy pyproject
COPY pyproject.toml ./

# Configure poetry not to create virtualenvs
RUN poetry config virtualenvs.create false \
    && poetry install --no-root --no-interaction --no-ansi

# Copy source
COPY . ./

EXPOSE 8001

ENV PYTHONUNBUFFERED=1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
