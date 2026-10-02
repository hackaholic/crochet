"""Database engine, session management, and dependencies."""

import os
from collections.abc import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.db.base import Base
from app.core.config import settings

# Default to SQLite for local development/testing without docker, or PostgreSQL in docker
DATABASE_URL = settings.database_url

# SQLAlchemy 2.0 with psycopg v3 accepts postgresql+psycopg:// or postgresql://
if DATABASE_URL.startswith("postgresql://") and "+psycopg" not in DATABASE_URL:
    # Use psycopg v3 driver if available
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg://", 1)

connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    echo=os.getenv("SQL_ECHO", "false").lower() == "true",
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def run_migrations() -> None:
    """Run Alembic migrations programmatically to head revision."""
    from alembic.config import Config
    from alembic import command

    backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    ini_path = os.path.join(backend_dir, "alembic.ini")
    if os.path.exists(ini_path):
        alembic_cfg = Config(ini_path)
        alembic_cfg.set_main_option("script_location", os.path.join(backend_dir, "alembic"))
        command.upgrade(alembic_cfg, "head")
    else:
        Base.metadata.create_all(bind=engine)


def init_db() -> None:
    """Initialize database schema via Alembic migrations, with fallback for custom test setups."""
    import app.models  # noqa: F401 - Ensure all models are registered in Base.metadata
    try:
        run_migrations()
    except Exception:
        # Safe fallback for in-memory databases or isolated test runners
        Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency for database sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
