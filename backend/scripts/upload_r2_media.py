#!/usr/bin/env python3
"""Synchronize Sulocraft-managed images to Cloudflare R2.

Dry-run is the default. Pass --apply to upload changed or missing objects.
"""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
import mimetypes
import os
from pathlib import Path
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import boto3
from botocore.exceptions import ClientError


def required(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise SystemExit(f"Missing required environment variable: {name}")
    return value


def public_url(base: str, key: str) -> str:
    return f"{base.rstrip('/')}/{key}"


def verify_public_url(url: str) -> str | None:
    """Return an error string after retries, or None when browser delivery works."""
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/140.0 Safari/537.36"
    }
    last_error: str | None = None
    for attempt in range(1, 6):
        try:
            with urlopen(Request(url, method="HEAD", headers=headers), timeout=15) as response:
                if response.status == 200:
                    return None
                last_error = f"{response.status} {url}"
        except (HTTPError, URLError) as error:
            last_error = f"{error} {url}"
        if attempt < 5:
            time.sleep(2)
    return last_error


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", default="public/images", help="Local image root")
    parser.add_argument("--prefix", default="", help="Optional R2 object-key prefix")
    parser.add_argument("--apply", action="store_true", help="Perform uploads; otherwise dry-run")
    parser.add_argument("--verify-public", action="store_true", help="Require uploaded public URLs to return HTTP 200")
    args = parser.parse_args()

    endpoint = required("R2_ENDPOINT")
    access_key = required("R2_ACCESS_KEY_ID")
    secret_key = required("R2_SECRET_ACCESS_KEY")
    bucket = os.getenv("R2_PUBLIC_BUCKET", "sulocraft-products").strip()
    base_url = os.getenv("R2_PUBLIC_BASE_URL", "https://images.sulocraft.com").strip()
    source = Path(args.source).resolve()
    if not source.is_dir():
        raise SystemExit(f"Image source directory does not exist: {source}")

    s3 = boto3.client(
        "s3",
        endpoint_url=endpoint,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name="auto",
    )

    files = sorted(path for path in source.rglob("*") if path.is_file())
    objects: list[tuple[Path, str, str]] = []
    changed: list[tuple[Path, str, str]] = []
    unchanged = 0
    for path in files:
        relative = path.relative_to(source).as_posix()
        key = "/".join(part for part in (args.prefix.strip("/"), relative) if part)
        content_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        objects.append((path, key, content_type))
        try:
            remote = s3.head_object(Bucket=bucket, Key=key)
            if remote.get("ContentLength") == path.stat().st_size:
                unchanged += 1
                continue
        except ClientError as error:
            code = str(error.response.get("Error", {}).get("Code", ""))
            if code not in {"404", "NoSuchKey", "NotFound"}:
                raise
        changed.append((path, key, content_type))

    action = "UPLOAD" if args.apply else "WOULD UPLOAD"
    for path, key, content_type in changed:
        print(f"{action}: {path} -> r2://{bucket}/{key}")
        if args.apply:
            s3.upload_file(
                str(path),
                bucket,
                key,
                ExtraArgs={"ContentType": content_type, "CacheControl": "public, max-age=31536000, immutable"},
            )

    if args.apply and args.verify_public:
        urls = [public_url(base_url, key) for _, key, _ in objects]
        with ThreadPoolExecutor(max_workers=8) as pool:
            failures = [error for error in pool.map(verify_public_url, urls) if error]
        if failures:
            print("Public verification failed:", file=sys.stderr)
            print("\n".join(failures), file=sys.stderr)
            return 2

    print(f"Scanned {len(files)} files: {len(changed)} changed, {unchanged} unchanged. apply={args.apply}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
