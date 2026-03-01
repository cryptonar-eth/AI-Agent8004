from __future__ import annotations
import time
from agent.config.settings import load_settings
from agent.core.types import MarketSnapshot
from agent.trading.policy import TradingPolicy, new_trade_proposal
from agent.trading.execution import Executor
from agent.ops.audit import log

def main() -> None:
    settings = load_settings()
    policy = TradingPolicy()
    execu = Executor(settings)

    snap = MarketSnapshot(symbol="ETH-USD", ts_ms=int(time.time()*1000), mid=3500.0)

    proposals = policy.decide(snap)

    # Demo: create one trade proposal (still won't execute without approval file)
    demo = new_trade_proposal("ETH-USD", "buy", 0.005, "demo proposal")
    proposals.append(demo)

    log("proposals_created", {"count": len(proposals), "ids": [p.proposal_id for p in proposals]})

    for p in proposals:
        print(f"[PROPOSAL] {p.proposal_id} type={p.type} payload={p.payload} reason={p.reason}")
        execu.execute(p)

    print("\nTo approve the demo proposal, run:")
    print(f"  touch approvals/{demo.proposal_id}.approved")
    print("Then run the script again.\n")

if __name__ == "__main__":
    main()
