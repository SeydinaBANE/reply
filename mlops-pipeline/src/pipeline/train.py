import logging
from dataclasses import dataclass

from sklearn.dummy import DummyClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class TrainingResult:
    accuracy: float
    n_train: int
    n_test: int


def train_model(
    features: list[list[float]],
    labels: list[int],
    test_size: float = 0.2,
    seed: int = 42,
) -> TrainingResult:
    x_train, x_test, y_train, y_test = train_test_split(
        features, labels, test_size=test_size, random_state=seed
    )
    model = DummyClassifier(strategy="most_frequent")
    model.fit(x_train, y_train)
    accuracy = float(accuracy_score(y_test, model.predict(x_test)))
    logger.info("trained model accuracy=%.4f", accuracy)
    return TrainingResult(accuracy=accuracy, n_train=len(x_train), n_test=len(x_test))
