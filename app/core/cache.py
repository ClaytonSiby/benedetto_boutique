from typing import Optional, Any
import json
from app.core.redis import get_redis


class CacheManager:
    """Manage application caching with Redis"""

    def __init__(self):
        self.prefix = "cache:"
        self.default_ttl = 3600  # 1 hour

    async def get(self, key: str) -> Optional[Any]:
        """Get cached value"""
        cache_key = f"{self.prefix}{key}"
        redis_client = await get_redis()

        value = await redis_client.get(cache_key)
        if value:
            return json.loads(value)
        return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set cached value"""
        cache_key = f"{self.prefix}{key}"
        redis_client = await get_redis()

        ttl = ttl or self.default_ttl
        serialized_value = json.dumps(value)

        return await redis_client.setex(cache_key, ttl, serialized_value)

    async def delete(self, key: str) -> bool:
        """Delete cached value"""
        cache_key = f"{self.prefix}{key}"
        redis_client = await get_redis()
        result = await redis_client.delete(cache_key)
        return result > 0

    async def delete_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern"""
        cache_pattern = f"{self.prefix}{pattern}"
        redis_client = await get_redis()

        keys = []
        async for key in redis_client.scan_iter(match=cache_pattern):
            keys.append(key)

        if keys:
            return await redis_client.delete(*keys)
        return 0

    async def exists(self, key: str) -> bool:
        """Check if key exists"""
        cache_key = f"{self.prefix}{key}"
        redis_client = await get_redis()
        return await redis_client.exists(cache_key) > 0


cache_manager = CacheManager()
