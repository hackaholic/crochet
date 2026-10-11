FROM python:3.12-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy \
    PYTHONPATH=/app/backend

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    nodejs \
    npm \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install uv from official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Install pnpm and security tools
RUN npm install -g pnpm && \
    pip install --no-cache-dir pip-audit semgrep

# Prepare backend dependencies
COPY backend/pyproject.toml backend/uv.lock* /app/backend/
WORKDIR /app/backend
RUN uv sync --extra dev --frozen 2>/dev/null || uv sync --extra dev

WORKDIR /app
CMD ["./scripts/security/scan-sast.sh"]
