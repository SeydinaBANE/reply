import argparse
import logging
from pathlib import Path

from pipeline.config import load_settings
from pipeline.dataset import load_dataset
from pipeline.registry import ArtifactRegistry
from pipeline.runner import run_pipeline
from pipeline.tracker import MlflowTracker

logger = logging.getLogger(__name__)


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(description="Train, track, register and gate a model")
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--label-column", default="label")
    parser.add_argument("--model-path", type=Path, default=Path("models/model.joblib"))
    args = parser.parse_args()

    settings = load_settings()
    dataset = load_dataset(args.data, args.label_column)
    tracker = MlflowTracker(settings.mlflow_tracking_uri, settings.model_name)
    registry = ArtifactRegistry(settings.jfrog_url, settings.jfrog_repo, settings.jfrog_token)

    report = run_pipeline(
        dataset=dataset,
        tracker=tracker,
        registry=registry,
        model_name=settings.model_name,
        model_path=args.model_path,
        threshold=settings.eval_threshold,
        seed=settings.train_seed,
    )
    logger.info("pipeline finished accuracy=%.4f f1=%.4f", report.accuracy, report.f1)


if __name__ == "__main__":
    main()
