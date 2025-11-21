import redis.asyncio as redis
from typing import Optional
from app.core.config import settings


class RedisClient:
    """Redis client singleton for caching and session management"""

    _instance: Optional[redis.Redis] = None

    @classmethod
    async def get_instance(cls) -> redis.Redis:
        """Get or create Redis instance"""
        if cls._instance is None:
            cls._instance = await redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True
            )
        return cls._instance

    @classmethod
    async def close(cls):
        """Close Redis connection"""
        if cls._instance is not None:
            await cls._instance.close()
            cls._instance = None


async def get_redis() -> redis.Redis:
    """Dependency to get Redis client"""
    return await RedisClient.get_instance()
