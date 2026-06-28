import logging

from redis.asyncio import Redis

from monitor.models import AlertLevel, DriftResult

logger = logging.getLogger(__name__)


class AlertPublisher:
    def __init__(self, redis: Redis, channel: str = "drift-alerts") -> None:
        self._redis = redis
        self._channel = channel

    async def publish(self, model: str, result: DriftResult) -> None:
        if result.level is AlertLevel.OK:
            return
        message = f"{model}:{result.level.value}:{result.psi:.4f}"
        await self._redis.publish(self._channel, message)
        logger.warning("published drift alert %s", message)
