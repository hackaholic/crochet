#!/usr/bin/env python3
"""Compatibility wrapper pointing to scripts/decrypt_secrets.py with --env preprod."""

import sys
from pathlib import Path

# Add scripts directory to sys.path and invoke decrypt_secrets
sys.path.insert(0, str(Path(__file__).resolve().parent))
from decrypt_secrets import main

if __name__ == "__main__":
    # If --env was not explicitly passed, default to preprod
    args = sys.argv[1:]
    if "--env" not in args:
        args = ["--env", "preprod"] + args
    raise SystemExit(main(args))
