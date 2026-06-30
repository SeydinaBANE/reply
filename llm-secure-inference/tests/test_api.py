from dataclasses import dataclass

from fastapi.testclient import TestClient

from conftest import FakeRedis
from inference.audit import LoggingAuditLogger
from inference.auth import ApiKeyAuthenticator
from inference.backend import Completion, EchoBackend
from inference.errors import BackendError
from inference.main import app, get_state
from inference.ratelimit import RateLimiter
from inference.service import InferenceService


@dataclass
class _StubState:
    service: InferenceService


class _FailingBackend:
    async def complete(self, prompt: str, max_tokens: int) -> Completion:
        raise BackendError("backend down")


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


def test_completions_rate_limited_returns_429() -> None:
    state = _state(limit=1)
    app.dependency_overrides[get_state] = lambda: state
    client = TestClient(app)
    headers = {"Authorization": "Bearer k1"}
    client.post("/v1/completions", json={"prompt": "hi"}, headers=headers)
    response = client.post("/v1/completions", json={"prompt": "hi"}, headers=headers)
    app.dependency_overrides.clear()
    assert response.status_code == 429


def test_completions_backend_error_returns_502() -> None:
    service = InferenceService(
        ApiKeyAuthenticator(["k1"]),
        RateLimiter(FakeRedis(), 10),
        _FailingBackend(),
        LoggingAuditLogger(),
    )
    state = _StubState(service=service)
    app.dependency_overrides[get_state] = lambda: state
    client = TestClient(app)
    response = client.post(
        "/v1/completions", json={"prompt": "hi"}, headers={"Authorization": "Bearer k1"}
    )
    app.dependency_overrides.clear()
    assert response.status_code == 502
