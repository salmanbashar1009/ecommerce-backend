import redis.asyncio as redis
import json
from app.core.config import settings
from typing import Optional, Any

class RedisCache:
    """
    Async Redis Cache Wrapper
    Handles serialization, deserialization, and error safety.
    """
    def __init__(self):
        self.client = redis.from_url(
            settings.REDIS_URL, 
            decode_responses=True
        )


    async def get_cached_product(self, key:str)-> Optional[Any]:
         """
        Retrieve value from cache.
        Returns None if key not found or on failure.
        """
         try:
             cached_data = await self.client.get(key)
             if cached_data is None:
                 return None
             return json.loads(cached_data)
         except Exception:
             return None
         

    async def set_cached_product(self, key:str, value:Any, expire_seconds:int = 3600) -> None:
        """
        Store value in cache with optional expiration.
        """
        try:
            serialized_value = json.dumps(value)
            await self.client.set(key,serialized_value, ex=expire_seconds)
        except Exception:
            pass  # Fail silently on cache set errors to avoid impacting main flow