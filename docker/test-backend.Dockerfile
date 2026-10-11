FROM python:3.12-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy \
    PYTHONPATH=/app/backend

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    postgresql-client \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install uv from official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Prepare backend dependencies
COPY backend/pyproject.toml backend/uv.lock* /app/backend/

WORKDIR /app/backend
RUN uv sync --extra dev --frozen 2>/dev/null || uv sync --extra dev

WORKDIR /app
CMD ["uv", "run", "pytest", "tests", "-q"]
