import json
from typing import Optional, Any

import redis.asyncio as redis
from app.core.config import settings


class RedisCache:
    """
    Async Redis Cache Wrapper
    Handles serialization, deserialization, and basic error safety.
    """

    def __init__(self):
        self.client = redis.from_url(
            settings.REDIS_URL,
            decode_responses=True
        )

    async def get(self, key: str) -> Optional[Any]:
        """Retrieve value from cache."""
        try:
            cached = await self.client.get(key)
            return json.loads(cached) if cached else None
        except Exception as e:
            # TODO: replace with proper logging
            print(f"Redis GET error: {e}")
            return None

    async def set(
        self,
        key: str,
        value: Any,
        expire_seconds: int = 3600
    ) -> None:
        """Store value in cache with expiration."""
        try:
            await self.client.set(
                key,
                json.dumps(value),
                ex=expire_seconds
            )
        except Exception as e:
            print(f"Redis SET error: {e}")

    async def delete(self, key: str) -> None:
        """Remove a key from cache."""
        try:
            await self.client.delete(key)
        except Exception as e:
            print(f"Redis DELETE error: {e}")

    async def invalidate_product(self, slug: str) -> None:
        """Invalidate product cache entry."""
        await self.delete(self._product_key(slug))

    @staticmethod
    def _product_key(slug: str) -> str:
        return f"product:{slug}"