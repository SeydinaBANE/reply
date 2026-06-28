import numpy as np
from fastapi.testclient import TestClient

from conftest import FakePool, FakeRedis
from monitor.alerts import AlertPublisher
from monitor.config import Settings
from monitor.main import AppState, app, get_state
from monitor.store import PredictionStore


def _state(redis: FakeRedis) -> AppState:
    pool = FakePool()
    return AppState(
        pool=pool,
        redis=redis,
        store=PredictionStore(pool),
        alerts=AlertPublisher(redis),
        settings=Settings(),
    )


def test_log_endpoint_records() -> None:
    app.dependency_overrides[get_state] = lambda: _state(FakeRedis())
    client = TestClient(app)
    response = client.post(
        "/log",
        json={"model": "m", "features": [1.0, 2.0], "prediction": 1.0, "latency_ms": 12.0},
    )
    app.dependency_overrides.clear()
    assert response.status_code == 201


def test_drift_endpoint_publishes_on_shift() -> None:
    redis = FakeRedis()
    app.dependency_overrides[get_state] = lambda: _state(redis)
    rng = np.random.default_rng(0)
    reference = rng.normal(size=(300, 2)).tolist()
    current = (rng.normal(size=(300, 2)) + 4.0).tolist()
    client = TestClient(app)
    response = client.post(
        "/drift", json={"model": "m", "reference": reference, "current": current}
    )
    app.dependency_overrides.clear()
    assert response.status_code == 200
    assert response.json()["level"] == "critical"
    assert len(redis.published) == 1


def test_metrics_endpoint_exposes_prometheus() -> None:
    client = TestClient(app)
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "http_request_latency_seconds" in response.text
