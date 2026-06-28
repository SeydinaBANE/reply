from dataclasses import dataclass

from fastapi.testclient import TestClient

from conftest import FakeEmbedder, FakeGenerator, FakeStore
from rag_service.ingestion import IngestService
from rag_service.main import app, get_state
from rag_service.models import Passage
from rag_service.pipeline import RagPipeline
from rag_service.retrieval import Retriever


@dataclass
class _StubState:
    pipeline: RagPipeline
    ingest: IngestService


def _build_state(passages: list[Passage]) -> _StubState:
    store = FakeStore(passages)
    retriever = Retriever(FakeEmbedder(), store, top_k=5)
    pipeline = RagPipeline(retriever, FakeGenerator("stub answer"))
    ingest = IngestService(FakeEmbedder(), store, chunk_size=10, chunk_overlap=2)
    return _StubState(pipeline=pipeline, ingest=ingest)


def test_query_endpoint_returns_answer_and_sources() -> None:
    passages = [Passage(document_id="a#0", content="alpha", score=0.9)]
    app.dependency_overrides[get_state] = lambda: _build_state(passages)
    client = TestClient(app)
    response = client.post("/query", json={"question": "what?"})
    app.dependency_overrides.clear()

    assert response.status_code == 200
    body = response.json()
    assert body["answer"] == "stub answer"
    assert body["sources"][0]["document_id"] == "a#0"


def test_query_endpoint_empty_corpus_returns_409() -> None:
    app.dependency_overrides[get_state] = lambda: _build_state([])
    client = TestClient(app)
    response = client.post("/query", json={"question": "what?"})
    app.dependency_overrides.clear()

    assert response.status_code == 409


def test_ingest_endpoint_returns_chunk_count() -> None:
    app.dependency_overrides[get_state] = lambda: _build_state([])
    client = TestClient(app)
    response = client.post("/ingest", json={"document_id": "doc", "content": "a " * 50})
    app.dependency_overrides.clear()

    assert response.status_code == 201
    assert response.json()["chunks"] > 0
