from __future__ import annotations

import json
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_RISK_POLICY_PATH = PROJECT_ROOT / "config/risk_policy.example.json"


@dataclass(frozen=True)
class RiskPolicy:
    version: int
    mode: str
    allowed_symbols: frozenset[str]
    max_qty_by_symbol: dict[str, Decimal]
    allowed_intents: frozenset[str]
    allowed_sides: frozenset[str]
    require_manual_approval: bool
    require_price: bool
    live_trading_enabled: bool


def load_risk_policy(path: Path = DEFAULT_RISK_POLICY_PATH) -> RiskPolicy:
    raw = json.loads(path.read_text(encoding="utf-8"))

    allowed_symbols = frozenset(str(symbol) for symbol in raw["allowed_symbols"])
    allowed_intents = frozenset(str(intent) for intent in raw["allowed_intents"])
    allowed_sides = frozenset(str(side) for side in raw["allowed_sides"])

    max_qty_by_symbol = {
        str(symbol): Decimal(str(qty))
        for symbol, qty in raw["max_qty_by_symbol"].items()
    }

    policy = RiskPolicy(
        version=int(raw["version"]),
        mode=str(raw["mode"]),
        allowed_symbols=allowed_symbols,
        max_qty_by_symbol=max_qty_by_symbol,
        allowed_intents=allowed_intents,
        allowed_sides=allowed_sides,
        require_manual_approval=bool(raw["require_manual_approval"]),
        require_price=bool(raw["require_price"]),
        live_trading_enabled=bool(raw["live_trading_enabled"]),
    )

    validate_risk_policy(policy)
    return policy


def validate_risk_policy(policy: RiskPolicy) -> None:
    if policy.version != 1:
        raise ValueError("unsupported risk policy version")

    if policy.mode != "dry_run_only":
        raise ValueError("risk policy must remain dry_run_only")

    if policy.live_trading_enabled:
        raise ValueError("live trading must be disabled")

    if not policy.require_manual_approval:
        raise ValueError("manual approval must be required")

    if not policy.require_price:
        raise ValueError("price must be required")

    if not policy.allowed_symbols:
        raise ValueError("at least one allowed symbol is required")

    if "DRY_RUN_ORDER" not in policy.allowed_intents:
        raise ValueError("DRY_RUN_ORDER intent must be allowed")

    if policy.allowed_sides != frozenset({"buy", "sell"}):
        raise ValueError("allowed sides must be exactly buy and sell")

    for symbol in policy.allowed_symbols:
        if symbol not in policy.max_qty_by_symbol:
            raise ValueError(f"missing max quantity for symbol: {symbol}")

        max_qty = policy.max_qty_by_symbol[symbol]
        if max_qty <= Decimal("0"):
            raise ValueError(f"max quantity must be positive for symbol: {symbol}")
