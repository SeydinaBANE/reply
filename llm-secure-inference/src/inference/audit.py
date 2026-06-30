import json
import logging
from datetime import datetime, timezone
from typing import Protocol

logger = logging.getLogger("inference.audit")


class AuditLogger(Protocol):
    def record(self, api_key: str, prompt: str, tokens: int) -> None: ...


class LoggingAuditLogger:
    def record(self, api_key: str, prompt: str, tokens: int) -> None:
        event = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "event": "completion",
            "api_key": _mask(api_key),
            "prompt_len": len(prompt),
            "tokens": tokens,
        }
        logger.info(json.dumps(event, separators=(",", ":"), sort_keys=True))


def _mask(api_key: str) -> str:
    if len(api_key) <= 4:
        return "***"
    return f"{api_key[:4]}***"
