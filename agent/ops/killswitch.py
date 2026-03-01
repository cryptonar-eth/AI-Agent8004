from __future__ import annotations
from pathlib import Path

KILLSWITCH_FILE = Path("approvals/KILL_SWITCH")

def is_killed() -> bool:
    return KILLSWITCH_FILE.exists()

def kill(reason: str = "") -> None:
    KILLSWITCH_FILE.parent.mkdir(parents=True, exist_ok=True)
    KILLSWITCH_FILE.write_text(reason or "killed")

def revive() -> None:
    if KILLSWITCH_FILE.exists():
        KILLSWITCH_FILE.unlink()
