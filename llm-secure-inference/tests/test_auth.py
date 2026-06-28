import pytest

from inference.auth import ApiKeyAuthenticator
from inference.errors import UnauthorizedError


def test_verify_accepts_known_key() -> None:
    ApiKeyAuthenticator(["k1", "k2"]).verify("k1")


def test_verify_rejects_unknown_key() -> None:
    with pytest.raises(UnauthorizedError):
        ApiKeyAuthenticator(["k1"]).verify("nope")


def test_verify_ignores_blank_keys() -> None:
    with pytest.raises(UnauthorizedError):
        ApiKeyAuthenticator(["  ", ""]).verify("")
