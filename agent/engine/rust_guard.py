from __future__ import annotations

import json
from dataclasses import dataclass
from decimal import Decimal
from typing import Any

import novanexus_engine

from agent.config.risk_policy import RiskPolicy, load_risk_policy


@dataclass(frozen=True)
class RustOrderProposal:
    proposal_id: str
    symbol: str
    side: str
    qty: Decimal
    price: Decimal | None
    intent: str = "DRY_RUN_ORDER"
    dry_run: bool = True
    approved: bool = False

    def to_engine_json(self) -> str:
        return json.dumps(
            {
                "proposal_id": self.proposal_id,
                "symbol": self.symbol,
                "side": self.side,
                "qty": str(self.qty),
                "price": str(self.price) if self.price is not None else None,
                "intent": self.intent,
                "dry_run": self.dry_run,
                "approved": self.approved,
            },
            sort_keys=True,
        )


def _policy_deny(proposal_id: str, reason: str) -> dict[str, Any]:
    return {
        "allowed": False,
        "reason": reason,
        "proposal_id": proposal_id,
        "engine": "novanexus_python_policy_gate_v0.1",
    }


def _validate_against_policy(
    proposal: RustOrderProposal,
    policy: RiskPolicy,
) -> dict[str, Any] | None:
    if policy.live_trading_enabled:
        return _policy_deny(proposal.proposal_id, "live trading is disabled by policy")

    if policy.mode != "dry_run_only":
        return _policy_deny(proposal.proposal_id, "policy mode must be dry_run_only")

    if proposal.symbol not in policy.allowed_symbols:
        return _policy_deny(proposal.proposal_id, "symbol not allowed by policy")

    if proposal.intent not in policy.allowed_intents:
        return _policy_deny(
            proposal.proposal_id,
            "only DRY_RUN_ORDER intent is allowed by policy",
        )

    if proposal.side not in policy.allowed_sides:
        return _policy_deny(proposal.proposal_id, "side not allowed by policy")

    if not proposal.dry_run:
        return _policy_deny(proposal.proposal_id, "real trading is disabled by policy")

    if policy.require_manual_approval and not proposal.approved:
        return _policy_deny(proposal.proposal_id, "manual approval missing by policy")

    if policy.require_price and proposal.price is None:
        return _policy_deny(proposal.proposal_id, "price required by policy")

    if proposal.qty <= Decimal("0"):
        return _policy_deny(proposal.proposal_id, "quantity must be positive by policy")

    max_qty = policy.max_qty_by_symbol.get(proposal.symbol)
    if max_qty is None:
        return _policy_deny(proposal.proposal_id, "max quantity missing by policy")

    if proposal.qty > max_qty:
        return _policy_deny(
            proposal.proposal_id,
            f"quantity exceeds max_qty={max_qty} by policy",
        )

    return None


def validate_with_rust(
    proposal: RustOrderProposal,
    policy: RiskPolicy | None = None,
) -> dict[str, Any]:
    active_policy = policy or load_risk_policy()

    policy_denial = _validate_against_policy(proposal, active_policy)
    if policy_denial is not None:
        return policy_denial

    raw = novanexus_engine.validate_order_json(proposal.to_engine_json())
    result = json.loads(raw)

    if not isinstance(result, dict):
        raise RuntimeError("Rust engine returned non-dict result")

    return result
