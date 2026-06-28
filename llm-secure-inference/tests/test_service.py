import pytest

from conftest import FakeRedis
from inference.audit import LoggingAuditLogger
from inference.auth import ApiKeyAuthenticator
from inference.backend import EchoBackend
from inference.errors import RateLimitExceededError, UnauthorizedError
from inference.ratelimit import RateLimiter
from inference.service import InferenceService


def _service(limit: int = 10) -> InferenceService:
    return InferenceService(
        ApiKeyAuthenticator(["k1"]),
        RateLimiter(FakeRedis(), limit),
        EchoBackend(),
        LoggingAuditLogger(),
    )


@pytest.mark.asyncio
async def test_service_completes_for_valid_key() -> None:
    completion, remaining = await _service().complete("k1", "hello world", 256)
    assert completion.text == "hello world"
    assert remaining == 9


@pytest.mark.asyncio
async def test_service_rejects_invalid_key() -> None:
    with pytest.raises(UnauthorizedError):
        await _service().complete("bad", "hello", 256)


@pytest.mark.asyncio
async def test_service_enforces_rate_limit() -> None:
    service = _service(limit=1)
    await service.complete("k1", "hello", 256)
    with pytest.raises(RateLimitExceededError):
        await service.complete("k1", "hello", 256)
