FROM python:3.12-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY backend/pyproject.toml ./
RUN pip install --no-cache-dir fastapi "uvicorn[standard]" "sqlalchemy>=2.0" "psycopg[binary]>=3.2" "pydantic>=2.0" "python-multipart>=0.0.12" "pyyaml>=6.0" "boto3>=1.34" "alembic>=1.13,<2.0" "httpx>=0.28,<1.0"

COPY backend/alembic.ini ./
COPY backend/alembic ./alembic
COPY backend/app ./app
EXPOSE 8000
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
