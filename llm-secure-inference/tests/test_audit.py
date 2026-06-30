import json
import logging

import pytest

from inference.audit import LoggingAuditLogger


def test_record_emits_structured_json(caplog: pytest.LogCaptureFixture) -> None:
    with caplog.at_level(logging.INFO, logger="inference.audit"):
        LoggingAuditLogger().record("supersecretkey", "hello world", 2)
    event = json.loads(caplog.records[-1].message)
    assert event["event"] == "completion"
    assert event["prompt_len"] == 11
    assert event["tokens"] == 2


def test_record_masks_api_key(caplog: pytest.LogCaptureFixture) -> None:
    with caplog.at_level(logging.INFO, logger="inference.audit"):
        LoggingAuditLogger().record("supersecretkey", "hi", 1)
    event = json.loads(caplog.records[-1].message)
    assert event["api_key"] == "supe***"
    assert "secret" not in event["api_key"]
