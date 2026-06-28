import pytest

from conftest import FakeEmbedder, FakeGenerator, FakeStore
from rag_service.errors import EmptyCorpusError
from rag_service.generation import build_prompt
from rag_service.ingestion import IngestService
from rag_service.models import Passage
from rag_service.pipeline import RagPipeline
from rag_service.retrieval import Retriever


def test_build_prompt_numbers_sources() -> None:
    passages = [
        Passage(document_id="a#0", content="alpha", score=0.9),
        Passage(document_id="b#0", content="beta", score=0.8),
    ]
    prompt = build_prompt("question?", passages)
    assert "[1] alpha" in prompt
    assert "[2] beta" in prompt
    assert "question?" in prompt


@pytest.mark.asyncio
async def test_pipeline_answer_returns_sources() -> None:
    passages = [Passage(document_id="a#0", content="alpha", score=0.9)]
    retriever = Retriever(FakeEmbedder(), FakeStore(passages), top_k=5)
    generator = FakeGenerator("the answer")
    pipeline = RagPipeline(retriever, generator)

    response = await pipeline.answer("question?")

    assert response.answer == "the answer"
    assert response.sources == passages


@pytest.mark.asyncio
async def test_pipeline_answer_empty_corpus_propagates() -> None:
    retriever = Retriever(FakeEmbedder(), FakeStore([]), top_k=5)
    pipeline = RagPipeline(retriever, FakeGenerator())
    with pytest.raises(EmptyCorpusError):
        await pipeline.answer("question?")


@pytest.mark.asyncio
async def test_ingest_service_stores_chunks() -> None:
    store = FakeStore()
    service = IngestService(FakeEmbedder(), store, chunk_size=10, chunk_overlap=2)
    count = await service.ingest("doc", "a " * 50)
    assert count == len(store.added)
    assert count > 0
