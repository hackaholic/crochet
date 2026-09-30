"""Database engine, session management, and dependencies."""

import os
from collections.abc import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.db.base import Base

# Default to SQLite for local development/testing without docker, or PostgreSQL in docker
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./crochet.db")

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


def init_db() -> None:
    """Create database tables if they do not exist."""
    import app.models  # noqa: F401 - Ensure all models are registered in Base.metadata
    Base.metadata.create_all(bind=engine)

    # Lightweight auto-migration for newly added columns on existing databases
    with engine.connect() as conn:
        try:
            from sqlalchemy import text
            conn.execute(text("ALTER TABLE users ADD COLUMN role VARCHAR(20) DEFAULT 'CUSTOMER'"))
            conn.commit()
        except Exception:
            pass  # Column already exists or dialect specific


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency for database sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
