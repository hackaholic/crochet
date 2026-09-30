"""Factory for resolving active storage provider based on environment."""

from app.core.config import settings
from app.services.storage.base import BaseStorageProvider
from app.services.storage.mock import MockStorageProvider


def get_storage_provider() -> BaseStorageProvider:
    """Return CloudflareR2StorageProvider if credentials configured, otherwise MockStorageProvider."""
    if settings.r2_endpoint and settings.r2_access_key_id and settings.r2_secret_access_key:
        try:
            from app.services.storage.r2 import CloudflareR2StorageProvider
            return CloudflareR2StorageProvider()
        except Exception:
            return MockStorageProvider()
    return MockStorageProvider()
