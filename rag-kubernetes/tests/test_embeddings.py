import pytest

from rag_service.embeddings import CachedEmbedder
from rag_service.errors import EmbeddingError


class _Backend:
    def __init__(self) -> None:
        self.calls = 0

    async def embed(self, text: str) -> list[float]:
        self.calls += 1
        return [1.0, 2.0, 3.0]


class _FailingBackend:
    async def embed(self, text: str) -> list[float]:
        raise RuntimeError("backend down")


class _BoomRedis:
    async def get(self, key: str) -> bytes | None:
        raise RuntimeError("redis down")

    async def set(self, key: str, value: bytes, ex: int | None = None) -> None:
        raise RuntimeError("redis down")


@pytest.mark.asyncio
async def test_embed_caches_second_call() -> None:
    from conftest import FakeRedis

    backend = _Backend()
    embedder = CachedEmbedder(backend, FakeRedis(), ttl=60)
    first = await embedder.embed("hello")
    second = await embedder.embed("hello")
    assert first == second
    assert backend.calls == 1


@pytest.mark.asyncio
async def test_embed_backend_failure_raises_embedding_error() -> None:
    from conftest import FakeRedis

    embedder = CachedEmbedder(_FailingBackend(), FakeRedis(), ttl=60)
    with pytest.raises(EmbeddingError):
        await embedder.embed("hello")


@pytest.mark.asyncio
async def test_embed_continues_when_redis_fails() -> None:
    backend = _Backend()
    embedder = CachedEmbedder(backend, _BoomRedis(), ttl=60)
    result = await embedder.embed("hello")
    assert result == [1.0, 2.0, 3.0]
    assert backend.calls == 1
