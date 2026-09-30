FROM python:3.12-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY backend/pyproject.toml ./
RUN pip install --no-cache-dir fastapi "uvicorn[standard]" "sqlalchemy>=2.0" "psycopg[binary]>=3.2" "pydantic>=2.0"

COPY backend/app ./app
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
