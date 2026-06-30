import logging
from collections.abc import Callable
from pathlib import Path
from typing import Protocol, TypeVar

import hvac
from hvac import exceptions as hvac_exc

from inference.errors import SecretNotFoundError, VaultAuthError, VaultUnavailableError

logger = logging.getLogger(__name__)

DEFAULT_JWT_PATH = "/var/run/secrets/kubernetes.io/serviceaccount/token"

T = TypeVar("T")


class SecretReader(Protocol):
    def read(self, path: str) -> dict[str, str]: ...
    def health(self) -> None: ...


class VaultClient:
    def __init__(self, reader: SecretReader) -> None:
        self._reader = reader

    def read_secret(self, path: str, key: str) -> str:
        data = self._reader.read(path)
        if key not in data:
            raise SecretNotFoundError(f"key '{key}' missing at '{path}'")
        return data[key]

    def health(self) -> None:
        self._reader.health()


def _guard(operation: Callable[[], T]) -> T:
    try:
        return operation()
    except hvac_exc.Forbidden as exc:
        raise VaultAuthError(str(exc)) from exc
    except hvac_exc.InvalidPath as exc:
        raise SecretNotFoundError(str(exc)) from exc
    except Exception as exc:
        raise VaultUnavailableError(str(exc)) from exc


def _read_kv2(client: "hvac.Client", path: str) -> dict[str, str]:
    secret = client.secrets.kv.v2.read_secret_version(path=path, raise_on_deleted_version=True)
    data = secret["data"]["data"]
    return {str(key): str(value) for key, value in data.items()}


class HvacSecretReader:
    def __init__(self, addr: str, token: str) -> None:
        self._addr = addr
        self._token = token

    def _client(self) -> "hvac.Client":
        return hvac.Client(url=self._addr, token=self._token)

    def read(self, path: str) -> dict[str, str]:
        return _guard(lambda: _read_kv2(self._client(), path))

    def health(self) -> None:
        _guard(lambda: self._client().sys.read_health_status(method="GET"))


class KubernetesAuthReader:
    def __init__(self, addr: str, role: str, jwt_path: str = DEFAULT_JWT_PATH) -> None:
        self._addr = addr
        self._role = role
        self._jwt_path = jwt_path

    def _client(self) -> "hvac.Client":
        client = hvac.Client(url=self._addr)
        jwt = Path(self._jwt_path).read_text(encoding="utf-8")
        client.auth.kubernetes.login(role=self._role, jwt=jwt)
        return client

    def read(self, path: str) -> dict[str, str]:
        return _guard(lambda: _read_kv2(self._client(), path))

    def health(self) -> None:
        _guard(lambda: self._client().sys.read_health_status(method="GET"))
