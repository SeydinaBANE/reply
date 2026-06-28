from dataclasses import dataclass

from fastapi.testclient import TestClient

from conftest import FakeRedis
from inference.audit import LoggingAuditLogger
from inference.auth import ApiKeyAuthenticator
from inference.backend import EchoBackend
from inference.main import app, get_state
from inference.ratelimit import RateLimiter
from inference.service import InferenceService


@dataclass
class _StubState:
    service: InferenceService


def _state(limit: int = 10) -> _StubState:
    service = InferenceService(
        ApiKeyAuthenticator(["k1"]),
        RateLimiter(FakeRedis(), limit),
        EchoBackend(),
        LoggingAuditLogger(),
    )
    return _StubState(service=service)


def test_completions_authorized() -> None:
    app.dependency_overrides[get_state] = lambda: _state()
    client = TestClient(app)
    response = client.post(
        "/v1/completions",
        json={"prompt": "hello world"},
        headers={"Authorization": "Bearer k1"},
    )
    app.dependency_overrides.clear()
    assert response.status_code == 200
    assert response.json()["completion"] == "hello world"
    assert response.headers["X-RateLimit-Remaining"] == "9"


def test_completions_missing_token_returns_401() -> None:
    app.dependency_overrides[get_state] = lambda: _state()
    client = TestClient(app)
    response = client.post("/v1/completions", json={"prompt": "hi"})
    app.dependency_overrides.clear()
    assert response.status_code == 401


def test_completions_invalid_key_returns_401() -> None:
    app.dependency_overrides[get_state] = lambda: _state()
    client = TestClient(app)
    response = client.post(
        "/v1/completions",
        json={"prompt": "hi"},
        headers={"Authorization": "Bearer wrong"},
    )
    app.dependency_overrides.clear()
    assert response.status_code == 401
