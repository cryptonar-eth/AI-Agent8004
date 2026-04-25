from __future__ import annotations

from decimal import Decimal

from agent.engine.rust_guard import RustOrderProposal, validate_with_rust


def test_python_policy_gate_denies_bad_symbol_before_rust() -> None:
    proposal = RustOrderProposal(
        proposal_id="policy-badsymbol-0001",
        symbol="BTC-USD",
        side="buy",
        qty=Decimal("0.001"),
        price=Decimal("2500.00"),
        intent="DRY_RUN_ORDER",
        dry_run=True,
        approved=True,
    )

    decision = validate_with_rust(proposal)

    assert decision["allowed"] is False
    assert decision["engine"] == "novanexus_python_policy_gate_v0.1"
    assert "symbol not allowed" in decision["reason"]


def test_python_policy_gate_denies_missing_price_before_rust() -> None:
    proposal = RustOrderProposal(
        proposal_id="policy-noprice-0001",
        symbol="ETH-USD",
        side="buy",
        qty=Decimal("0.001"),
        price=None,
        intent="DRY_RUN_ORDER",
        dry_run=True,
        approved=True,
    )

    decision = validate_with_rust(proposal)

    assert decision["allowed"] is False
    assert decision["engine"] == "novanexus_python_policy_gate_v0.1"
    assert "price required" in decision["reason"]


def test_python_policy_gate_denies_real_order_before_rust() -> None:
    proposal = RustOrderProposal(
        proposal_id="policy-realorder-0001",
        symbol="ETH-USD",
        side="buy",
        qty=Decimal("0.001"),
        price=Decimal("2500.00"),
        intent="REAL_ORDER",
        dry_run=False,
        approved=True,
    )

    decision = validate_with_rust(proposal)

    assert decision["allowed"] is False
    assert decision["engine"] == "novanexus_python_policy_gate_v0.1"
    assert "DRY_RUN_ORDER" in decision["reason"] or "real trading" in decision["reason"]


def test_valid_policy_proposal_still_reaches_rust_gate() -> None:
    proposal = RustOrderProposal(
        proposal_id="policy-safe-0001",
        symbol="ETH-USD",
        side="buy",
        qty=Decimal("0.001"),
        price=Decimal("2500.00"),
        intent="DRY_RUN_ORDER",
        dry_run=True,
        approved=True,
    )

    decision = validate_with_rust(proposal)

    assert decision["allowed"] is True
    assert decision["engine"] == "novanexus_rust_engine_v0.1"
