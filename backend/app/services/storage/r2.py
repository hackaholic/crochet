"""Cloudflare R2 S3-compatible storage provider."""

import logging
from app.core.config import settings
from app.services.storage.base import BaseStorageProvider

logger = logging.getLogger(__name__)


class CloudflareR2StorageProvider(BaseStorageProvider):
    """Direct integration with Cloudflare R2 bucket via S3 API."""

    def __init__(self):
        try:
            import boto3
            from botocore.config import Config

            self.client = boto3.client(
                "s3",
                endpoint_url=settings.r2_endpoint,
                aws_access_key_id=settings.r2_access_key_id,
                aws_secret_access_key=settings.r2_secret_access_key,
                config=Config(signature_version="s3v4"),
                region_name="auto",
            )
        except ImportError:
            raise RuntimeError(
                "boto3 is required for CloudflareR2StorageProvider. Install with: pip install boto3"
            )

        self.bucket = settings.r2_public_bucket
        self.base_url = settings.r2_public_base_url.rstrip("/")

    def upload_file(
        self,
        file_bytes: bytes,
        destination_path: str,
        content_type: str = "image/webp",
    ) -> str:
        """Upload raw binary bytes to Cloudflare R2 and return the public image CDN URL."""
        clean_path = destination_path.lstrip("/")
        self.client.put_object(
            Bucket=self.bucket,
            Key=clean_path,
            Body=file_bytes,
            ContentType=content_type,
            CacheControl="public, max-age=31536000, immutable",
        )
        return f"{self.base_url}/{clean_path}"

    def delete_file(self, destination_path: str) -> bool:
        """Delete an object from Cloudflare R2."""
        clean_path = destination_path.lstrip("/")
        try:
            self.client.delete_object(Bucket=self.bucket, Key=clean_path)
            return True
        except Exception as e:
            logger.error(f"Failed to delete object from R2 ({clean_path}): {e}")
            return False
