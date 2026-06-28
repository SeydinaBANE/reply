from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from pipeline.errors import RegistryError
from pipeline.registry import ArtifactRegistry


def _registry() -> ArtifactRegistry:
    return ArtifactRegistry("https://example.com/artifactory", "ml-models", "token")


def test_push_missing_artifact_raises(tmp_path: Path) -> None:
    with pytest.raises(RegistryError):
        _registry().push(tmp_path / "missing.joblib", "model.joblib")


def test_push_returns_url(tmp_path: Path) -> None:
    artifact = tmp_path / "model.joblib"
    artifact.write_bytes(b"payload")
    with patch("pipeline.registry.requests.put", return_value=MagicMock(status_code=201)):
        url = _registry().push(artifact, "model.joblib")
    assert url.endswith("ml-models/model.joblib")


def test_pull_writes_file(tmp_path: Path) -> None:
    response = MagicMock(status_code=200, content=b"data")
    with patch("pipeline.registry.requests.get", return_value=response):
        dest = _registry().pull("model.joblib", tmp_path / "out.joblib")
    assert dest.read_bytes() == b"data"


def test_pull_error_status_raises(tmp_path: Path) -> None:
    response = MagicMock(status_code=404, text="not found")
    with patch("pipeline.registry.requests.get", return_value=response):
        with pytest.raises(RegistryError):
            _registry().pull("model.joblib", tmp_path / "out.joblib")
