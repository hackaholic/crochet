"""Media inspection and metadata resolution service conforming to Task 5.20."""

from __future__ import annotations

import hashlib
import json
import mimetypes
import os
from pathlib import Path
import struct
from urllib.parse import urlparse

from app.core.config import settings
from app.core.images import LOCAL_IMAGE_ASSET_MAP, build_image_url
from app.schemas.media import MediaMetadataOut, MediaVariantOut


# Candidate filesystem roots where public images reside across local dev, testing, and Docker
IMAGE_ROOT_CANDIDATES: list[Path] = [
    Path("public/images"),
    Path("../public/images"),
    Path("/app/public/images"),
    Path(__file__).resolve().parent.parent.parent.parent / "public" / "images",
]

# Candidate filesystem paths where the responsive media manifest resides
MANIFEST_PATH_CANDIDATES: list[Path] = [
    Path("public/images/optimized/manifest.json"),
    Path("../public/images/optimized/manifest.json"),
    Path("/app/public/images/optimized/manifest.json"),
    Path(__file__).resolve().parent.parent.parent.parent / "public" / "images" / "optimized" / "manifest.json",
]


def _parse_png_dimensions(data: bytes) -> tuple[int | None, int | None]:
    if len(data) >= 24 and data.startswith(b"\x89PNG\r\n\x1a\n"):
        w, h = struct.unpack(">II", data[16:24])
        return w, h
    return None, None


def _parse_jpeg_dimensions(data: bytes) -> tuple[int | None, int | None]:
    if len(data) < 2 or not data.startswith(b"\xff\xd8"):
        return None, None
    idx = 2
    size = len(data)
    sof_markers = {
        0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7,
        0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF,
    }
    while idx + 4 <= size:
        if data[idx] != 0xFF:
            idx += 1
            continue
        marker = data[idx + 1]
        if marker in (0xD8, 0xD9):
            idx += 2
            continue
        if idx + 4 > size:
            break
        length = struct.unpack(">H", data[idx + 2 : idx + 4])[0]
        if marker in sof_markers and idx + 9 <= size:
            h, w = struct.unpack(">HH", data[idx + 5 : idx + 9])
            return w, h
        idx += 2 + length
    return None, None


def _parse_webp_dimensions(data: bytes) -> tuple[int | None, int | None]:
    if len(data) >= 30 and data.startswith(b"RIFF") and data[8:12] == b"WEBP":
        chunk_type = data[12:16]
        if chunk_type == b"VP8 " and len(data) >= 30:
            # Lossy VP8
            if data[23:26] == b"\x9d\x01\x2a":
                w = struct.unpack("<H", data[26:28])[0] & 0x3FFF
                h = struct.unpack("<H", data[28:30])[0] & 0x3FFF
                return w, h
        elif chunk_type == b"VP8L" and len(data) >= 25:
            # Lossless VP8L
            if data[20] == 0x2F:
                b1, b2, b3, b4 = data[21], data[22], data[23], data[24]
                w = 1 + (((b2 & 0x3F) << 8) | b1)
                h = 1 + (((b4 & 0x0F) << 10) | (b3 << 2) | ((b2 & 0xC0) >> 6))
                return w, h
        elif chunk_type == b"VP8X" and len(data) >= 30:
            # Extended VP8X
            w = 1 + (data[24] | (data[25] << 8) | (data[26] << 16))
            h = 1 + (data[27] | (data[28] << 8) | (data[29] << 16))
            return w, h
    return None, None


def _parse_gif_dimensions(data: bytes) -> tuple[int | None, int | None]:
    if len(data) >= 10 and (data.startswith(b"GIF87a") or data.startswith(b"GIF89a")):
        w, h = struct.unpack("<HH", data[6:10])
        return w, h
    return None, None


