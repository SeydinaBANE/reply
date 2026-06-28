from collections.abc import Iterable

from inference.errors import UnauthorizedError


class ApiKeyAuthenticator:
    def __init__(self, allowed_keys: Iterable[str]) -> None:
        self._allowed = frozenset(key.strip() for key in allowed_keys if key.strip())

    def verify(self, api_key: str) -> None:
        if api_key not in self._allowed:
            raise UnauthorizedError("invalid api key")
