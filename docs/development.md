# Development environment

## Containers

Docker Compose defines the complete local stack in `docker/compose.yaml`.

| Service | Purpose | Address |
| --- | --- | --- |
| `frontend` | React and Vite storefront | `http://localhost:8080` |
| `api` | Python FastAPI backend | `http://localhost:8000` |
| `db` | PostgreSQL persistent data store | `localhost:5432` |

Start a fresh environment with:

```bash
docker-compose -f docker/compose.yaml up --build
```

Stop it with:

```bash
docker-compose -f docker/compose.yaml down
```

To stop it and remove the local database volume:

```bash
docker-compose -f docker/compose.yaml down --volumes
```

The API currently provides `GET /health`. FastAPI also creates live endpoint documentation at `/docs`. The database is included now so the catalogue and order modules can be built without reshaping the local environment later.

## Backend growth path

Build the backend by adding an API domain at a time:

1. Define its request and response schemas.
2. Add route handlers under `backend/app/`.
3. Add database access and migrations.
4. Add container-based tests.
5. Replace the matching frontend sample-data usage with API calls.

Do not put secrets in `docker/compose.yaml`. Use an ignored environment file when real payment, email, or production database credentials are introduced.
