import pytest
from unittest.mock import AsyncMock, patch

from app.core.cache import MemoryCache, CacheService, init_cache, close_cache, get_cache
from app.core.config import CacheType


# ---------------------------------------------------------------------------
# MemoryCache
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_memory_cache_set_and_get():
    cache = MemoryCache()
    await cache.set("key", {"value": 42})
    result = await cache.get("key")
    assert result == {"value": 42}


@pytest.mark.asyncio
async def test_memory_cache_get_missing_key_returns_none():
    cache = MemoryCache()
    assert await cache.get("missing") is None


@pytest.mark.asyncio
async def test_memory_cache_delete():
    cache = MemoryCache()
    await cache.set("key", {"x": 1})
    await cache.delete("key")
    assert await cache.get("key") is None


@pytest.mark.asyncio
async def test_memory_cache_exists():
    cache = MemoryCache()
    await cache.set("key", {})
    assert await cache.exists("key") is True
    assert await cache.exists("other") is False


@pytest.mark.asyncio
async def test_memory_cache_close_clears_store():
    cache = MemoryCache()
    await cache.set("key", {"x": 1})
    await cache.close()
    assert await cache.get("key") is None


# ---------------------------------------------------------------------------
# init_cache / get_cache with memory backend
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_init_cache_memory(monkeypatch):
    monkeypatch.setattr("app.core.cache.settings.CACHE_TYPE", CacheType.MEMORY)
    await init_cache()
    cache = get_cache()
    assert isinstance(cache, MemoryCache)
    await close_cache()


# ---------------------------------------------------------------------------
# CacheService facade
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_cache_service_delegates_to_backend(monkeypatch):
    monkeypatch.setattr("app.core.cache.settings.CACHE_TYPE", CacheType.MEMORY)
    await init_cache()

    service = CacheService()
    await service.set("todo:1", {"title": "Buy milk"})
    result = await service.get("todo:1")
    assert result == {"title": "Buy milk"}

    await service.delete("todo:1")
    assert await service.exists("todo:1") is False

    await close_cache()