def inspect_image_bytes(data: bytes) -> tuple[int | None, int | None, str | None]:
    """Inspect raw binary bytes for image dimensions and MIME type without external dependencies."""
    if not data:
        return None, None, None

    # PNG
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        w, h = _parse_png_dimensions(data)
        return w, h, "image/png"

    # JPEG
    if data.startswith(b"\xff\xd8"):
        w, h = _parse_jpeg_dimensions(data)
        return w, h, "image/jpeg"

    # WebP
    if data.startswith(b"RIFF") and len(data) >= 12 and data[8:12] == b"WEBP":
        w, h = _parse_webp_dimensions(data)
        return w, h, "image/webp"

    # GIF
    if data.startswith(b"GIF87a") or data.startswith(b"GIF89a"):
        w, h = _parse_gif_dimensions(data)
        return w, h, "image/gif"

    return None, None, None


def _resolve_local_image_path(clean_path: str) -> Path | None:
    """Safely find a local file path for an image key, preventing directory traversal."""
    # Strict path traversal check
    if ".." in clean_path or clean_path.startswith("/") or "\\" in clean_path or "\0" in clean_path:
        return None

    # Check primary candidates
    for base in IMAGE_ROOT_CANDIDATES:
        try:
            resolved_base = base.resolve()
            target = (resolved_base / clean_path).resolve()
            if resolved_base in target.parents and target.is_file():
                return target
        except (ValueError, OSError):
            continue

    # Check local alias map (e.g. occasions)
    local_alias = LOCAL_IMAGE_ASSET_MAP.get(clean_path)
    if local_alias and local_alias != clean_path:
        return _resolve_local_image_path(local_alias)

    return None


def extract_asset_key(relative_path_or_url: str) -> str:
    """Normalize a path or URL into its relative asset key if it points to Sulocraft media."""
    if not relative_path_or_url:
        return ""
    val = relative_path_or_url.strip()
    image_base = settings.image_base_url.rstrip("/")
    if image_base and val.startswith(f"{image_base}/"):
        return val[len(image_base):].lstrip("/")
    if val.startswith(("http://", "https://")):
        parsed = urlparse(val)
        # Check if URL belongs to our configured image base URL or local static route
        image_base = settings.image_base_url.rstrip("/")
        if image_base and val.startswith(image_base):
            return val[len(image_base) :].lstrip("/")
        if parsed.path.startswith("/static/images/"):
            return parsed.path[len("/static/images/") :].lstrip("/")
        # External URL without known relative key
        return val
    return val.lstrip("/")


def inspect_image_file(clean_path: str) -> tuple[int | None, int | None, str | None]:
    """Read dimensions and content type from local disk if file is available."""
    local_path = _resolve_local_image_path(clean_path)
    if local_path:
        try:
            with open(local_path, "rb") as fp:
                # 64KB is plenty to read all image headers (including JPEG markers)
                header = fp.read(65536)
                w, h, mime = inspect_image_bytes(header)
                if mime is None:
                    mime = mimetypes.guess_type(local_path.name)[0]
                return w, h, mime
        except (OSError, ValueError):
            pass

    guessed_mime = mimetypes.guess_type(clean_path)[0]
    return None, None, guessed_mime


# In-memory LRU-style cache for image metadata to avoid repeated disk reads
_DIMENSION_CACHE: dict[str, tuple[int | None, int | None, str | None]] = {}


def get_image_dimensions(relative_path_or_url: str) -> tuple[int | None, int | None, str | None]:
    """Resolve intrinsic width, height, and content type for an asset key or URL.

    Security guarantees:
    - Never makes outbound HTTP requests (SSRF safe).
    - Prevents directory traversal (rejects '..', absolute paths).
    - Unknown/unreachable files return (None, None, content_type) safely.
    """
    if not relative_path_or_url:
        return None, None, None

    raw = relative_path_or_url.strip()
    if raw in _DIMENSION_CACHE:
        return _DIMENSION_CACHE[raw]

    # If external URL that doesn't map to our media host, do NOT probe remotely (prevent SSRF)
    if raw.startswith(("http://", "https://")):
        key = extract_asset_key(raw)
        if key == raw:
            # External URL; guess content type from path extension without remote fetch
            parsed = urlparse(raw)
            guessed = mimetypes.guess_type(parsed.path)[0]
            _DIMENSION_CACHE[raw] = (None, None, guessed)
            return None, None, guessed
        clean_path = key
    else:
        clean_path = extract_asset_key(raw)

    w, h, mime = inspect_image_file(clean_path)
    _DIMENSION_CACHE[raw] = (w, h, mime)
    return w, h, mime


