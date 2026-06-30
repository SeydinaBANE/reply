import pytest

from conftest import FailingRedis, FakeRedis
from inference.errors import RateLimiterUnavailableError, RateLimitExceededError
from inference.ratelimit import RateLimiter


@pytest.mark.asyncio
async def test_ratelimit_allows_under_quota() -> None:
    limiter = RateLimiter(FakeRedis(), limit_per_minute=3)
    assert await limiter.check("k1") == 2
    assert await limiter.check("k1") == 1


@pytest.mark.asyncio
async def test_ratelimit_blocks_over_quota() -> None:
    limiter = RateLimiter(FakeRedis(), limit_per_minute=1)
    await limiter.check("k1")
    with pytest.raises(RateLimitExceededError):
        await limiter.check("k1")


@pytest.mark.asyncio
async def test_ratelimit_fails_open_when_redis_down() -> None:
    failures: list[None] = []
    limiter = RateLimiter(
        FailingRedis(), limit_per_minute=5, on_failure=lambda: failures.append(None)
    )
    assert await limiter.check("k1") == 5
    assert len(failures) == 1


@pytest.mark.asyncio
async def test_ratelimit_fails_closed_when_configured() -> None:
    limiter = RateLimiter(FailingRedis(), limit_per_minute=5, fail_open=False)
    with pytest.raises(RateLimiterUnavailableError):
        await limiter.check("k1")
