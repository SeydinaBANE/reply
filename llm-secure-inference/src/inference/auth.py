import hashlib
import hmac
from collections.abc import Iterable

from inference.errors import UnauthorizedError


def _digest(api_key: str) -> str:
    return hashlib.sha256(api_key.encode("utf-8")).hexdigest()


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
