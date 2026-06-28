import logging
from typing import Protocol

from inference.errors import SecretNotFoundError

logger = logging.getLogger(__name__)


class SecretReader(Protocol):
    def read(self, path: str) -> dict[str, str]: ...


class VaultClient:
    def __init__(self, reader: SecretReader) -> None:
        self._reader = reader

    def read_secret(self, path: str, key: str) -> str:
        data = self._reader.read(path)
        if key not in data:
            raise SecretNotFoundError(f"key '{key}' missing at '{path}'")
        return data[key]
