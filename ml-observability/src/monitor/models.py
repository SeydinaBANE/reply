from dataclasses import dataclass
from enum import Enum


class AlertLevel(str, Enum):
    OK = "ok"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass(frozen=True)
class DriftResult:
    psi: float
    level: AlertLevel