# Responsive media manifest cache
_MANIFEST_CACHE: dict[str, list[dict]] | None = None
_MANIFEST_CACHE_MTIME: float | None = None
_MANIFEST_CACHE_SIZE: int | None = None
_MANIFEST_HASH_CACHE: str = ""


def _find_manifest_path() -> Path | None:
    """Locate the media manifest file across configured settings and filesystem candidate locations."""
    custom_path = getattr(settings, "media_manifest_path", None)
    if custom_path:
        # Prevent traversal if custom path is supplied
        if ".." in custom_path or "\0" in custom_path:
            return None
        p = Path(custom_path).resolve()
        if p.is_file():
            return p

    for candidate in MANIFEST_PATH_CANDIDATES:
        try:
            resolved = candidate.resolve()
            if resolved.is_file():
                return resolved
        except (ValueError, OSError):
            continue
    return None


def _load_media_manifest() -> dict[str, list[dict]]:
    """Safely load, validate, and cache responsive WebP media variants from manifest.json.

    Security & robustness:
    - Bounded file size (<= 10MB) prevents memory exhaustion.
    - Strict version validation (version == 1).
    - Traversal rejection: strips/rejects keys containing '..', '/', null bytes, or backslashes.
    - Validates positive integers for dimensions and rejects duplicate variant widths per asset.
    - Caches by file mtime and size to avoid per-request disk reads or JSON decoding.
    - Returns {} safely on missing, corrupted, or invalid manifest without crashing.
    """
    global _MANIFEST_CACHE, _MANIFEST_CACHE_MTIME, _MANIFEST_CACHE_SIZE, _MANIFEST_HASH_CACHE

    manifest_path = _find_manifest_path()
    if not manifest_path:
        _MANIFEST_CACHE = {}
        _MANIFEST_HASH_CACHE = ""
        return _MANIFEST_CACHE

    try:
        st = manifest_path.stat()
        # Bounded size check
        if st.st_size > 10 * 1024 * 1024:
            _MANIFEST_CACHE = {}
            _MANIFEST_HASH_CACHE = ""
            return _MANIFEST_CACHE

        # Cache hit check
        if (
            _MANIFEST_CACHE is not None
            and _MANIFEST_CACHE_MTIME == st.st_mtime
            and _MANIFEST_CACHE_SIZE == st.st_size
        ):
            return _MANIFEST_CACHE

        content_bytes = manifest_path.read_bytes()
        _MANIFEST_HASH_CACHE = hashlib.sha256(content_bytes).hexdigest()

        data = json.loads(content_bytes.decode("utf-8"))
        if not isinstance(data, dict):
            _MANIFEST_CACHE = {}
            return _MANIFEST_CACHE

        version = data.get("version")
        if version != 1:
            _MANIFEST_CACHE = {}
            return _MANIFEST_CACHE

        assets = data.get("assets")
        if not isinstance(assets, list):
            _MANIFEST_CACHE = {}
            return _MANIFEST_CACHE

        parsed_manifest: dict[str, list[dict]] = {}
        for asset in assets:
            if not isinstance(asset, dict):
                continue
            asset_key = asset.get("key")
            if not isinstance(asset_key, str) or not asset_key:
                continue
            # Security: reject directory traversal, absolute paths, null bytes, backslashes
            if ".." in asset_key or asset_key.startswith("/") or "\\" in asset_key or "\0" in asset_key:
                continue

            variants_raw = asset.get("variants")
            if not isinstance(variants_raw, list):
                continue

            safe_variants: list[dict] = []
            seen_widths: set[int] = set()
            for v in variants_raw:
                if not isinstance(v, dict):
                    continue
                v_key = v.get("key")
                v_width = v.get("width")
                v_height = v.get("height")
                v_type = v.get("contentType", "image/webp")
                v_desc = v.get("descriptor") or (f"{v_width}w" if isinstance(v_width, int) else None)

                # Validation
                if not isinstance(v_key, str) or not v_key:
                    continue
                if ".." in v_key or v_key.startswith("/") or "\\" in v_key or "\0" in v_key:
                    continue
                if not isinstance(v_width, int) or v_width <= 0:
                    continue
                if not isinstance(v_height, int) or v_height <= 0:
                    continue
                if v_width in seen_widths:
                    # Duplicate width rejection
                    continue
                seen_widths.add(v_width)

                safe_variants.append({
                    "key": v_key,
                    "width": v_width,
                    "height": v_height,
                    "contentType": v_type,
                    "descriptor": v_desc,
                    "bytes": v.get("bytes"),
                    "sha256": v.get("sha256"),
                })

            # Sort by width ascending
            safe_variants.sort(key=lambda item: item["width"])
            parsed_manifest[asset_key] = safe_variants

        _MANIFEST_CACHE = parsed_manifest
        _MANIFEST_CACHE_MTIME = st.st_mtime
        _MANIFEST_CACHE_SIZE = st.st_size
        return _MANIFEST_CACHE

    except (OSError, ValueError, json.JSONDecodeError):
        _MANIFEST_CACHE = {}
        _MANIFEST_HASH_CACHE = ""
        return _MANIFEST_CACHE


