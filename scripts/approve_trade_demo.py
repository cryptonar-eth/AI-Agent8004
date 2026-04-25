from __future__ import annotations

from agent.governance.approvals import write_proposal_approval
from agent.trading.policy import new_trade_proposal


def main() -> None:
    demo = new_trade_proposal(
        "ETH-USD",
        "buy",
        0.005,
        "demo proposal",
        proposal_id="trade-demo-fixed-0001",
    )

    path = write_proposal_approval(demo, note="approved demo dry-run proposal")
    print(f"Wrote hash-bound approval: {path}")


if __name__ == "__main__":
    main()
