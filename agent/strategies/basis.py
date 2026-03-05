from __future__ import annotations
from dataclasses import dataclass

from agent.core.proposals import Proposal
from agent.core.types import MarketSnapshot
from agent.strategies.base import StrategyContext


@dataclass
class BasisStrategy:
    name: str = "basis"

    def generate(self, snap: MarketSnapshot, ctx: StrategyContext) -> list[Proposal]:
        # Proposal-only placeholder
        return []