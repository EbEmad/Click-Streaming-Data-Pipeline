import logging

import aioboto3
from botocore.exceptions import ClientError

from .config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class S3Storage:
    """Async S3 storage for document content."""

    def __init__(self):
        self.session = aioboto3.Session(
            aws_access_key_id=settings.minio_access_key,
            aws_secret_access_key=settings.minio_secret_key,
        )
        self.endpoint_url = f"http://{settings.minio_endpoint}"

    def _get_client(self):
        return self.session.client(
            "s3",
            endpoint_url=self.endpoint_url,
            region_name="us-east-1",
            use_ssl=settings.minio_secure,
        )

    async def ensure_buckets(self):
        """Create buckets if they don't exist."""
        async with self._get_client() as s3:
            for bucket in [settings.minio_bucket_documents, "signatures"]:
                try:
                    await s3.head_bucket(Bucket=bucket)
                except ClientError:
                    await s3.create_bucket(Bucket=bucket)
                    logger.info(f"Created bucket: {bucket}")

    async def upload_document(self, document_id: str, content: bytes) -> str:
        """Upload document to S3."""
        object_name = f"{document_id}/content"

        async with self._get_client() as s3:
            await s3.put_object(
                Bucket=settings.minio_bucket_documents, Key=object_name, Body=content
            )

        logger.info(f"Uploaded: {object_name} ({len(content)} bytes)")
        return object_name

    async def get_document(self, document_id: str) -> bytes:
        """Download document from S3."""
        object_name = f"{document_id}/content"

        async with self._get_client() as s3:
            response = await s3.get_object(
                Bucket=settings.minio_bucket_documents, Key=object_name
            )
            async with response["Body"] as stream:
                return await stream.read()


storage = S3Storage()
