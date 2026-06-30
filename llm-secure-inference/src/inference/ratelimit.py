import logging
from collections.abc import Callable

from redis.asyncio import Redis
from redis.exceptions import RedisError

from inference.errors import RateLimiterUnavailableError, RateLimitExceededError

logger = logging.getLogger(__name__)

_FIXED_WINDOW_LUA = """
local current = redis.call('INCR', KEYS[1])
if current == 1 then
  redis.call('EXPIRE', KEYS[1], ARGV[1])
end
return current
"""

_WINDOW_SECONDS = 60


class RateLimiter:
    def __init__(
        self,
        redis: Redis,
        limit_per_minute: int,
        *,
        fail_open: bool = True,
        on_failure: Callable[[], None] | None = None,
    ) -> None:
        self._redis = redis
        self._limit = limit_per_minute
        self._fail_open = fail_open
        self._on_failure = on_failure

    async def check(self, identity: str) -> int:
        key = f"ratelimit:{identity}"
        try:
            count = int(await self._redis.eval(_FIXED_WINDOW_LUA, 1, key, _WINDOW_SECONDS))
        except RedisError as exc:
            return self._degrade(identity, exc)
        if count > self._limit:
            raise RateLimitExceededError(identity)
        return self._limit - count

    def _degrade(self, identity: str, exc: RedisError) -> int:
        if self._on_failure is not None:
            self._on_failure()
        if self._fail_open:
            logger.warning("rate limiter unavailable, failing open for %s: %s", identity, exc)
            return self._limit
        logger.error("rate limiter unavailable, failing closed for %s: %s", identity, exc)
        raise RateLimiterUnavailableError(identity) from exc
