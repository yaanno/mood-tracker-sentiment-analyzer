# syntax=docker/dockerfile:1

ARG PYTHON_VERSION=3.9
FROM python:${PYTHON_VERSION}-slim AS base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    PROJECT_DIR="/code"

ENV PATH="$POETRY_HOME/bin:$PROJECT_DIR/.venv/bin:$PATH"

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    build-essential

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 - && chmod a+x /opt/poetry/bin/poetry
RUN poetry self add poetry-plugin-export

# Set the working directory
WORKDIR $PROJECT_DIR

# Create cache for transformers
RUN mkdir -p $PROJECT_DIR/.cache && chmod 777 $PROJECT_DIR/.cache

# Copy the dependency files first
COPY poetry.lock pyproject.toml ./

# Install dependencies
RUN poetry install --no-root

# Remove build dependencies
RUN apt-get remove --purge -y build-essential

# Copy the application code
COPY sentiment_analyser ./sentiment_analyser

# Expose the port
EXPOSE 8000

# Create a non-root user
ARG UID=10001
RUN useradd -r -u ${UID} -s /bin/bash appuser

USER appuser

# Run the application
CMD ["poetry", "run", "uvicorn", "sentiment_analyser.main:app", "--host", "0.0.0.0", "--port", "8000"]
