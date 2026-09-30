"""Abstract base class for asset storage providers."""

from abc import ABC, abstractmethod


class BaseStorageProvider(ABC):
    """Abstract storage provider interface."""

    @abstractmethod
    def upload_file(
        self,
        file_bytes: bytes,
        destination_path: str,
        content_type: str = "image/webp",
    ) -> str:
        """Upload file bytes and return the public CDN URL."""
        pass

    @abstractmethod
    def delete_file(self, destination_path: str) -> bool:
        """Delete an object by its relative key path."""
        pass
