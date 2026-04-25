from __future__ import annotations

import json
from decimal import Decimal
from pathlib import Path

import pytest

from agent.config.risk_policy import load_risk_policy


def _write_policy(tmp_path: Path, data: dict) -> Path:
    path = tmp_path / "risk_policy.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


def _valid_policy() -> dict:
    return {
        "version": 1,
        "mode": "dry_run_only",
        "allowed_symbols": ["ETH-USD"],
        "max_qty_by_symbol": {"ETH-USD": "0.01"},
        "allowed_intents": ["DRY_RUN_ORDER"],
        "require_manual_approval": True,
        "require_price": True,
        "live_trading_enabled": False,
    }


def test_load_default_risk_policy() -> None:
    policy = load_risk_policy()

    assert policy.version == 1
    assert policy.mode == "dry_run_only"
    assert policy.allowed_symbols == frozenset({"ETH-USD"})
    assert policy.max_qty_by_symbol["ETH-USD"] == Decimal("0.01")
    assert policy.require_manual_approval is True
    assert policy.live_trading_enabled is False


def test_policy_rejects_live_trading_enabled(tmp_path: Path) -> None:
    data = _valid_policy()
    data["live_trading_enabled"] = True

    with pytest.raises(ValueError, match="live trading"):
        load_risk_policy(_write_policy(tmp_path, data))


def test_policy_rejects_missing_manual_approval(tmp_path: Path) -> None:
    data = _valid_policy()
    data["require_manual_approval"] = False

    with pytest.raises(ValueError, match="manual approval"):
        load_risk_policy(_write_policy(tmp_path, data))


def test_policy_rejects_non_positive_max_qty(tmp_path: Path) -> None:
    data = _valid_policy()
    data["max_qty_by_symbol"]["ETH-USD"] = "0"

    with pytest.raises(ValueError, match="positive"):
        load_risk_policy(_write_policy(tmp_path, data))


def test_policy_rejects_missing_dry_run_intent(tmp_path: Path) -> None:
    data = _valid_policy()
    data["allowed_intents"] = []

    with pytest.raises(ValueError, match="DRY_RUN_ORDER"):
        load_risk_policy(_write_policy(tmp_path, data))
