import pytest

from rag_service.errors import EmptyCorpusError
from rag_service.models import Passage
from rag_service.retrieval import Retriever


class _FakeEmbedder:
    async def embed(self, text: str) -> list[float]:
        return [0.1, 0.2, 0.3]


class _FakeStore:
    def __init__(self, passages: list[Passage]) -> None:
        self._passages = passages

    async def search(self, embedding: list[float], top_k: int) -> list[Passage]:
        return self._passages[:top_k]

    async def count(self) -> int:
        return len(self._passages)


@pytest.mark.asyncio
async def test_retrieve_empty_corpus() -> None:
    retriever = Retriever(_FakeEmbedder(), _FakeStore([]), top_k=5)
    with pytest.raises(EmptyCorpusError):
        await retriever.retrieve("question")


@pytest.mark.asyncio
async def test_retrieve_returns_top_k() -> None:
    corpus = [Passage(document_id=str(i), content=f"doc {i}", score=1.0) for i in range(10)]
    retriever = Retriever(_FakeEmbedder(), _FakeStore(corpus), top_k=3)
    passages = await retriever.retrieve("question")
    assert len(passages) == 3
