from __future__ import annotations
import json
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

STATE_FILE = Path("logs/state.json")
LOCK_FILE = Path("logs/state.json.lock")

_MAX_EXECUTED_IDS = 2000
_STALE_LOCK_SECONDS = 30.0

@dataclass
class AgentState:
    equity_usd: float = 1000.0
    daily_pnl_usd: float = 0.0
    day_key: str = ""
    last_trade_ts_ms_by_symbol: dict[str, int] | None = None
    executed_proposal_ids: list[str] | None = None  # idempotency (bounded)

    def __post_init__(self) -> None:
        if self.last_trade_ts_ms_by_symbol is None:
            self.last_trade_ts_ms_by_symbol = {}
        if self.executed_proposal_ids is None:
            self.executed_proposal_ids = []

def _today_key() -> str:
    return time.strftime("%Y-%m-%d", time.gmtime())

class _FileLock:
    """Dependency-free lock using exclusive create; includes stale-lock recovery."""
    def __init__(self, path: Path, timeout_s: float = 2.0, poll_s: float = 0.05):
        self.path = path
        self.timeout_s = timeout_s
        self.poll_s = poll_s
        self._fd: int | None = None

    def __enter__(self) -> "_FileLock":
        self.path.parent.mkdir(parents=True, exist_ok=True)
        deadline = time.time() + self.timeout_s
        while True:
            try:
                self._fd = os.open(str(self.path), os.O_CREAT | os.O_EXCL | os.O_RDWR)
                os.write(self._fd, str(os.getpid()).encode("utf-8"))
                return self
            except FileExistsError:
                # Stale lock recovery
                try:
                    age = time.time() - self.path.stat().st_mtime
                    if age > _STALE_LOCK_SECONDS:
                        self.path.unlink(missing_ok=True)
                        continue
                except Exception:
                    pass

                if time.time() >= deadline:
                    raise TimeoutError(f"Timed out acquiring state lock: {self.path}")
                time.sleep(self.poll_s)

    def __exit__(self, exc_type, exc, tb) -> None:
        try:
            if self._fd is not None:
                os.close(self._fd)
        finally:
            try:
                self.path.unlink(missing_ok=True)
            except Exception:
                pass

def _state_to_dict(state: AgentState) -> dict[str, Any]:
    return {
        "equity_usd": state.equity_usd,
        "daily_pnl_usd": state.daily_pnl_usd,
        "day_key": state.day_key,
        "last_trade_ts_ms_by_symbol": state.last_trade_ts_ms_by_symbol or {},
        "executed_proposal_ids": (state.executed_proposal_ids or [])[-_MAX_EXECUTED_IDS:],
    }

def _write_state_unlocked(state: AgentState) -> None:
    """Write state atomically. MUST be called only while holding _FileLock."""
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    data = _state_to_dict(state)
    tmp = STATE_FILE.with_suffix(STATE_FILE.suffix + f".tmp.{os.getpid()}")
    tmp.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")
    os.replace(tmp, STATE_FILE)

def save_state(state: AgentState) -> None:
    with _FileLock(LOCK_FILE):
        _write_state_unlocked(state)

def load_state() -> AgentState:
    with _FileLock(LOCK_FILE):
        if not STATE_FILE.exists():
            s = AgentState(day_key=_today_key())
            _write_state_unlocked(s)
            return s

        try:
            raw = STATE_FILE.read_text(encoding="utf-8")
            data = json.loads(raw)
        except Exception as e:
            # Fail closed: corrupted state should block execution until operator fixes it.
            raise RuntimeError(f"State file is unreadable/corrupt: {STATE_FILE}") from e

        s = AgentState(
            equity_usd=float(data.get("equity_usd", 1000.0)),
            daily_pnl_usd=float(data.get("daily_pnl_usd", 0.0)),
            day_key=str(data.get("day_key", _today_key())),
            last_trade_ts_ms_by_symbol=dict(data.get("last_trade_ts_ms_by_symbol", {})),
            executed_proposal_ids=list(data.get("executed_proposal_ids", [])),
        )

        changed = False

        # reset daily pnl if day changed
        if s.day_key != _today_key():
            s.day_key = _today_key()
            s.daily_pnl_usd = 0.0
            changed = True

        # bound executed ids
        if len(s.executed_proposal_ids) > _MAX_EXECUTED_IDS:
            s.executed_proposal_ids = s.executed_proposal_ids[-_MAX_EXECUTED_IDS:]
            changed = True

        if changed:
            _write_state_unlocked(s)

        return s

def mark_executed(state: AgentState, proposal_id: str) -> None:
    ids = state.executed_proposal_ids or []
    if proposal_id in ids:
        return
    ids.append(proposal_id)
    if len(ids) > _MAX_EXECUTED_IDS:
        ids[:] = ids[-_MAX_EXECUTED_IDS:]
    state.executed_proposal_ids = ids
    save_state(state)
    