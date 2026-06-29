from dataclasses import dataclass

from fastapi.testclient import TestClient

from conftest import FakeEmbedder, FakeGenerator, FakeStore
from rag_service.ingestion import IngestService
from rag_service.main import app
from rag_service.models import Passage
from rag_service.pipeline import RagPipeline
from rag_service.retrieval import Retriever

API_KEY = "test-key"
AUTH = {"X-API-Key": API_KEY}


@dataclass
class _StubState:
    pipeline: RagPipeline
    ingest: IngestService
    store: FakeStore
    api_key: str


def _install_state(passages: list[Passage]) -> _StubState:
    store = FakeStore(passages)
    retriever = Retriever(FakeEmbedder(), store, top_k=5)
    pipeline = RagPipeline(retriever, FakeGenerator("stub answer"))
    ingest = IngestService(FakeEmbedder(), store, chunk_size=10, chunk_overlap=2)
    state = _StubState(pipeline=pipeline, ingest=ingest, store=store, api_key=API_KEY)
    app.state.rag = state
    return state


def test_query_endpoint_returns_answer_and_sources() -> None:
    _install_state([Passage(document_id="a#0", content="alpha", score=0.9)])
    client = TestClient(app)
    response = client.post("/query", json={"question": "what?"}, headers=AUTH)

    assert response.status_code == 200
    body = response.json()
    assert body["answer"] == "stub answer"
    assert body["sources"][0]["document_id"] == "a#0"


def test_query_endpoint_empty_corpus_returns_409() -> None:
    _install_state([])
    client = TestClient(app)
    response = client.post("/query", json={"question": "what?"}, headers=AUTH)

    assert response.status_code == 409


def test_query_endpoint_without_api_key_returns_401() -> None:
    _install_state([])
    client = TestClient(app)
    response = client.post("/query", json={"question": "what?"})

    assert response.status_code == 401


def test_query_endpoint_with_wrong_api_key_returns_401() -> None:
    _install_state([])
    client = TestClient(app)
    response = client.post("/query", json={"question": "what?"}, headers={"X-API-Key": "nope"})

    assert response.status_code == 401


def test_query_endpoint_rejects_too_long_question() -> None:
    _install_state([])
    client = TestClient(app)
    response = client.post("/query", json={"question": "x" * 2_001}, headers=AUTH)

    assert response.status_code == 422


def test_ingest_endpoint_returns_chunk_count() -> None:
    _install_state([])
    client = TestClient(app)
    response = client.post("/ingest", json={"document_id": "doc", "content": "a " * 50}, headers=AUTH)

    assert response.status_code == 201
    assert response.json()["chunks"] > 0


def test_ingest_endpoint_without_api_key_returns_401() -> None:
    _install_state([])
    client = TestClient(app)
    response = client.post("/ingest", json={"document_id": "doc", "content": "abc"})

    assert response.status_code == 401


def test_ingest_endpoint_rejects_too_long_content() -> None:
    _install_state([])
    client = TestClient(app)
    response = client.post(
        "/ingest", json={"document_id": "doc", "content": "a" * 200_001}, headers=AUTH
    )

    assert response.status_code == 422


def test_delete_endpoint_returns_deleted_count() -> None:
    _install_state([])
    client = TestClient(app)
    response = client.delete("/documents/doc", headers=AUTH)

    assert response.status_code == 200
    assert response.json() == {"deleted": 1}


def test_healthz_is_public() -> None:
    client = TestClient(app)
    response = client.get("/healthz")

    assert response.status_code == 200
