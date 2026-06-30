import logging
from dataclasses import asdict, dataclass, field

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Component:
    name: str
    inputs: list[str] = field(default_factory=list)
    outputs: list[str] = field(default_factory=list)
    depends_on: list[str] = field(default_factory=list)


def build_pipeline_spec(model_name: str, eval_threshold: float) -> dict[str, object]:
    train = Component(name="train", inputs=["dataset"], outputs=["model", "metrics"])
    evaluate = Component(
        name="evaluate",
        inputs=["model", "metrics"],
        outputs=["gate_passed"],
        depends_on=["train"],
    )
    register = Component(
        name="register",
        inputs=["model", "gate_passed"],
        outputs=["model_uri"],
        depends_on=["evaluate"],
    )
    deploy = Component(
        name="deploy",
        inputs=["model_uri"],
        outputs=["endpoint"],
        depends_on=["register"],
    )
    components = [train, evaluate, register, deploy]
    _validate_dag(components)
    return {
        "name": f"{model_name}-pipeline",
        "components": [asdict(component) for component in components],
        "gate": {"metric": "accuracy", "threshold": eval_threshold},
    }


def _validate_dag(components: list[Component]) -> None:
    names = {component.name for component in components}
    for component in components:
        missing = [dep for dep in component.depends_on if dep not in names]
        if missing:
            raise ValueError(f"{component.name} depends on unknown components: {missing}")
