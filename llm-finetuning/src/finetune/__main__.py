import argparse
import logging
from pathlib import Path

from finetune.config import load_settings
from finetune.dataset import load_jsonl
from finetune.generator import VertexTextGenerator
from finetune.runner import run_evaluation

logger = logging.getLogger(__name__)


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(description="Evaluate a fine-tuned model against a baseline")
    parser.add_argument("--eval-data", type=Path, required=True)
    parser.add_argument("--report", type=Path, default=Path("eval_report.json"))
    args = parser.parse_args()

    settings = load_settings()
    examples = load_jsonl(args.eval_data)
    generator = VertexTextGenerator(
        settings.vertex_project, settings.vertex_location, settings.base_model
    )
    report = run_evaluation(generator, examples, settings.eval_baseline, args.report)
    logger.info("evaluation finished exact_match=%.4f", report.exact_match)


if __name__ == "__main__":
    main()
