import logging

logger = logging.getLogger(__name__)


def build_pipeline_spec(model_name: str, eval_threshold: float) -> dict[str, object]:
    return {
        "name": f"{model_name}-pipeline",
        "components": ["train", "evaluate", "register", "deploy"],
        "gate": {"metric": "accuracy", "threshold": eval_threshold},
    }
