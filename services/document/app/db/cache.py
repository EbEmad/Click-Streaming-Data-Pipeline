import json
import logging
from typing import Any
import redis.asyncio as aioredis
from .config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

class RedisCache:

    def __init__(self):
        self.redis: aioredis.Redis | None=None

    async def connect(self):
        """Initialize Redis connection."""
        try:
            self.redis=await aioredis.from_url(
                settings.redis_url,
                encoding="utf-8",
                decode_responses=True,
                max_connections=50,
            )

            await self.redis.ping()
            logger.info("Redis connected successfully")
        except Exception as e:
            logger.error(f"Redis connection failed: {e}")
            raise

    async def disconnect(self):
        """Close Redis connection."""
        if self.redis:
            await self.redis.close()
            logger.info("Redis disconnected")
