# app/services/session_store.py
import os
import json
import logging
import asyncio
from typing import Optional, Any

# Try to use redis.asyncio (redis-py) if available; fall back to aioredis if not.
try:
    import redis.asyncio as redis_client  # redis-py >= 4.2 (recommended)
    REDIS_CLIENT_NAME = "redis.asyncio"
except Exception:
    try:
        import aioredis as redis_client  # older aioredis package
        REDIS_CLIENT_NAME = "aioredis"
    except Exception:
        redis_client = None
        REDIS_CLIENT_NAME = None

logger = logging.getLogger("session_store")

class SessionStore:
    def __init__(self, url: str, decode_responses: bool = True):
        if redis_client is None:
            raise RuntimeError("No redis client available. Install 'redis' or 'aioredis'.")
        self.url = url
        self.decode_responses = decode_responses
        self._client = None  # lazy connect

    async def _ensure_client(self):
        if self._client is None:
            logger.info(f"Connecting to Redis ({REDIS_CLIENT_NAME}) at {self.url} ...")
            # redis.asyncio.from_url returns a Redis instance with async methods
            try:
                # redis-py style
                self._client = redis_client.from_url(self.url, decode_responses=self.decode_responses)
            except Exception:
                # aioredis style (older) - from_url may differ
                self._client = await redis_client.create_redis_pool(self.url)
            # optionally try ping
            try:
                if hasattr(self._client, "ping"):
                    await self._client.ping()
                elif hasattr(self._client, "execute"):
                    await self._client.execute("PING")
                logger.info(f"Connected to Redis at {self.url}")
            except Exception as e:
                logger.warning(f"Redis ping/connect failed: {e}")

    async def get(self, key: str) -> Optional[dict]:
        await self._ensure_client()
        raw = None
        if hasattr(self._client, "get"):
            raw = await self._client.get(key)
        else:
            # older aioredis execute
            raw = await self._client.execute("GET", key)
        if not raw:
            return None
        try:
            return json.loads(raw)
        except Exception:
            # if value stored as JSON string but decoding fails, return raw
            return raw

    async def set(self, key: str, value: Any, ex: Optional[int] = None) -> bool:
        await self._ensure_client()
        to_store = value if isinstance(value, str) else json.dumps(value)
        if hasattr(self._client, "set"):
            if ex:
                await self._client.set(key, to_store, ex=ex)
            else:
                await self._client.set(key, to_store)
        else:
            # aioredis execute style
            if ex:
                await self._client.execute("SET", key, to_store, "EX", str(ex))
            else:
                await self._client.execute("SET", key, to_store)
        return True

    async def delete(self, key: str) -> bool:
        await self._ensure_client()
        if hasattr(self._client, "delete"):
            await self._client.delete(key)
        else:
            await self._client.execute("DEL", key)
        return True

    async def close(self):
        if self._client is None:
            return
        try:
            if hasattr(self._client, "close"):
                await self._client.close()
            if hasattr(self._client, "connection_pool") and hasattr(self._client.connection_pool, "disconnect"):
                await self._client.connection_pool.disconnect()
        except Exception:
            pass

# Module-level session_store object (may be None until created)
session_store: Optional[SessionStore] = None

async def create_session_store(redis_url: Optional[str] = None) -> SessionStore:
    """
    Create (and assign) the module-level session_store.
    This is designed to be awaited during FastAPI startup.
    """
    global session_store
    if session_store is not None:
        return session_store

    if not redis_url:
        redis_url = os.getenv("REDIS_URL") or os.getenv("REDIS", "redis://localhost:6379/0")

    # create instance and attempt to connect (lazy connect will ping)
    store = SessionStore(redis_url)
    try:
        await store._ensure_client()
    except Exception as e:
        logger.warning(f"create_session_store: connection attempt failed: {e}")

    session_store = store
    return session_store

def get_session_store() -> Optional[SessionStore]:
    """
    Synchronous accessor (for modules that import it).
    May return None if create_session_store hasn't been run yet.
    """
    return session_store
