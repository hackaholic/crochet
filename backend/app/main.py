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


class CSRFOriginProtectionMiddleware(BaseHTTPMiddleware):
    """Enforce CSRF protection on state-changing requests using cookie authentication."""

    MUTATING_METHODS = {"POST", "PUT", "PATCH", "DELETE"}

    async def dispatch(self, request: Request, call_next):
        if request.method in self.MUTATING_METHODS:
            session_cookie = request.cookies.get("session_token")
            if session_cookie:
                origin = request.headers.get("origin")
                referer = request.headers.get("referer")
                source = origin
                if not source and referer:
                    from urllib.parse import urlparse
                    parsed = urlparse(referer)
                    source = f"{parsed.scheme}://{parsed.netloc}"

                is_test_or_dev = (
                    settings.app_env == "development"
                    or os.getenv("TESTING", "false").lower() == "true"
                )

                if source:
                    is_valid = (
                        source in settings.cors_origins
                        or (is_test_or_dev and any(h in source for h in ("localhost", "127.0.0.1", "testserver")))
                    )
                    if not is_valid:
                        return Response(
                            content='{"detail":"CSRF origin validation failed"}',
                            status_code=403,
                            media_type="application/json",
                        )
                elif not is_test_or_dev:
                    return Response(
                        content='{"detail":"Origin or Referer header required for state-changing request"}',
                        status_code=403,
                        media_type="application/json",
                    )

        return await call_next(request)


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
app.add_middleware(CSRFOriginProtectionMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Mount API v1 routes
app.include_router(api_v1_router)


@app.get("/", tags=["system"])
def root() -> dict[str, str]:
    """Root entrypoint providing service status and quick links."""
    return {
        "status": "online",
        "service": "Sulocraft API",
        "version": app.version,
        "docs": "/docs",
        "health": "/health",
        "storefront": "/api/v1/storefront/home",
    }


@app.get("/health", tags=["system"])
def health_check() -> dict[str, str]:
    """Report whether the API process is available."""
    return {"status": "ok", "service": "sulocraft-api"}


@app.api_route("/static/images/{image_path:path}", methods=["GET", "HEAD"], tags=["system"])
def get_mock_static_image(image_path: str):
    """Serve local static assets or redirect to high-res photography during development."""
    from pathlib import Path
    from fastapi.responses import FileResponse, RedirectResponse
    from app.core.images import resolve_mock_image_source

    clean_path = image_path.lstrip("/")
    # Check if file exists locally on disk in public/images/
    candidates = [
        Path(f"public/images/{clean_path}"),
        Path(f"../public/images/{clean_path}"),
        Path(f"/app/public/images/{clean_path}"),
    ]
    for candidate in candidates:
        if candidate.is_file():
            return FileResponse(candidate)

    upstream_url = resolve_mock_image_source(image_path)
    return RedirectResponse(url=upstream_url, status_code=307)

