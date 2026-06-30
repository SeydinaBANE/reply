import logging

from inference.audit import AuditLogger
from inference.auth import KeyVerifier
from inference.backend import Completion, LlmBackend
from inference.ratelimit import RateLimiter

logger = logging.getLogger(__name__)


class InferenceService:
    def __init__(
        self,
        authenticator: KeyVerifier,
        limiter: RateLimiter,
        backend: LlmBackend,
        audit: AuditLogger,
    ) -> None:
        self._authenticator = authenticator
        self._limiter = limiter
        self._backend = backend
        self._audit = audit

    async def complete(
        self, api_key: str, prompt: str, max_tokens: int
    ) -> tuple[Completion, int]:
        self._authenticator.verify(api_key)
        remaining = await self._limiter.check(api_key)
        completion = await self._backend.complete(prompt, max_tokens)
        self._audit.record(api_key, prompt, completion.tokens)
        return completion, remaining
