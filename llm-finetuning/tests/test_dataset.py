import json
from pathlib import Path

import pytest

from finetune.dataset import load_jsonl
from finetune.errors import InvalidDatasetError


def test_load_jsonl_parses_records(tmp_path: Path) -> None:
    path = tmp_path / "data.jsonl"
    lines = [
        json.dumps({"instruction": "q1", "response": "a1"}),
        json.dumps({"instruction": "q2", "response": "a2"}),
    ]
    path.write_text("\n".join(lines), encoding="utf-8")
    examples = load_jsonl(path)
    assert [example.instruction for example in examples] == ["q1", "q2"]


def test_load_jsonl_missing_field_raises(tmp_path: Path) -> None:
    path = tmp_path / "data.jsonl"
    path.write_text(json.dumps({"instruction": "q1"}), encoding="utf-8")
    with pytest.raises(InvalidDatasetError):
        load_jsonl(path)


def test_load_jsonl_missing_file_raises(tmp_path: Path) -> None:
    with pytest.raises(InvalidDatasetError):
        load_jsonl(tmp_path / "missing.jsonl")
