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
