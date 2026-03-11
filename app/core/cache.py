from abc import ABC, abstractmethod
from typing import Optional
import json

from app.core.config import settings, CacheType


class AbstractCache(ABC):
    @abstractmethod
    async def get(self, key: str) -> Optional[dict]: ...

    @abstractmethod
    async def set(self, key: str, value: dict, ttl: Optional[int] = None) -> None: ...

    @abstractmethod
    async def delete(self, key: str) -> None: ...

    @abstractmethod
    async def exists(self, key: str) -> bool: ...

    @abstractmethod
    async def close(self) -> None: ...


class RedisCache(AbstractCache):
    def __init__(self) -> None:
        import redis.asyncio as redis
        self._client = redis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True,
        )

    async def ping(self) -> None:
        await self._client.ping()

    async def get(self, key: str) -> Optional[dict]:
        value = await self._client.get(key)
        return json.loads(value) if value else None

    async def set(self, key: str, value: dict, ttl: Optional[int] = None) -> None:
        await self._client.setex(key, ttl or settings.CACHE_TTL, json.dumps(value))

    async def delete(self, key: str) -> None:
        await self._client.delete(key)

    async def exists(self, key: str) -> bool:
        return await self._client.exists(key) > 0

    async def close(self) -> None:
        await self._client.aclose()


class MemoryCache(AbstractCache):
    def __init__(self) -> None:
        self._store: dict[str, dict] = {}

    async def get(self, key: str) -> Optional[dict]:
        return self._store.get(key)

    async def set(self, key: str, value: dict, ttl: Optional[int] = None) -> None:
        # TTL ignored for simplicity in memory backend (dev-only)
        self._store[key] = value

    async def delete(self, key: str) -> None:
        self._store.pop(key, None)

    async def exists(self, key: str) -> bool:
        return key in self._store

    async def close(self) -> None:
        self._store.clear()


# ---- Singleton -----------------------------------------------------------

_cache_instance: Optional[AbstractCache] = None


async def init_cache() -> None:
    global _cache_instance
    if settings.CACHE_TYPE == CacheType.REDIS:
        instance = RedisCache()
        await instance.ping()
        _cache_instance = instance
    else:
        _cache_instance = MemoryCache()


async def close_cache() -> None:
    global _cache_instance
    if _cache_instance is not None:
        await _cache_instance.close()
        _cache_instance = None


def get_cache() -> AbstractCache:
    if _cache_instance is None:
        raise RuntimeError("Cache not initialized")
    return _cache_instance


# Legacy alias — kept for backward compatibility with existing service code
def get_redis() -> AbstractCache:
    return get_cache()


class CacheService:
    """Thin facade used by application services."""

    def __init__(self) -> None:
        self._cache = get_cache()

    async def get(self, key: str) -> Optional[dict]:
        return await self._cache.get(key)

    async def set(self, key: str, value: dict, ttl: int = settings.CACHE_TTL) -> None:
        await self._cache.set(key, value, ttl)

    async def delete(self, key: str) -> None:
        await self._cache.delete(key)

    async def exists(self, key: str) -> bool:
        return await self._cache.exists(key)
