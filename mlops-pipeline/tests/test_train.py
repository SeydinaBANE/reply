from pathlib import Path

import pytest

from pipeline.errors import RegistryError
from pipeline.registry import ArtifactRegistry
from pipeline.train import train_model


def test_train_model_returns_metrics() -> None:
    features = [[float(i)] for i in range(20)]
    labels = [i % 2 for i in range(20)]
    result = train_model(features, labels, seed=0)
    assert 0.0 <= result.accuracy <= 1.0
    assert result.n_train + result.n_test == 20


def test_registry_push_missing_artifact_raises(tmp_path: Path) -> None:
    registry = ArtifactRegistry("https://example.com", "repo", "token")
    with pytest.raises(RegistryError):
        registry.push(tmp_path / "missing.pkl", "model.pkl")
