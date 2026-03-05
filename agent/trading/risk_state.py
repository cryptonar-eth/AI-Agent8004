from __future__ import annotations
from dataclasses import dataclass
import time

from agent.storage.state_store import AgentState, save_state


@dataclass(frozen=True)
class RiskPctRules:
    max_risk_per_trade_pct: float = 0.02      # 2%
    max_daily_loss_pct: float = 0.03          # 3%
    cooldown_seconds: int = 120               # 2 minutes between trades per symbol
    max_exposure_pct: float = 0.20            # 20% total exposure cap (USD notional)


@dataclass(frozen=True)
class RiskDecision:
    ok: bool
    reason: str


def _now_ms() -> int:
    return int(time.time() * 1000)


def _get_exposure(state: AgentState, symbol: str) -> float:
    # Backward compatible: older state may not have this field yet.
    exposure_map = getattr(state, "exposure_usd_by_symbol", None)
    if not isinstance(exposure_map, dict):
        return 0.0
    try:
        return float(exposure_map.get(symbol, 0.0))
    except Exception:
        return 0.0


def check_trade_pct(
    state: AgentState,
    symbol: str,
    est_notional_usd: float,
    rules: RiskPctRules = RiskPctRules(),
) -> RiskDecision:
    # Daily loss circuit breaker
    max_daily_loss_usd = state.equity_usd * rules.max_daily_loss_pct
    if state.daily_pnl_usd <= -max_daily_loss_usd:
        return RiskDecision(False, f"Daily loss limit hit: pnl={state.daily_pnl_usd:.2f} <= -{max_daily_loss_usd:.2f}")

    # Per-trade risk cap (using notional as proxy for now)
    max_trade_usd = state.equity_usd * rules.max_risk_per_trade_pct
    if est_notional_usd > max_trade_usd:
        return RiskDecision(False, f"Trade too large vs equity: {est_notional_usd:.2f} > {max_trade_usd:.2f} (risk pct cap)")

    # Total exposure cap (per symbol) - conservative
    max_exposure_usd = state.equity_usd * rules.max_exposure_pct
    current_exposure = _get_exposure(state, symbol)
    if current_exposure + est_notional_usd > max_exposure_usd:
        return RiskDecision(
            False,
            f"Exposure cap hit for {symbol}: {current_exposure + est_notional_usd:.2f} > {max_exposure_usd:.2f}",
        )

    # Cooldown per symbol
    last_ms = state.last_trade_ts_ms_by_symbol.get(symbol)
    if last_ms is not None:
        dt = (_now_ms() - last_ms) / 1000.0
        if dt < rules.cooldown_seconds:
            return RiskDecision(False, f"Cooldown active for {symbol}: wait {rules.cooldown_seconds - int(dt)}s")

    return RiskDecision(True, "OK")


def record_trade_timestamp(state: AgentState, symbol: str) -> None:
    state.last_trade_ts_ms_by_symbol[symbol] = _now_ms()
    save_state(state)


def record_exposure_delta(state: AgentState, symbol: str, delta_usd: float) -> None:
    """
    Conservative exposure tracking.
    For now, we only ever add exposure on 'enter' in DRY_RUN.
    Later we will subtract on exits / reduce_only fills via reconciliation.
    """
    exposure_map = getattr(state, "exposure_usd_by_symbol", None)
    if not isinstance(exposure_map, dict):
        exposure_map = {}
        setattr(state, "exposure_usd_by_symbol", exposure_map)

    prev = 0.0
    try:
        prev = float(exposure_map.get(symbol, 0.0))
    except Exception:
        prev = 0.0

    exposure_map[symbol] = max(0.0, prev + float(delta_usd))
    save_state(state)
    