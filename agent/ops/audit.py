from __future__ import annotations
import json
import time
from pathlib import Path
from typing import Any

AUDIT_FILE = Path("logs/audit.jsonl")

def log(event: str, data: dict[str, Any]) -> None:
    AUDIT_FILE.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "ts_ms": int(time.time() * 1000),
        "event": event,
        "data": data,
    }
    with AUDIT_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
