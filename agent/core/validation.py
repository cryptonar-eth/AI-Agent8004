from __future__ import annotations

import math
from typing import Any

from agent.core.proposals import Proposal, ProposalType


def _is_finite_positive_number(value: Any) -> bool:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return False

    return math.isfinite(number) and number > 0


def validate_proposal_shape(proposal: Proposal) -> tuple[bool, str]:
    if not isinstance(proposal.payload, dict):
        return False, "proposal payload must be a dictionary"

    if proposal.type == ProposalType.TRADE:
        return _validate_trade_payload(proposal.payload)

    if proposal.type == ProposalType.TRADE_BUNDLE:
        return _validate_trade_bundle_payload(proposal.payload)

    return False, f"unsupported proposal type: {proposal.type}"


def _validate_trade_payload(payload: dict[str, Any]) -> tuple[bool, str]:
    symbol = payload.get("symbol")
    side = payload.get("side")
    qty = payload.get("qty")
    price_usd = payload.get("price_usd")

    if not isinstance(symbol, str) or not symbol.strip():
        return False, "trade symbol must be a non-empty string"

    if side not in {"buy", "sell"}:
        return False, "trade side must be buy or sell"

    if not _is_finite_positive_number(qty):
        return False, "trade quantity must be a positive finite number"

    if price_usd is not None and not _is_finite_positive_number(price_usd):
        return False, "trade price_usd must be a positive finite number when provided"

    return True, "OK"


def _validate_trade_bundle_payload(payload: dict[str, Any]) -> tuple[bool, str]:
    legs = payload.get("legs")

    if not isinstance(legs, list) or not legs:
        return False, "trade bundle legs must be a non-empty list"

    for index, leg in enumerate(legs):
        if not isinstance(leg, dict):
            return False, f"trade bundle leg[{index}] must be a dictionary"

        symbol = leg.get("symbol")
        side = leg.get("side")
        venue = leg.get("venue")
        instrument = leg.get("instrument")
        qty = leg.get("qty")
        notional_usd = leg.get("notional_usd")
        price_usd = leg.get("price_usd")
        leverage = leg.get("leverage")

        if not isinstance(venue, str) or not venue.strip():
            return False, f"trade bundle leg[{index}] venue must be a non-empty string"

        if instrument not in {"spot", "perp"}:
            return False, f"trade bundle leg[{index}] instrument must be spot or perp"

        if not isinstance(symbol, str) or not symbol.strip():
            return False, f"trade bundle leg[{index}] symbol must be a non-empty string"

        if side not in {"buy", "sell"}:
            return False, f"trade bundle leg[{index}] side must be buy or sell"

        if qty is None and notional_usd is None:
            return False, f"trade bundle leg[{index}] requires qty or notional_usd"

        if qty is not None and not _is_finite_positive_number(qty):
            return False, f"trade bundle leg[{index}] qty must be a positive finite number"

        if notional_usd is not None and not _is_finite_positive_number(notional_usd):
            return False, f"trade bundle leg[{index}] notional_usd must be positive and finite"

        if price_usd is not None and not _is_finite_positive_number(price_usd):
            return False, f"trade bundle leg[{index}] price_usd must be positive and finite"

        if leverage is not None and not _is_finite_positive_number(leverage):
            return False, f"trade bundle leg[{index}] leverage must be positive and finite"

    return True, "OK"
