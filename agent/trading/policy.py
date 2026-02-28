from __future__ import annotations
from agent.core.types import MarketSnapshot, Decision

class TradingPolicy:
    # No RPC, no keys, no side effects
    def decide(self, snap: MarketSnapshot) -> Decision:
        return Decision(intents=[], notes=f"No-op policy for {snap.symbol}")
