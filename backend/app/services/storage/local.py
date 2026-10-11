"""Local filesystem storage provider for durable zero-credential development and preprod."""

import logging
from pathlib import Path
from app.core.config import settings
from app.services.storage.base import BaseStorageProvider

logger = logging.getLogger(__name__)


def _find_storage_root() -> Path:
    """Find persistent public/images directory location."""
    candidates = [
        Path("public/images"),
        Path("../public/images"),
        Path("/app/public/images"),
    ]
    for c in candidates:
        if c.is_dir():
            return c.resolve()
    default_dir = Path("public/images")
    default_dir.mkdir(parents=True, exist_ok=True)
    return default_dir.resolve()


class LocalStorageProvider(BaseStorageProvider):
    """Local storage provider that persists files directly to the public/images disk directory."""

    def __init__(self, base_dir: Path | str | None = None, base_url: str | None = None):
        if base_dir:
            self.base_dir = Path(base_dir).resolve()
            self.base_dir.mkdir(parents=True, exist_ok=True)
        else:
            self.base_dir = _find_storage_root()

        self.base_url = (base_url or settings.image_base_url).rstrip("/")

    def _resolve_safe_path(self, destination_path: str) -> Path:
        """Sanitize and ensure destination_path is safely contained within base_dir."""
        clean_path = destination_path.lstrip("/\\")
        target_path = (self.base_dir / clean_path).resolve()
        try:
            target_path.relative_to(self.base_dir)
        except ValueError:
            raise ValueError(f"Path traversal detected: {destination_path}")
        return target_path

    def upload_file(
        self,
        file_bytes: bytes,
        destination_path: str,
        content_type: str = "image/webp",
    ) -> str:
        """Persist uploaded bytes directly to disk and return public image URL."""
        target_path = self._resolve_safe_path(destination_path)
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_bytes(file_bytes)

        clean_path = destination_path.lstrip("/\\")
        return f"{self.base_url}/{clean_path}"

    def delete_file(self, destination_path: str) -> bool:
        """Remove file from disk storage."""
        target_path = self._resolve_safe_path(destination_path)
        try:
            if target_path.is_file():
                target_path.unlink()
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to delete local file ({destination_path}): {e}")
            return False
