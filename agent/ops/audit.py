from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any


AUDIT_FILE = Path("logs/audit.jsonl")

SENSITIVE_KEY_FRAGMENTS = (
    "api_key",
    "apikey",
    "secret",
    "token",
    "password",
    "passwd",
    "private_key",
    "privatekey",
    "mnemonic",
    "seed",
    "bearer",
    "authorization",
    "auth",
)


def _is_sensitive_key(key: str) -> bool:
    lowered = key.lower()
    return any(fragment in lowered for fragment in SENSITIVE_KEY_FRAGMENTS)


def redact_sensitive(value: Any) -> Any:
    if isinstance(value, dict):
        redacted: dict[str, Any] = {}

        for key, item in value.items():
            key_str = str(key)

            if _is_sensitive_key(key_str):
                redacted[key_str] = "[REDACTED]"
            else:
                redacted[key_str] = redact_sensitive(item)

        return redacted

    if isinstance(value, list):
        return [redact_sensitive(item) for item in value]

    if isinstance(value, tuple):
        return [redact_sensitive(item) for item in value]

    return value


def log(event: str, data: dict[str, Any] | None = None) -> None:
    AUDIT_FILE.parent.mkdir(parents=True, exist_ok=True)

    safe_data = redact_sensitive(data or {})

    record = {
        "ts_ms": int(time.time() * 1000),
        "event": str(event),
        "data": safe_data,
    }

    with AUDIT_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, sort_keys=True, default=str) + "\n")
