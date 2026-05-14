from __future__ import annotations

import json
from collections.abc import Callable
from typing import TypeVar

from app.cache.redis_client import get_cache_backend
from app.core.config import settings

T = TypeVar("T")


class CacheManager:
    def __init__(self) -> None:
        self._backend = get_cache_backend()

    def get_json(self, key: str) -> dict[str, object] | None:
        raw = self._backend.get(key)
        if raw is None:
            return None
        return json.loads(raw)

    def set_json(
        self, key: str, payload: dict[str, object], ttl_seconds: int | None = None
    ) -> None:
        ttl = ttl_seconds or settings.cache_default_ttl_seconds
        self._backend.set(key, json.dumps(payload), ttl)

    def get_or_set_json(
        self,
        key: str,
        loader: Callable[[], dict[str, object]],
        ttl_seconds: int | None = None,
    ) -> dict[str, object]:
        cached = self.get_json(key)
        if cached is not None:
            return cached

        fresh = loader()
        self.set_json(key=key, payload=fresh, ttl_seconds=ttl_seconds)
        return fresh

    def invalidate_key(self, key: str) -> None:
        self._backend.delete(key)

    def invalidate_prefix(self, prefix: str) -> int:
        return self._backend.delete_prefix(prefix)


cache_manager = CacheManager()
