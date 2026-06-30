import pytest

from inference.auth import ApiKeyAuthenticator, ApiKeyProvider
from inference.errors import SecretNotFoundError, UnauthorizedError


def test_verify_accepts_known_key() -> None:
    ApiKeyAuthenticator(["k1", "k2"]).verify("k1")


def test_verify_rejects_unknown_key() -> None:
    with pytest.raises(UnauthorizedError):
        ApiKeyAuthenticator(["k1"]).verify("nope")


def test_verify_ignores_blank_keys() -> None:
    with pytest.raises(UnauthorizedError):
        ApiKeyAuthenticator(["  ", ""]).verify("")


def test_provider_refreshes_keys_after_ttl() -> None:
    keys = [["k1"], ["k2"]]
    now = [0.0]
    provider = ApiKeyProvider(lambda: keys.pop(0), refresh_s=60.0, clock=lambda: now[0])
    provider.verify("k1")
    now[0] = 61.0
    provider.verify("k2")
    with pytest.raises(UnauthorizedError):
        provider.verify("k1")


def test_provider_keeps_cached_keys_when_loader_fails() -> None:
    state = {"fail": False}

    def loader() -> list[str]:
        if state["fail"]:
            raise SecretNotFoundError("vault down")
        return ["k1"]

    now = [0.0]
    provider = ApiKeyProvider(loader, refresh_s=60.0, clock=lambda: now[0])
    state["fail"] = True
    now[0] = 61.0
    provider.verify("k1")
