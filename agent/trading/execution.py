from __future__ import annotations

from agent.config.settings import Settings
from agent.core.proposals import Proposal, ProposalType
from agent.governance.approvals import is_approved, validate_proposal_id
from agent.governance.policy import check_trade, check_trade_bundle
from agent.ops.killswitch import is_killed
from agent.ops.audit import log
from agent.storage.state_store import load_state, mark_executed
from agent.trading.risk_state import check_trade_pct, record_trade_timestamp


def _safe_float(x, default: float) -> float:
    try:
        return float(x)
    except Exception:
        return default


class Executor:
    """High-trust choke point. All execution must pass here."""

    def __init__(self, settings: Settings):
        self.settings = settings

    def _autonomy_enabled(self) -> bool:
        # Defence-in-depth: require two explicit flags to enable autonomy.
        return bool(self.settings.auto_execute_trades and self.settings.auto_execute_ack)

    def execute(self, proposal: Proposal) -> None:
        # Validate proposal_id early (defence in depth)
        try:
            validate_proposal_id(proposal.proposal_id)
        except Exception as e:
            log(
                "blocked_invalid_proposal_id",
                {"proposal_id": str(getattr(proposal, "proposal_id", None)), "error": str(e)},
            )
            print(f"[EXEC] BLOCKED: invalid proposal_id: {e}")
            return

        if is_killed():
            log("blocked_killswitch", {"proposal_id": proposal.proposal_id, "type": proposal.type})
            print("[EXEC] BLOCKED: kill switch enabled")
            return

        # Load state early so we can enforce idempotency consistently
        try:
            state = load_state()
        except Exception as e:
            log("blocked_state_unreadable", {"proposal_id": proposal.proposal_id, "error": str(e)})
            print(f"[EXEC] BLOCKED: state unreadable: {e}")
            return

        # Idempotency: do not execute the same proposal twice.
        if proposal.proposal_id in (state.executed_proposal_ids or []):
            log("blocked_idempotent_replay", {"proposal_id": proposal.proposal_id})
            print("[EXEC] BLOCKED: proposal already executed (idempotent)")
            return

        autonomy = self._autonomy_enabled()

        # Approval gate (for everything that can execute)
        if not autonomy:
            if not is_approved(proposal.proposal_id):
                log("blocked_no_approval", {"proposal_id": proposal.proposal_id, "payload": proposal.payload})
                print(f"[EXEC] BLOCKED: not approved. Create approvals/{proposal.proposal_id}.approved")
                return

        if proposal.type == ProposalType.TRADE:
            self._execute_single_trade(proposal, state, autonomy)
            return

        if proposal.type == ProposalType.TRADE_BUNDLE:
            self._execute_trade_bundle(proposal, state, autonomy)
            return

        log("blocked_unknown_type", {"proposal_id": proposal.proposal_id, "type": proposal.type})
        print(f"[EXEC] BLOCKED: unsupported proposal type: {proposal.type}")

    # -------------------------
    # Single trade path (legacy)
    # -------------------------
    def _execute_single_trade(self, proposal: Proposal, state, autonomy: bool) -> None:
        symbol = str(proposal.payload.get("symbol"))
        side = str(proposal.payload.get("side"))
        qty = _safe_float(proposal.payload.get("qty"), 0.0)

        ok, reason = check_trade(symbol, qty)
        if not ok:
            log("blocked_governance", {"proposal_id": proposal.proposal_id, "reason": reason, "payload": proposal.payload})
            print(f"[EXEC] BLOCKED: governance: {reason}")
            return

        price = _safe_float(proposal.payload.get("price_usd"), 3500.0)
        est_notional_usd = qty * price

        rd = check_trade_pct(state, symbol, est_notional_usd)
        if not rd.ok:
            log(
                "blocked_risk_pct",
                {"proposal_id": proposal.proposal_id, "reason": rd.reason, "notional_usd": est_notional_usd},
            )
            print(f"[EXEC] BLOCKED: risk: {rd.reason}")
            return

        if self.settings.dry_run:
            log("dry_run_trade", {"proposal_id": proposal.proposal_id, "payload": proposal.payload, "reason": proposal.reason})
            record_trade_timestamp(state, symbol)
            mark_executed(state, proposal.proposal_id)
            mode = "AUTO" if autonomy else "APPROVAL"
            print(f"[EXEC] DRY_RUN ({mode}) TRADE: {side} {qty} {symbol} @~{price} :: {proposal.reason}")
            return

        raise NotImplementedError("Live execution not implemented yet")

    # -------------------------
    # Bundle path (multi-leg)
    # -------------------------
    def _execute_trade_bundle(self, proposal: Proposal, state, autonomy: bool) -> None:
        payload = proposal.payload

        ok, reason = check_trade_bundle(payload)
        if not ok:
            log("blocked_governance_bundle", {"proposal_id": proposal.proposal_id, "reason": reason, "payload": payload})
            print(f"[EXEC] BLOCKED: governance(bundle): {reason}")
            return

        legs = payload.get("legs", [])
        assert isinstance(legs, list)

        # Conservative risk estimation:
        # - We compute total notional as sum(abs(leg_notional))
        # - Then apply risk cage to each symbol with that leg notional
        #
        # This is intentionally strict; we can refine later with margin models.
        total_notional_usd = 0.0
        per_symbol_notional: dict[str, float] = {}

        for leg in legs:
            symbol = str(leg.get("symbol"))
            price = _safe_float(leg.get("price_usd"), _safe_float(payload.get("price_usd"), 3500.0))

            qty = leg.get("qty")
            notional_usd = leg.get("notional_usd")

            leg_notional = None
            if notional_usd is not None:
                leg_notional = abs(_safe_float(notional_usd, 0.0))
            elif qty is not None:
                leg_notional = abs(_safe_float(qty, 0.0) * price)
            else:
                leg_notional = 0.0  # governance should have blocked this already

            total_notional_usd += leg_notional
            per_symbol_notional[symbol] = per_symbol_notional.get(symbol, 0.0) + leg_notional

        # Risk cage checks (fail closed)
        # Apply per-symbol check using aggregated notional per symbol.
        for sym, sym_notional in per_symbol_notional.items():
            rd = check_trade_pct(state, sym, sym_notional)
            if not rd.ok:
                log(
                    "blocked_risk_pct_bundle",
                    {"proposal_id": proposal.proposal_id, "symbol": sym, "reason": rd.reason, "notional_usd": sym_notional},
                )
                print(f"[EXEC] BLOCKED: risk(bundle): {sym}: {rd.reason}")
                return

        # If we ever implement live execution, bundle needs atomic behaviour:
        # enter both legs or abort.
        if self.settings.dry_run:
            log(
                "dry_run_trade_bundle",
                {"proposal_id": proposal.proposal_id, "payload": payload, "reason": proposal.reason, "total_notional_usd": total_notional_usd},
            )

            # Conservative: record timestamps for each symbol present in bundle.
            for sym in per_symbol_notional.keys():
                record_trade_timestamp(state, sym)

            mark_executed(state, proposal.proposal_id)
            mode = "AUTO" if autonomy else "APPROVAL"

            # Print a readable summary
            print(f"[EXEC] DRY_RUN ({mode}) TRADE_BUNDLE: legs={len(legs)} total_notional~{total_notional_usd:.2f} :: {proposal.reason}")
            for i, leg in enumerate(legs):
                venue = str(leg.get("venue"))
                instrument = str(leg.get("instrument"))
                symbol = str(leg.get("symbol"))
                side = str(leg.get("side"))
                qty = leg.get("qty")
                notional_usd = leg.get("notional_usd")
                lev = leg.get("leverage")
                ro = bool(leg.get("reduce_only", False))
                print(f"  - leg[{i}] {venue} {instrument} {side} {symbol} qty={qty} notional_usd={notional_usd} lev={lev} reduce_only={ro}")

            return

        raise NotImplementedError("Live bundle execution not implemented yet")
    