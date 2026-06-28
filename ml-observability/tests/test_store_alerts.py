import pytest

from conftest import FakePool, FakeRedis, feature_rows
from monitor.alerts import AlertPublisher
from monitor.models import AlertLevel, DriftResult
from monitor.store import PredictionStore


@pytest.mark.asyncio
async def test_store_record_inserts() -> None:
    pool = FakePool()
    store = PredictionStore(pool)
    await store.record("m", [1.0, 2.0], prediction=1.0, latency_ms=12.0)
    assert len(pool.executed) == 1


@pytest.mark.asyncio
async def test_store_recent_features_parses_json() -> None:
    pool = FakePool(rows=feature_rows([[1.0, 2.0], [3.0, 4.0]]))
    store = PredictionStore(pool)
    features = await store.recent_features("m", limit=10)
    assert features == [[1.0, 2.0], [3.0, 4.0]]


@pytest.mark.asyncio
async def test_alert_publisher_skips_ok_level() -> None:
    redis = FakeRedis()
    await AlertPublisher(redis).publish("m", DriftResult(psi=0.1, level=AlertLevel.OK))
    assert redis.published == []


@pytest.mark.asyncio
async def test_alert_publisher_emits_on_critical() -> None:
    redis = FakeRedis()
    await AlertPublisher(redis).publish("m", DriftResult(psi=0.3, level=AlertLevel.CRITICAL))
    assert len(redis.published) == 1
    assert "critical" in redis.published[0][1]
