import hashlib
import logging
from typing import Protocol

from redis.asyncio import Redis

from rag_service.errors import EmbeddingError
from rag_service.metrics import CACHE_EVENTS

logger = logging.getLogger(__name__)


class EmbeddingBackend(Protocol):
    async def embed(self, text: str) -> list[float]: ...


class CachedEmbedder:
    def __init__(self, backend: EmbeddingBackend, redis: Redis, ttl: int) -> None:
        self._backend = backend
        self._redis = redis
        self._ttl = ttl

    async def embed(self, text: str) -> list[float]:
        key = self._cache_key(text)
        cached = await self._read_cache(key)
        if cached is not None:
            return cached
        try:
            vector = await self._backend.embed(text)
        except EmbeddingError:
            raise
        except Exception as exc:
            raise EmbeddingError(str(exc)) from exc
        await self._write_cache(key, vector)
        return vector

    async def _read_cache(self, key: str) -> list[float] | None:
        try:
            cached = await self._redis.get(key)
        except Exception as exc:
            logger.warning("redis get failed, bypassing cache: %s", exc)
            return None
        if cached is None:
            CACHE_EVENTS.labels(result="miss").inc()
            return None
        CACHE_EVENTS.labels(result="hit").inc()
        return self._decode(cached)

    async def _write_cache(self, key: str, vector: list[float]) -> None:
        try:
            await self._redis.set(key, self._encode(vector), ex=self._ttl)
        except Exception as exc:
            logger.warning("redis set failed, continuing without caching: %s", exc)

    @staticmethod
    def _cache_key(text: str) -> str:
        digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
        return f"emb:{digest}"

    @staticmethod
    def _encode(vector: list[float]) -> bytes:
        return ",".join(repr(value) for value in vector).encode("utf-8")

    @staticmethod
    def _decode(raw: bytes | str) -> list[float]:
        text = raw.decode("utf-8") if isinstance(raw, bytes) else raw
        return [float(value) for value in text.split(",")]
