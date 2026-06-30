import logging
from collections.abc import Iterator
from contextlib import contextmanager, nullcontext
from contextlib import AbstractContextManager
from pathlib import Path
from typing import Protocol

import mlflow
from mlflow.models import infer_signature

logger = logging.getLogger(__name__)


class ExperimentTracker(Protocol):
    def run(self, tags: dict[str, str]) -> AbstractContextManager[None]: ...

    def log_params(self, params: dict[str, object]) -> None: ...

    def log_metrics(self, metrics: dict[str, float]) -> None: ...

    def log_artifact(self, path: Path) -> None: ...

    def log_model(self, model: object, name: str, sample: list[list[float]]) -> None: ...


class NoOpTracker:
    def run(self, tags: dict[str, str]) -> AbstractContextManager[None]:
        logger.debug("noop run %s", tags)
        return nullcontext()

    def log_params(self, params: dict[str, object]) -> None:
        logger.debug("noop log_params %s", params)

    def log_metrics(self, metrics: dict[str, float]) -> None:
        logger.debug("noop log_metrics %s", metrics)

    def log_artifact(self, path: Path) -> None:
        logger.debug("noop log_artifact %s", path)

    def log_model(self, model: object, name: str, sample: list[list[float]]) -> None:
        logger.debug("noop log_model %s", name)


class MlflowTracker:
    def __init__(self, tracking_uri: str, experiment: str) -> None:
        mlflow.set_tracking_uri(tracking_uri)
        mlflow.set_experiment(experiment)

    @contextmanager
    def run(self, tags: dict[str, str]) -> Iterator[None]:
        with mlflow.start_run(tags=tags):
            yield

    def log_params(self, params: dict[str, object]) -> None:
        mlflow.log_params(params)

    def log_metrics(self, metrics: dict[str, float]) -> None:
        mlflow.log_metrics(metrics)

    def log_artifact(self, path: Path) -> None:
        mlflow.log_artifact(str(path))

    def log_model(self, model: object, name: str, sample: list[list[float]]) -> None:
        predictions = model.predict(sample)  # type: ignore[attr-defined]
        signature = infer_signature(sample, predictions)
        mlflow.sklearn.log_model(model, name, signature=signature)
