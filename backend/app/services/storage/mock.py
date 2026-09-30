"""Mock storage provider for zero-credential local development and automated testing."""

from app.core.config import settings
from app.services.storage.base import BaseStorageProvider


class MockStorageProvider(BaseStorageProvider):
    """Local / mock storage provider that returns deterministic public R2 CDN URLs."""

    def __init__(self, base_url: str | None = None):
        self.base_url = (base_url or settings.r2_public_base_url).rstrip("/")
        self.uploaded_files: dict[str, bytes] = {}

    def upload_file(
        self,
        file_bytes: bytes,
        destination_path: str,
        content_type: str = "image/webp",
    ) -> str:
        """Record uploaded bytes in-memory and return full CDN URL."""
        clean_path = destination_path.lstrip("/")
        self.uploaded_files[clean_path] = file_bytes
        return f"{self.base_url}/{clean_path}"

    def delete_file(self, destination_path: str) -> bool:
        """Remove file from in-memory tracking."""
        clean_path = destination_path.lstrip("/")
        return self.uploaded_files.pop(clean_path, None) is not None
