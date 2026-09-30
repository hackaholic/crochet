"""FastAPI entry point for Sulocraft."""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from app.api.v1 import api_v1_router
from app.core.config import settings
from app.db.seed import seed_catalogue
from app.db.session import SessionLocal, init_db


class CloudflareCacheControlMiddleware(BaseHTTPMiddleware):
    """Enforce private, non-cached headers for authenticated/sensitive dynamic customer endpoints."""

    PRIVATE_PREFIXES = (
        "/api/v1/auth",
        "/api/v1/cart",
        "/api/v1/orders",
        "/api/v1/addresses",
        "/api/v1/account",
        "/api/v1/admin",
        "/api/v1/payments",
    )

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        if any(request.url.path.startswith(prefix) for prefix in self.PRIVATE_PREFIXES):
            response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, private"
            response.headers["Pragma"] = "no-cache"
        return response


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager to initialize database schema and seed initial data."""
    init_db()
    with SessionLocal() as db:
        seed_catalogue(db)
    yield


app = FastAPI(
    title="Sulocraft API",
    version="0.2.0",
    description="Backend service for the Sulocraft direct-to-consumer crochet storefront.",
    lifespan=lifespan,
)

# Enforce strict non-caching for customer-sensitive endpoints behind Cloudflare
app.add_middleware(CloudflareCacheControlMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Mount API v1 routes
app.include_router(api_v1_router)


@app.get("/health", tags=["system"])
def health_check() -> dict[str, str]:
    """Report whether the API process is available."""
    return {"status": "ok", "service": "sulocraft-api"}
