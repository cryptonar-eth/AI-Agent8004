from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class GovernanceRules:
    allowed_symbols: set[str]
    max_qty_per_trade: float
    enabled: bool = True

DEFAULT_RULES = GovernanceRules(
    allowed_symbols={"ETH-USD"},
    max_qty_per_trade=0.01,
    enabled=True,
)

def check_trade(symbol: str, qty: float, rules: GovernanceRules = DEFAULT_RULES) -> tuple[bool, str]:
    if not rules.enabled:
        return False, "Governance disabled"
    if symbol not in rules.allowed_symbols:
        return False, f"Symbol not allowed: {symbol}"
    if qty <= 0:
        return False, "Qty must be > 0"
    if qty > rules.max_qty_per_trade:
        return False, f"Qty exceeds max per trade: {qty} > {rules.max_qty_per_trade}"
    return True, "OK"