def get_media_manifest_hash() -> str:
    """Return SHA256 hex digest of the current media manifest, or empty string if missing."""
    global _MANIFEST_HASH_CACHE
    _load_media_manifest()
    return _MANIFEST_HASH_CACHE


def get_image_variants(key_or_url: str) -> list[MediaVariantOut]:
    """Resolve responsive WebP variants for an asset key or URL from the verified manifest.

    Guarantees:
    - Never performs outbound HTTP requests (SSRF safe).
    - Prevents directory traversal (rejects '..', absolute paths, null bytes).
    - Resolves variant URLs using configured build_image_url.
    - Returns variants sorted by width ascending with descriptor format '<width>w'.
    - Returns [] for unknown, unoptimized, or external images safely.
    """
    if not key_or_url or not key_or_url.strip():
        return []

    raw = key_or_url.strip()
    if ".." in raw or "\\" in raw or "\0" in raw:
        return []

    # If external URL that doesn't map to our media host, return empty
    if raw.startswith(("http://", "https://")):
        key = extract_asset_key(raw)
        if key == raw:
            return []
        clean_key = key
    else:
        clean_key = extract_asset_key(raw)

    manifest = _load_media_manifest()
    variants_data = manifest.get(clean_key)

    if not variants_data:
        # Check local alias map (e.g. occasions)
        alias = LOCAL_IMAGE_ASSET_MAP.get(clean_key)
        if alias and alias != clean_key:
            variants_data = manifest.get(alias)

    if not variants_data:
        return []

    results: list[MediaVariantOut] = []
    for v in variants_data:
        v_url = build_image_url(v["key"])
        results.append(
            MediaVariantOut(
                url=v_url,
                key=v["key"],
                width=v["width"],
                height=v["height"],
                content_type=v.get("contentType", "image/webp"),
                descriptor=v.get("descriptor"),
            )
        )
    return results


def build_media_metadata(
    key_or_url: str,
    alt_text: str | None = None,
    db_width: int | None = None,
    db_height: int | None = None,
    db_content_type: str | None = None,
    variants: list[MediaVariantOut] | None = None,
) -> MediaMetadataOut | None:
    """Build a rich MediaMetadataOut object with resolved URL, key, alt text, dimensions, and MIME type."""
    if not key_or_url or not key_or_url.strip():
        return None

    raw = key_or_url.strip()
    key = extract_asset_key(raw) if not raw.startswith(("http://", "https://")) else (
        extract_asset_key(raw) if extract_asset_key(raw) != raw else None
    )
    url = build_image_url(raw)

    width = db_width
    height = db_height
    content_type = db_content_type

    # If dimensions not in DB, inspect file
    if width is None or height is None or content_type is None:
        file_w, file_h, file_mime = get_image_dimensions(key or raw)
        if width is None:
            width = file_w
        if height is None:
            height = file_h
        if content_type is None:
            content_type = file_mime

    resolved_variants = variants if variants is not None else get_image_variants(key or raw)

    return MediaMetadataOut(
        url=url,
        key=key,
        alt_text=alt_text,
        width=width,
        height=height,
        content_type=content_type,
        variants=resolved_variants,
    )

