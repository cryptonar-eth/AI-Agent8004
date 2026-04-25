from __future__ import annotations

from decimal import Decimal

from agent.engine.rust_guard import RustOrderProposal, validate_with_rust


def test_rust_allows_safe_dry_run_order() -> None:
    proposal = RustOrderProposal(
        proposal_id="test-safe-0001",
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
    assert decision["proposal_id"] == "test-safe-0001"


def test_rust_denies_real_trading() -> None:
    proposal = RustOrderProposal(
        proposal_id="test-real-0001",
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
    assert "DRY_RUN_ORDER" in decision["reason"] or "real trading" in decision["reason"]


def test_rust_denies_oversized_order() -> None:
    proposal = RustOrderProposal(
        proposal_id="test-size-0001",
        symbol="ETH-USD",
        side="buy",
        qty=Decimal("1.0"),
        price=Decimal("2500.00"),
        intent="DRY_RUN_ORDER",
        dry_run=True,
        approved=True,
    )

    decision = validate_with_rust(proposal)

    assert decision["allowed"] is False
    assert "quantity exceeds" in decision["reason"]


def test_rust_denies_missing_approval() -> None:
    proposal = RustOrderProposal(
        proposal_id="test-approval-0001",
        symbol="ETH-USD",
        side="buy",
        qty=Decimal("0.001"),
        price=Decimal("2500.00"),
        intent="DRY_RUN_ORDER",
        dry_run=True,
        approved=False,
    )

    decision = validate_with_rust(proposal)

    assert decision["allowed"] is False
    assert "approval" in decision["reason"]
