from redis.asyncio import Redis

from inference.errors import RateLimitExceededError


class RateLimiter:
    def __init__(self, redis: Redis, limit_per_minute: int) -> None:
        self._redis = redis
        self._limit = limit_per_minute

    async def check(self, identity: str) -> int:
        key = f"ratelimit:{identity}"
        count = await self._redis.incr(key)
        if count == 1:
            await self._redis.expire(key, 60)
        if count > self._limit:
            raise RateLimitExceededError(identity)
        return self._limit - count
