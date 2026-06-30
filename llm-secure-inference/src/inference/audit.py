import hashlib
import logging
from typing import Protocol

logger = logging.getLogger(__name__)


class AuditLogger(Protocol):
    def record(self, api_key: str, prompt: str, tokens: int) -> None: ...


class LoggingAuditLogger:
    def record(self, api_key: str, prompt: str, tokens: int) -> None:
        logger.info(
            "audit key=%s prompt_len=%d tokens=%d prompt_hash=%s",
            _mask(api_key), len(prompt), tokens, _hash(prompt),
        )


def _mask(api_key: str) -> str:
    if len(api_key) <= 4:
        return "***"
    return f"{api_key[:4]}***"


def _hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]
