import logging
from pathlib import Path

from pipeline.evaluation import enforce_gate
from pipeline.models import Dataset, EvaluationReport
from pipeline.registry import ArtifactRegistry
from pipeline.train import save_model, train_model
from pipeline.tracker import ExperimentTracker

logger = logging.getLogger(__name__)


def run_pipeline(
    dataset: Dataset,
    tracker: ExperimentTracker,
    registry: ArtifactRegistry,
    model_name: str,
    model_path: Path,
    threshold: float,
) -> EvaluationReport:
    model, report = train_model(dataset)
    tracker.log_metrics({"accuracy": report.accuracy, "f1": report.f1})
    save_model(model, model_path)
    tracker.log_artifact(model_path)
    registry.push(model_path, f"{model_name}.joblib")
    enforce_gate(report, threshold)
    return report
