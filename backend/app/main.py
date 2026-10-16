import logging
import os
from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from sqlalchemy.orm import Session

from app.api.v1 import api_v1_router
from app.core.config import settings
from app.db.seed import seed_catalogue
from app.db.session import SessionLocal, get_db, init_db
from app.services.seo import SeoService

LOG_FORMAT = f"[sulocraft][env={settings.app_env}] [%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s"
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
logger = logging.getLogger("sulocraft.api")


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
    if settings.app_env.lower() == "production" and settings.email_provider.lower() == "resend":
        if not settings.resend_api_key or not settings.resend_api_key.strip():
            raise RuntimeError("Production EMAIL_PROVIDER=resend requires RESEND_API_KEY to be configured.")
        sender = settings.email_from_orders
        if "@sulocraft.com" not in sender.lower():
            raise RuntimeError(f"Production email sender '{sender}' must be on the @sulocraft.com domain.")

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
    from fastapi import HTTPException
    from fastapi.responses import FileResponse, RedirectResponse
    from app.core.images import LOCAL_IMAGE_ASSET_MAP, resolve_mock_image_source


    clean_path = image_path.lstrip("/")
    if ".." in Path(clean_path).parts or "\\" in clean_path or "\x00" in clean_path:
        raise HTTPException(status_code=404, detail="Image not found")
    def local_response(key: str):
        for root in (Path("public/images"), Path("../public/images"), Path("/app/public/images")):
            base = root.resolve()
            candidate = (base / key).resolve()
            if candidate.is_relative_to(base) and candidate.is_file():
                # Minimal container OS MIME databases may not know WebP.
                return FileResponse(candidate, media_type="image/webp" if candidate.suffix.lower() == ".webp" else None)
        return None

    response = local_response(clean_path)
    if response is not None:
        return response

    # DB/R2 keys may reference an approved checked-in artwork alias.
    local_asset = LOCAL_IMAGE_ASSET_MAP.get(clean_path)
    if local_asset:
        response = local_response(local_asset)
        if response is not None:
            return response

    upstream_url = resolve_mock_image_source(image_path)
    if upstream_url:
        return RedirectResponse(url=upstream_url, status_code=307)

    raise HTTPException(status_code=404, detail="Image not found")



@app.get("/sitemap.xml", tags=["seo"])
def root_sitemap(db: Session = Depends(get_db)) -> Response:
    """Root sitemap.xml endpoint for reverse proxies and web crawlers."""
    content = SeoService.generate_sitemap_xml(db)
    return Response(content=content, media_type="application/xml")


@app.get("/robots.txt", tags=["seo"])
def root_robots() -> Response:
    """Root robots.txt endpoint for reverse proxies and web crawlers."""
    content = SeoService.generate_robots_txt()
    return Response(content=content, media_type="text/plain")
