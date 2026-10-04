#!/usr/bin/env python3
"""Fail closed when an API database URL does not match its mounted DB secrets."""

from __future__ import annotations

import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit


def validate(database_file: Path, user_file: Path, password_file: Path, url_file: Path) -> bool:
    try:
        database = database_file.read_text(encoding="utf-8").strip()
        username = user_file.read_text(encoding="utf-8").strip()
        password = password_file.read_text(encoding="utf-8").strip()
        parsed = urlsplit(url_file.read_text(encoding="utf-8").strip())
        return (
            bool(database and username and password)
            and parsed.scheme in {"postgres", "postgresql", "postgresql+psycopg"}
            and parsed.hostname == "postgres"
            and parsed.port in {None, 5432}
            and unquote(parsed.path.lstrip("/")) == database
            and unquote(parsed.username or "") == username
            and unquote(parsed.password or "") == password
        )
    except (OSError, UnicodeError, ValueError):
        return False


def main(argv: list[str]) -> int:
    if len(argv) != 5:
        print("Usage: validate_database_target.py DB_FILE USER_FILE PASSWORD_FILE URL_FILE", file=sys.stderr)
        return 2
    if not validate(*(Path(value) for value in argv[1:])):
        print("Database secret groups do not target the same PostgreSQL database.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
