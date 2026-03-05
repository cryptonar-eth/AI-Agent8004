from __future__ import annotations
from dataclasses import dataclass
import time

from agent.core.proposals import Proposal, ProposalType
from agent.core.types import MarketSnapshot
from agent.strategies.base import StrategyContext


@dataclass
class FundingCarryStrategy:
    """
    Funding carry: long spot + short perp (atomic bundle).

    SECURITY-FIRST:
    - Proposal-only.
    - Fail-closed if required context is missing.
    - Emits a bundle proposal so executor can gate the combined exposure atomically.
    """
    name: str = "funding_carry"
    interval_seconds: int = 30
    min_funding_rate: float = 0.0003  # e.g. 0.03% per funding window (placeholder)
    qty_spot: float = 0.001
    venue: str = "demo"
    _last_emit: float = 0.0

    def generate(self, snap: MarketSnapshot, ctx: StrategyContext) -> list[Proposal]:
        now = time.time()
        if now - self._last_emit < self.interval_seconds:
            return []

        # Fail-closed until ctx carries regime + funding info
        regime = getattr(ctx, "regime", None)
        funding_rate = getattr(ctx, "funding_rate", None)

        if regime != "SIDEWAYS":
            return []

        if funding_rate is None:
            return []

        try:
            fr = float(funding_rate)
        except Exception:
            return []

        if fr < self.min_funding_rate:
            return []

        # Atomic bundle: spot long + perp short
        # NOTE: symbol mapping will evolve later (perp symbol conventions differ by venue).
        spot_symbol = snap.symbol
        perp_symbol = f"{snap.symbol}-PERP"

        self._last_emit = now

        pid = f"bundle-fundingcarry-{spot_symbol}-{int(now)}"
        return [
            Proposal(
                proposal_id=pid,
                type=ProposalType.TRADE_BUNDLE,
                reason=f"funding carry SIDEWAYS funding={fr:.6f}",
                payload={
                    "legs": [
                        {
                            "venue": self.venue,
                            "instrument": "spot",
                            "symbol": spot_symbol,
                            "side": "buy",
                            "qty": self.qty_spot,
                            "price_usd": float(getattr(snap, "mid", 3500.0)),
                        },
                        {
                            "venue": self.venue,
                            "instrument": "perp",
                            "symbol": perp_symbol,
                            "side": "sell",
                            # keep it 1x: use qty or notional_usd later; start with qty mirror
                            "qty": self.qty_spot,
                            "leverage": 1.0,
                            "reduce_only": False,
                            "price_usd": float(getattr(snap, "mid", 3500.0)),
                        },
                    ],
                    "max_slippage_bps": 20,
                    "min_expected_edge_usd": 0.0,
                },
            )
        ]
    