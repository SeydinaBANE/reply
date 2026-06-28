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


class HvacSecretReader:
    def __init__(self, addr: str, token: str) -> None:
        self._addr = addr
        self._token = token

    def read(self, path: str) -> dict[str, str]:
        try:
            import hvac

            client = hvac.Client(url=self._addr, token=self._token)
            secret = client.secrets.kv.v2.read_secret_version(path=path)
            data = secret["data"]["data"]
        except Exception as exc:
            raise SecretNotFoundError(str(exc)) from exc
        return {str(key): str(value) for key, value in data.items()}
