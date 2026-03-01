from __future__ import annotations
import secrets
from agent.core.types import MarketSnapshot
from agent.core.proposals import Proposal, ProposalType

class TradingPolicy:
    """
    No keys. No RPC. Creates proposals only.
    SAFE DEFAULT: no proposals.
    """
    def decide(self, snap: MarketSnapshot) -> list[Proposal]:
        return []

def new_trade_proposal(symbol: str, side: str, qty: float, reason: str) -> Proposal:
    pid = f"trade-{secrets.token_urlsafe(12)}"
    return Proposal(
        proposal_id=pid,
        type=ProposalType.TRADE,
        payload={"symbol": symbol, "side": side, "qty": qty},
        reason=reason,
    )
