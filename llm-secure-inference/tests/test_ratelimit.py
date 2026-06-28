import pytest

from conftest import FakeRedis
from inference.errors import RateLimitExceededError
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
