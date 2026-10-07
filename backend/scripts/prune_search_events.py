#!/usr/bin/env python3
"""CLI utility to prune expired search events based on retention policy."""

import argparse
import logging
import os
import sys

# Ensure backend root is on PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.db.session import SessionLocal
from app.services.search import DEFAULT_RETENTION_DAYS, prune_expired_search_events

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] [%(levelname)s]: %(message)s")
logger = logging.getLogger("prune_search_events")


def main() -> int:
    parser = argparse.ArgumentParser(description="Prune expired search telemetry events.")
    parser.add_argument(
        "--days",
        type=int,
        default=DEFAULT_RETENTION_DAYS,
        help=f"Retention period in days (default: {DEFAULT_RETENTION_DAYS})",
    )
    args = parser.parse_args()

    if args.days < 1:
        logger.error("Retention days must be at least 1.")
        return 1

    logger.info("Starting search event retention prune (retention_days=%d)...", args.days)
    with SessionLocal() as db:
        try:
            count = prune_expired_search_events(db, retention_days=args.days)
            logger.info("Successfully pruned %d expired search event(s).", count)
            return 0
        except Exception as exc:
            logger.error("Failed to prune search events: %s", exc)
            return 1


if __name__ == "__main__":
    sys.exit(main())
