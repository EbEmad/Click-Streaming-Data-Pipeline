import logging
import redis.asyncio as aioredis

from .config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

class DocumentAnalytics:
    """Real-time document analytics using Redis."""

    def __init__(self):
        self.redis: aioredis.Redis | None = None
    
    async def connect(self):
        """Initialize Redis connection for analytics."""
        try:
            self.redis=await  aioredis.from_url(
                settings.redis_url,
                encoding="utf-8",
                decode_responses=True,
                max_connections=20,
            )

            await self.redis.ping()
            logger.info("Analytics Redis connected")
        except Exception as e:
            logger.error(f"Failed to connect to Analytics Redis: {e}")
            raise
    
    async def disconnect(self):
        """Close Redis connection."""
        if self.redis:
            await self.redis.close()
    
    async def track_view(self, document_id: str, client_ip: str):
        """Track document view (total + unique)."""
        try:
            # Atomic operations
            await self.redis.inc(f"views:{document_id}")
            await self.redis.pfadd(f"unique_views:{document_id}", client_ip)
        except Exception as e:
            logger.error(f"Failed to track view for document {document_id}: {e}")
            raise
    
    async def get_stats(self, document_id: str) -> dict:
        """Get document statistics."""
        try:
            total_views_raw = await self.redis.get(f"views:{document_id}")
            total_views=int(total_views_raw) if total_views_raw else 0
            unique_views=await self.redis.pfcount(f"unique_views:{document_id}")

            return {
                "total_views": total_views,
                "unique_views": unique_views,
            }
        except Exception as e:
            logger.error(f"Failed to get stats for document {document_id}: {e}")
            raise
analytics = DocumentAnalytics()
