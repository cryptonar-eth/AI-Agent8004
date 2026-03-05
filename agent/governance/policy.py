from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class GovernanceRules:
    enabled: bool = True

    # Symbol allowlist (canonical symbols in your system)
    allowed_symbols: set[str] = None  # set in DEFAULT_RULES

    # Execution-domain allowlists (defence in depth)
    allowed_venues: set[str] = None   # e.g. {"demo"} now; later: {"binance", "kraken", ...}
    allowed_instruments: set[str] = None  # {"spot", "perp"}

    # Simple size caps (tight by default)
    max_qty_per_trade: float = 0.01
    max_legs_per_bundle: int = 2

    # Optional: conservative notional cap for bundles (if provided by proposal)
    max_bundle_notional_usd: float = 200.0


DEFAULT_RULES = GovernanceRules(
    enabled=True,
    allowed_symbols={"ETH-USD"},
    allowed_venues={"demo"},
    allowed_instruments={"spot", "perp"},
    max_qty_per_trade=0.01,
    max_legs_per_bundle=2,
    max_bundle_notional_usd=200.0,
)


def check_trade(symbol: str, qty: float, rules: GovernanceRules = DEFAULT_RULES) -> tuple[bool, str]:
    """Back-compat single-leg trade governance (existing TRADE proposals)."""
    if not rules.enabled:
        return False, "Governance disabled"
    if symbol not in rules.allowed_symbols:
        return False, f"Symbol not allowed: {symbol}"
    if qty <= 0:
        return False, "Qty must be > 0"
    if qty > rules.max_qty_per_trade:
        return False, f"Qty exceeds max per trade: {qty} > {rules.max_qty_per_trade}"
    return True, "OK"


def _get_str(d: dict[str, Any], k: str, default: str = "") -> str:
    v = d.get(k, default)
    return str(v) if v is not None else default


def _get_float(d: dict[str, Any], k: str) -> float | None:
    if k not in d or d.get(k) is None:
        return None
    try:
        return float(d.get(k))
    except Exception:
        return None


def check_trade_leg(leg: dict[str, Any], rules: GovernanceRules = DEFAULT_RULES) -> tuple[bool, str]:
    """Governance for one leg in a bundle."""
    if not rules.enabled:
        return False, "Governance disabled"

    venue = _get_str(leg, "venue")
    instrument = _get_str(leg, "instrument")
    symbol = _get_str(leg, "symbol")
    side = _get_str(leg, "side")

    if venue not in rules.allowed_venues:
        return False, f"Venue not allowed: {venue}"
    if instrument not in rules.allowed_instruments:
        return False, f"Instrument not allowed: {instrument}"
    if symbol not in rules.allowed_symbols:
        return False, f"Symbol not allowed: {symbol}"
    if side not in {"buy", "sell"}:
        return False, f"Invalid side: {side}"

    qty = _get_float(leg, "qty")
    notional_usd = _get_float(leg, "notional_usd")

    # Require at least one sizing method
    if qty is None and notional_usd is None:
        return False, "Leg must specify qty or notional_usd"

    # If qty is provided, enforce qty cap (tight default)
    if qty is not None:
        if qty <= 0:
            return False, "Leg qty must be > 0"
        if qty > rules.max_qty_per_trade:
            return False, f"Leg qty exceeds max per trade: {qty} > {rules.max_qty_per_trade}"

    # leverage sanity if provided
    lev = _get_float(leg, "leverage")
    if lev is not None:
        if lev <= 0:
            return False, "Leverage must be > 0"
        # keep conservative defaults; risk module can enforce stricter later
        if lev > 5:
            return False, f"Leverage too high for now: {lev} > 5"

    return True, "OK"


def check_trade_bundle(payload: dict[str, Any], rules: GovernanceRules = DEFAULT_RULES) -> tuple[bool, str]:
    """Governance for atomic bundle proposals."""
    if not rules.enabled:
        return False, "Governance disabled"

    legs = payload.get("legs")
    if not isinstance(legs, list) or not legs:
        return False, "Bundle payload must include non-empty legs[]"

    if len(legs) > rules.max_legs_per_bundle:
        return False, f"Too many legs: {len(legs)} > {rules.max_legs_per_bundle}"

    for i, leg in enumerate(legs):
        if not isinstance(leg, dict):
            return False, f"Leg[{i}] must be an object"
        ok, reason = check_trade_leg(leg, rules=rules)
        if not ok:
            return False, f"Leg[{i}] invalid: {reason}"

    return True, "OK"
