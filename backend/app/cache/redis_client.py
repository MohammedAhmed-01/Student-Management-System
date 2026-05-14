from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Protocol

from redis import Redis
from redis.exceptions import RedisError

from app.core.config import settings


class CacheBackend(Protocol):
    def get(self, key: str) -> str | None: ...

    def set(self, key: str, value: str, ttl_seconds: int) -> None: ...

    def delete(self, key: str) -> None: ...

    def delete_prefix(self, prefix: str) -> int: ...


class RedisCacheBackend:
    def __init__(self, url: str) -> None:
        self._client = Redis.from_url(url, decode_responses=True)

    def get(self, key: str) -> str | None:
        return self._client.get(key)

    def set(self, key: str, value: str, ttl_seconds: int) -> None:
        self._client.set(name=key, value=value, ex=ttl_seconds)

    def delete(self, key: str) -> None:
        self._client.delete(key)

    def delete_prefix(self, prefix: str) -> int:
        keys = list(self._client.scan_iter(match=f"{prefix}*"))
        if not keys:
            return 0
        return int(self._client.delete(*keys))


@dataclass(slots=True)
class _MemoryValue:
    value: str
    expires_at: float


class InMemoryCacheBackend:
    def __init__(self) -> None:
        self._store: dict[str, _MemoryValue] = {}

    def get(self, key: str) -> str | None:
        item = self._store.get(key)
        if item is None:
            return None

        if item.expires_at < time.time():
            self._store.pop(key, None)
            return None

        return item.value

    def set(self, key: str, value: str, ttl_seconds: int) -> None:
        self._store[key] = _MemoryValue(
            value=value, expires_at=time.time() + ttl_seconds
        )

    def delete(self, key: str) -> None:
        self._store.pop(key, None)

    def delete_prefix(self, prefix: str) -> int:
        keys = [key for key in self._store if key.startswith(prefix)]
        for key in keys:
            self._store.pop(key, None)
        return len(keys)


_backend: CacheBackend | None = None


def get_cache_backend() -> CacheBackend:
    global _backend
    if _backend is not None:
        return _backend

    try:
        candidate = RedisCacheBackend(settings.redis_url)
        candidate._client.ping()
        _backend = candidate
    except RedisError:
        _backend = InMemoryCacheBackend()

    return _backend
