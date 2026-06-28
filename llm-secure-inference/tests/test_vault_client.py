import pytest

from inference.errors import SecretNotFoundError
from inference.vault_client import VaultClient


class _FakeReader:
    def __init__(self, data: dict[str, str]) -> None:
        self._data = data

    def read(self, path: str) -> dict[str, str]:
        return self._data


def test_read_secret_returns_value() -> None:
    client = VaultClient(_FakeReader({"api_key": "abc"}))
    assert client.read_secret("secret/data/llm", "api_key") == "abc"


def test_vault_missing_secret_raises() -> None:
    client = VaultClient(_FakeReader({}))
    with pytest.raises(SecretNotFoundError):
        client.read_secret("secret/data/llm", "api_key")
