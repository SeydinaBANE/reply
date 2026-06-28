import logging
from pathlib import Path
from typing import Protocol

import mlflow

logger = logging.getLogger(__name__)


class ExperimentTracker(Protocol):
    def log_params(self, params: dict[str, object]) -> None: ...

    def log_metrics(self, metrics: dict[str, float]) -> None: ...

    def log_artifact(self, path: Path) -> None: ...


class NoOpTracker:
    def log_params(self, params: dict[str, object]) -> None:
        logger.debug("noop log_params %s", params)

    def log_metrics(self, metrics: dict[str, float]) -> None:
        logger.debug("noop log_metrics %s", metrics)

    def log_artifact(self, path: Path) -> None:
        logger.debug("noop log_artifact %s", path)


class MlflowTracker:
    def __init__(self, tracking_uri: str, experiment: str) -> None:
        mlflow.set_tracking_uri(tracking_uri)
        mlflow.set_experiment(experiment)

    def log_params(self, params: dict[str, object]) -> None:
        mlflow.log_params(params)

    def log_metrics(self, metrics: dict[str, float]) -> None:
        mlflow.log_metrics(metrics)

    def log_artifact(self, path: Path) -> None:
        mlflow.log_artifact(str(path))
