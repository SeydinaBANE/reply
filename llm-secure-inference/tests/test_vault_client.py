from pathlib import Path

import pytest
from hvac import exceptions as hvac_exc

import inference.vault_client as vc
from inference.errors import SecretNotFoundError
from inference.vault_client import KubernetesAuthReader, VaultClient


class _FakeReader:
    def __init__(self, data: dict[str, str]) -> None:
        self._data = data

    def read(self, path: str) -> dict[str, str]:
        return self._data

    def health(self) -> None:
        return None


def test_read_secret_returns_value() -> None:
    client = VaultClient(_FakeReader({"api_key": "abc"}))
    assert client.read_secret("secret/data/llm", "api_key") == "abc"


def test_vault_missing_secret_raises() -> None:
    client = VaultClient(_FakeReader({}))
    with pytest.raises(SecretNotFoundError):
        client.read_secret("secret/data/llm", "api_key")


class _FakeKv2:
    def __init__(self, payload: dict[str, str] | None, error: Exception | None) -> None:
        self._payload = payload
        self._error = error

    def read_secret_version(self, path: str, raise_on_deleted_version: bool) -> object:
        if self._error is not None:
            raise self._error
        return {"data": {"data": self._payload}}


def _fake_client_factory(
    payload: dict[str, str] | None = None, error: Exception | None = None
) -> type:
    kv2 = _FakeKv2(payload, error)
    login_calls: list[tuple[str, str]] = []

    class _Kv:
        v2 = kv2

    class _Secrets:
        kv = _Kv()

    class _Kubernetes:
        def login(self, role: str, jwt: str) -> None:
            login_calls.append((role, jwt))

    class _Auth:
        kubernetes = _Kubernetes()

    class _Client:
        def __init__(self, url: str, token: str | None = None) -> None:
            self.url = url
            self.token = token
            self.secrets = _Secrets()
            self.auth = _Auth()

    _Client.login_calls = login_calls
    return _Client


def test_kubernetes_reader_logs_in_and_reads(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    jwt = tmp_path / "token"
    jwt.write_text("jwt-123")
    fake = _fake_client_factory(payload={"api_keys": "a,b"})
    monkeypatch.setattr(vc.hvac, "Client", fake)
    reader = KubernetesAuthReader("http://vault", "llm-role", str(jwt))
    assert reader.read("secret/data/llm") == {"api_keys": "a,b"}
    assert fake.login_calls == [("llm-role", "jwt-123")]


def test_reader_maps_invalid_path_to_not_found(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    jwt = tmp_path / "token"
    jwt.write_text("jwt-123")
    fake = _fake_client_factory(error=hvac_exc.InvalidPath("nope"))
    monkeypatch.setattr(vc.hvac, "Client", fake)
    reader = KubernetesAuthReader("http://vault", "llm-role", str(jwt))
    with pytest.raises(SecretNotFoundError):
        reader.read("secret/data/llm")
