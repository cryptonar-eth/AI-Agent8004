from __future__ import annotations
from dataclasses import dataclass
import time

from agent.core.proposals import Proposal
from agent.core.types import MarketSnapshot
from agent.strategies.base import StrategyContext
from agent.trading.policy import new_trade_proposal


@dataclass
class SmokeTestStrategy:
    """
    Emits one demo proposal (optionally rate-limited by interval_seconds).

    Security intent:
    - Proposal-only (no execution here)
    - Stable proposal_id to avoid approval spam
    - Lets Executor prove: approvals/autonomy/idempotency work
    """
    name: str = "smoke_test"
    interval_seconds: int = 10
    proposal_id: str = "trade-smoke-fixed-0001"

    _last_emit: float = 0.0

    def generate(self, snap: MarketSnapshot, ctx: StrategyContext) -> list[Proposal]:
        now = time.time()

        # Emit only once (smoke test). After first emit, stay quiet.
        if self._last_emit > 0:
            return []

        # Optional: keep interval logic (mostly redundant with emit-once)
        if now - self._last_emit < self.interval_seconds:
            return []

        self._last_emit = now
        return [
            new_trade_proposal(
                snap.symbol,
                "buy",
                0.001,
                "smoke test strategy",
                proposal_id=self.proposal_id,
            )
        ]