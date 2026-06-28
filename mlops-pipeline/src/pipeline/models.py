from dataclasses import dataclass


@dataclass(frozen=True)
class Dataset:
    features: list[list[float]]
    labels: list[int]

    def __post_init__(self) -> None:
        if len(self.features) != len(self.labels):
            raise ValueError("features and labels length mismatch")


@dataclass(frozen=True)
class EvaluationReport:
    accuracy: float
    f1: float
    n_train: int
    n_test: int
