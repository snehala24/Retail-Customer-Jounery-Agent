# app/services/session_store.py
import json, os, asyncio, logging
from typing import Any, Optional
import aioredis

logger = logging.getLogger("session_store")

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

class RedisSessionStore:
    """Asynchronous Redis session manager."""
    def __init__(self, redis):
        self.redis = redis

    async def get(self, session_id: str) -> Optional[dict[str, Any]]:
        data = await self.redis.get(session_id)
        if data:
            try:
                return json.loads(data)
            except Exception as e:
                logger.warning(f"Bad session JSON for {session_id}: {e}")
        return None

    async def set(self, session_id: str, data: dict[str, Any]):
        # 7-day TTL
        await self.redis.set(session_id, json.dumps(data), ex=60*60*24*7)

    async def delete(self, session_id: str):
        await self.redis.delete(session_id)


async def create_session_store() -> RedisSessionStore:
    """Factory to create a connected Redis session store."""
    redis = await aioredis.from_url(REDIS_URL, encoding="utf-8", decode_responses=False)
    logger.info(f"Connected to Redis at {REDIS_URL}")
    return RedisSessionStore(redis)
