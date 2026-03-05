from __future__ import annotations
from dataclasses import dataclass
from typing import Protocol

from agent.core.proposals import Proposal
from agent.core.types import MarketSnapshot


@dataclass(frozen=True)
class StrategyContext:
    # Extend later: funding rates, basis, volatility, etc.
    pass


class Strategy(Protocol):
    name: str

    def generate(self, snap: MarketSnapshot, ctx: StrategyContext) -> list[Proposal]:
        ...