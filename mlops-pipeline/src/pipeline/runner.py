import logging
from pathlib import Path

from pipeline.dataset import hash_dataset
from pipeline.evaluation import enforce_gate
from pipeline.models import Dataset, EvaluationReport
from pipeline.registry import ArtifactRegistry
from pipeline.train import save_model, train_model
from pipeline.tracker import ExperimentTracker

logger = logging.getLogger(__name__)

_SIGNATURE_SAMPLE = 5


def run_pipeline(
    dataset: Dataset,
    tracker: ExperimentTracker,
    registry: ArtifactRegistry,
    model_name: str,
    model_path: Path,
    threshold: float,
    baseline: float | None = None,
    tolerance: float = 0.0,
    seed: int = 42,
    test_size: float = 0.2,
) -> EvaluationReport:
    dataset_hash = hash_dataset(dataset)
    tags = {"model_name": model_name, "dataset_hash": dataset_hash}
    with tracker.run(tags):
        model, report = train_model(dataset, test_size=test_size, seed=seed)
        tracker.log_params(
            {
                "model_name": model_name,
                "seed": seed,
                "test_size": test_size,
                "threshold": threshold,
                "dataset_hash": dataset_hash,
                "n_samples": len(dataset.labels),
            }
        )
        tracker.log_metrics({"accuracy": report.accuracy, "f1": report.f1})

        enforce_gate(report, threshold, baseline=baseline, tolerance=tolerance)

        save_model(model, model_path)
        tracker.log_artifact(model_path)
        tracker.log_model(model, model_name, dataset.features[:_SIGNATURE_SAMPLE])
        registry.push(model_path, f"{model_name}.joblib")
    return report
