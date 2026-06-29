from collections.abc import Iterator
from pathlib import Path
from unittest.mock import patch

import pytest

from pipeline.errors import RegistryError
from pipeline.registry import ArtifactRegistry


class _FakeResponse:
    def __init__(self, status_code: int, content: bytes = b"", text: str = "") -> None:
        self.status_code = status_code
        self._content = content
        self.text = text

    def __enter__(self) -> "_FakeResponse":
        return self

    def __exit__(self, *args: object) -> bool:
        return False

    def iter_content(self, chunk_size: int) -> Iterator[bytes]:
        yield self._content


def _registry() -> ArtifactRegistry:
    return ArtifactRegistry(
        "https://example.com/artifactory", "ml-models", "token", backoff_base=0.0, max_attempts=3
    )


def test_push_missing_artifact_raises(tmp_path: Path) -> None:
    with pytest.raises(RegistryError):
        _registry().push(tmp_path / "missing.joblib", "model.joblib")


def test_push_returns_url(tmp_path: Path) -> None:
    artifact = tmp_path / "model.joblib"
    artifact.write_bytes(b"payload")
    with patch("pipeline.registry.requests.put", return_value=_FakeResponse(201)):
        url = _registry().push(artifact, "model.joblib")
    assert url.endswith("ml-models/model.joblib")


def test_push_retries_on_server_error(tmp_path: Path) -> None:
    artifact = tmp_path / "model.joblib"
    artifact.write_bytes(b"payload")
    responses = [_FakeResponse(503, text="busy"), _FakeResponse(201)]
    with patch("pipeline.registry.requests.put", side_effect=responses) as put:
        url = _registry().push(artifact, "model.joblib")
    assert put.call_count == 2
    assert url.endswith("ml-models/model.joblib")


def test_push_does_not_retry_on_client_error(tmp_path: Path) -> None:
    artifact = tmp_path / "model.joblib"
    artifact.write_bytes(b"payload")
    with patch("pipeline.registry.requests.put", return_value=_FakeResponse(400, text="bad")) as put:
        with pytest.raises(RegistryError):
            _registry().push(artifact, "model.joblib")
    assert put.call_count == 1


def test_pull_writes_file(tmp_path: Path) -> None:
    with patch("pipeline.registry.requests.get", return_value=_FakeResponse(200, content=b"data")):
        dest = _registry().pull("model.joblib", tmp_path / "out.joblib")
    assert dest.read_bytes() == b"data"


def test_pull_error_status_raises(tmp_path: Path) -> None:
    with patch("pipeline.registry.requests.get", return_value=_FakeResponse(404, text="not found")):
        with pytest.raises(RegistryError):
            _registry().pull("model.joblib", tmp_path / "out.joblib")
