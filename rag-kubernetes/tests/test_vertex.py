import pytest

from rag_service.errors import EmbeddingError
from rag_service.vertex import VertexEmbeddingBackend


class _EmbResult:
    def __init__(self, values: list[float]) -> None:
        self.values = values


class _FakeEmbClient:
    def __init__(self) -> None:
        self.calls = 0

    def get_embeddings(self, texts: list[str]) -> list[_EmbResult]:
        self.calls += 1
        return [_EmbResult([float(len(texts[0]))])]


class _FlakyEmbClient:
    def __init__(self, failures: int) -> None:
        self._failures = failures
        self.calls = 0

    def get_embeddings(self, texts: list[str]) -> list[_EmbResult]:
        self.calls += 1
        if self.calls <= self._failures:
            raise RuntimeError("transient")
        return [_EmbResult([1.0])]


def _backend(client: object, max_attempts: int = 1) -> VertexEmbeddingBackend:
    return VertexEmbeddingBackend(
        "project",
        "location",
        "model",
        timeout=5.0,
        max_attempts=max_attempts,
        backoff_base=0.0,
        client=client,  # type: ignore[arg-type]
    )


@pytest.mark.asyncio
async def test_embed_reuses_injected_client() -> None:
    client = _FakeEmbClient()
    backend = _backend(client)
    first = await backend.embed("hi")
    await backend.embed("yo")
    assert first == [2.0]
    assert client.calls == 2


@pytest.mark.asyncio
async def test_embed_retries_until_success() -> None:
    client = _FlakyEmbClient(failures=2)
    backend = _backend(client, max_attempts=3)
    result = await backend.embed("hello")
    assert result == [1.0]
    assert client.calls == 3


@pytest.mark.asyncio
async def test_embed_raises_after_exhausting_attempts() -> None:
    client = _FlakyEmbClient(failures=5)
    backend = _backend(client, max_attempts=2)
    with pytest.raises(EmbeddingError):
        await backend.embed("hello")
    assert client.calls == 2
