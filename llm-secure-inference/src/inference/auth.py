import hashlib
import hmac
import logging
import time
from collections.abc import Callable, Iterable
from typing import Protocol

from inference.errors import InferenceError, UnauthorizedError

logger = logging.getLogger(__name__)


def _digest(api_key: str) -> str:
    return hashlib.sha256(api_key.encode("utf-8")).hexdigest()


class KeyVerifier(Protocol):
    def verify(self, api_key: str) -> None: ...


class ApiKeyAuthenticator:
    def __init__(self, allowed_keys: Iterable[str]) -> None:
        self._allowed = tuple(_digest(key.strip()) for key in allowed_keys if key.strip())

    def verify(self, api_key: str) -> None:
        candidate = _digest(api_key)
        matched = False
        for allowed in self._allowed:
            if hmac.compare_digest(candidate, allowed):
                matched = True
        if not matched:
            raise UnauthorizedError("invalid api key")


class ApiKeyProvider:
    def __init__(
        self,
        loader: Callable[[], Iterable[str]],
        refresh_s: float,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self._loader = loader
        self._refresh_s = refresh_s
        self._clock = clock
        self._authenticator = ApiKeyAuthenticator(loader())
        self._loaded_at = clock()

    def verify(self, api_key: str) -> None:
        self._maybe_refresh()
        self._authenticator.verify(api_key)

    def _maybe_refresh(self) -> None:
        now = self._clock()
        if now - self._loaded_at < self._refresh_s:
            return
        self._loaded_at = now
        try:
            self._authenticator = ApiKeyAuthenticator(self._loader())
        except InferenceError as exc:
            logger.warning("api key refresh failed, keeping cached keys: %s", exc)
