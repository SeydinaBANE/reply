import hashlib
import logging
from typing import Protocol

from redis.asyncio import Redis

from rag_service.errors import EmbeddingError

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
        cached = await self._redis.get(key)
        if cached is not None:
            return self._decode(cached)
        try:
            vector = await self._backend.embed(text)
        except Exception as exc:
            raise EmbeddingError(str(exc)) from exc
        await self._redis.set(key, self._encode(vector), ex=self._ttl)
        return vector

    @staticmethod
    def _cache_key(text: str) -> str:
        digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
        return f"emb:{digest}"

    @staticmethod
    def _encode(vector: list[float]) -> bytes:
        return ",".join(repr(value) for value in vector).encode("utf-8")

    @staticmethod
    def _decode(raw: bytes) -> list[float]:
        return [float(value) for value in raw.decode("utf-8").split(",")]
