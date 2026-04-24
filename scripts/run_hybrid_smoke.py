from __future__ import annotations

from decimal import Decimal

from agent.engine.rust_guard import RustOrderProposal, validate_with_rust


def main() -> None:
    safe_demo = RustOrderProposal(
        proposal_id="hybrid-smoke-safe-001",
        symbol="ETH-USD",
        side="buy",
        qty=Decimal("0.001"),
        price=Decimal("2500.00"),
        intent="DRY_RUN_ORDER",
        dry_run=True,
        approved=True,
    )

    dangerous_demo = RustOrderProposal(
        proposal_id="hybrid-smoke-danger-001",
        symbol="ETH-USD",
        side="buy",
        qty=Decimal("1.0"),
        price=Decimal("2500.00"),
        intent="REAL_ORDER",
        dry_run=False,
        approved=True,
    )

    print("SAFE DEMO:")
    print(validate_with_rust(safe_demo))

    print("\nDANGEROUS DEMO:")
    print(validate_with_rust(dangerous_demo))


if __name__ == "__main__":
    main()
