# # syntax=docker/dockerfile:1

ARG PYTHON_VERSION=3.13.0
FROM python:3.11-slim AS base

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
RUN <<EOF
apt-get update
apt-get install --no-install-recommends -y curl build-essential
rm -rf /var/lib/apt/lists/*
EOF

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 - && chmod a+x /opt/poetry/bin/poetry
RUN poetry self add poetry-plugin-export


# Set the working directory
WORKDIR $PROJECT_DIR

# Create cache for transformers
RUN mkdir -p $PROJECT_DIR/.cache
RUN chmod 777 $PROJECT_DIR/.cache

# Copy the dependency files
COPY poetry.lock pyproject.toml ./

# Install dependencies
RUN poetry install --no-root

RUN pip3 install torch --index-url https://download.pytorch.org/whl/cpu

# Copy the application code
COPY sentiment_analyser ./sentiment_analyser


# Expose the port
EXPOSE 8000

ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/nonexistent" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    appuser

USER appuser

# Run the application
CMD ["poetry", "run", "uvicorn", "sentiment_analyser.main:app", "--host", "0.0.0.0", "--port", "8000"]
