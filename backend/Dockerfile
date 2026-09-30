FROM python:3.12-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends curl postgresql-client && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml ./
RUN pip install --no-cache-dir \
    "fastapi>=0.115,<1.0" \
    "uvicorn[standard]>=0.34,<1.0" \
    "sqlalchemy>=2.0,<3.0" \
    "psycopg[binary]>=3.2,<4.0" \
    "pydantic>=2.0,<3.0" \
    "python-multipart>=0.0.12" \
    "pyyaml>=6.0" \
    "boto3>=1.34"

COPY app ./app

EXPOSE 8000

HEALTHCHECK --interval=10s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
