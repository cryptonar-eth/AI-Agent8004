from __future__ import annotations
from dataclasses import dataclass

from agent.core.proposals import Proposal
from agent.core.types import MarketSnapshot
from agent.strategies.base import StrategyContext


@dataclass
class TrendStrategy:
    name: str = "trend"

    def generate(self, snap: MarketSnapshot, ctx: StrategyContext) -> list[Proposal]:
        return []