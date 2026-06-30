from dataclasses import dataclass

from fastapi.testclient import TestClient
from prometheus_client import REGISTRY

from inference.audit import LoggingAuditLogger
from inference.auth import ApiKeyAuthenticator
from inference.backend import EchoBackend
from inference.main import app, get_state
from inference.ratelimit import RateLimiter
from inference.service import InferenceService
from conftest import FakeRedis


@dataclass
class _StubState:
    service: InferenceService


def _state() -> _StubState:
    service = InferenceService(
        ApiKeyAuthenticator(["k1"]),
        RateLimiter(FakeRedis(), 10),
        EchoBackend(),
        LoggingAuditLogger(),
    )
    return _StubState(service=service)


def test_metrics_endpoint_exposes_prometheus() -> None:
    client = TestClient(app)
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "http_request_latency_seconds" in response.text


def test_auth_failure_increments_counter() -> None:
    before = REGISTRY.get_sample_value("inference_auth_failures_total") or 0.0
    app.dependency_overrides[get_state] = _state
    client = TestClient(app)
    client.post(
        "/v1/completions", json={"prompt": "hi"}, headers={"Authorization": "Bearer wrong"}
    )
    app.dependency_overrides.clear()
    after = REGISTRY.get_sample_value("inference_auth_failures_total") or 0.0
    assert after == before + 1


def test_tokens_counter_increments_on_success() -> None:
    before = REGISTRY.get_sample_value("inference_tokens_total") or 0.0
    app.dependency_overrides[get_state] = _state
    client = TestClient(app)
    client.post(
        "/v1/completions",
        json={"prompt": "hello world"},
        headers={"Authorization": "Bearer k1"},
    )
    app.dependency_overrides.clear()
    after = REGISTRY.get_sample_value("inference_tokens_total") or 0.0
    assert after == before + 2
