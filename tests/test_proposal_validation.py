from __future__ import annotations

from agent.core.proposals import Proposal, ProposalType
from agent.core.validation import validate_proposal_shape


def test_valid_trade_payload_passes() -> None:
    proposal = Proposal(
        proposal_id="validation-good-0001",
        type=ProposalType.TRADE,
        payload={"symbol": "ETH-USD", "side": "buy", "qty": 0.005, "price_usd": 3500.0},
        reason="valid proposal",
    )

    ok, reason = validate_proposal_shape(proposal)

    assert ok is True
    assert reason == "OK"


def test_trade_payload_rejects_bad_side() -> None:
    proposal = Proposal(
        proposal_id="validation-badside-0001",
        type=ProposalType.TRADE,
        payload={"symbol": "ETH-USD", "side": "hold", "qty": 0.005},
        reason="invalid side",
    )

    ok, reason = validate_proposal_shape(proposal)

    assert ok is False
    assert "side" in reason


def test_trade_payload_rejects_negative_qty() -> None:
    proposal = Proposal(
        proposal_id="validation-badqty-0001",
        type=ProposalType.TRADE,
        payload={"symbol": "ETH-USD", "side": "buy", "qty": -1},
        reason="invalid qty",
    )

    ok, reason = validate_proposal_shape(proposal)

    assert ok is False
    assert "quantity" in reason


def test_trade_payload_rejects_non_finite_price() -> None:
    proposal = Proposal(
        proposal_id="validation-badprice-0001",
        type=ProposalType.TRADE,
        payload={"symbol": "ETH-USD", "side": "buy", "qty": 0.005, "price_usd": float("nan")},
        reason="invalid price",
    )

    ok, reason = validate_proposal_shape(proposal)

    assert ok is False
    assert "price_usd" in reason


def test_valid_trade_bundle_payload_passes() -> None:
    proposal = Proposal(
        proposal_id="validation-bundle-0001",
        type=ProposalType.TRADE_BUNDLE,
        payload={
            "legs": [
                {
                    "venue": "static",
                    "instrument": "spot",
                    "symbol": "ETH-USD",
                    "side": "buy",
                    "qty": 0.005,
                    "price_usd": 3500.0,
                }
            ]
        },
        reason="valid bundle",
    )

    ok, reason = validate_proposal_shape(proposal)

    assert ok is True
    assert reason == "OK"
