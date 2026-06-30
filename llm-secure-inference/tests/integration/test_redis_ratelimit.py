import pytest

pytest.importorskip("testcontainers")

from redis.asyncio import Redis
from testcontainers.redis import RedisContainer

from inference.errors import RateLimitExceededError
from inference.ratelimit import RateLimiter

pytestmark = [pytest.mark.integration, pytest.mark.asyncio]


async def test_ratelimit_enforced_against_real_redis() -> None:
    with RedisContainer() as container:
        host = container.get_container_host_ip()
        port = container.get_exposed_port(6379)
        client: Redis = Redis.from_url(f"redis://{host}:{port}/0")
        try:
            limiter = RateLimiter(client, limit_per_minute=2)
            assert await limiter.check("k1") == 1
            assert await limiter.check("k1") == 0
            with pytest.raises(RateLimitExceededError):
                await limiter.check("k1")
        finally:
            await client.aclose()
