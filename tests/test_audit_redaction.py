from __future__ import annotations

import json
from pathlib import Path

from agent.ops.audit import log, redact_sensitive


def test_redact_sensitive_nested_values() -> None:
    payload = {
        "safe": "visible",
        "api_key": "abc123",
        "nested": {
            "private_key": "super-secret",
            "normal": "ok",
        },
        "items": [
            {"token": "bad"},
            {"symbol": "ETH-USD"},
        ],
    }

    redacted = redact_sensitive(payload)

    assert redacted["safe"] == "visible"
    assert redacted["api_key"] == "[REDACTED]"
    assert redacted["nested"]["private_key"] == "[REDACTED]"
    assert redacted["nested"]["normal"] == "ok"
    assert redacted["items"][0]["token"] == "[REDACTED]"
    assert redacted["items"][1]["symbol"] == "ETH-USD"


def test_audit_log_redacts_sensitive_values(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)

    log(
        "test_event",
        {
            "api_key": "abc123",
            "payload": {
                "symbol": "ETH-USD",
                "mnemonic": "never log this",
            },
        },
    )

    lines = Path("logs/audit.jsonl").read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1

    record = json.loads(lines[0])

    assert record["event"] == "test_event"
    assert record["data"]["api_key"] == "[REDACTED]"
    assert record["data"]["payload"]["symbol"] == "ETH-USD"
    assert record["data"]["payload"]["mnemonic"] == "[REDACTED]"
