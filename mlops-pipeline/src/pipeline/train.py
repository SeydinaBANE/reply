import logging
from pathlib import Path

import joblib
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from pipeline.models import Dataset, EvaluationReport

logger = logging.getLogger(__name__)


def train_model(dataset: Dataset, test_size: float = 0.2, seed: int | None = None) -> tuple[object, EvaluationReport]:
    x_train, x_test, y_train, y_test = train_test_split(
        dataset.features, dataset.labels, test_size=test_size, random_state=seed
    )
    model = make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000))
    model.fit(x_train, y_train)

    predictions = model.predict(x_test)
    report = EvaluationReport(
        accuracy=float(accuracy_score(y_test, predictions)),
        f1=float(f1_score(y_test, predictions, average="binary", zero_division=0.0)),
        n_train=len(x_train),
        n_test=len(x_test),
    )
    logger.info("trained model accuracy=%.4f f1=%.4f", report.accuracy, report.f1)
    return model, report


def save_model(model: object, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, path)
    logger.info("saved model to %s", path)
