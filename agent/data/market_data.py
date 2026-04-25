from __future__ import annotations

import math
import time
from dataclasses import dataclass
from typing import Protocol

from agent.core.types import MarketSnapshot


ALLOWED_MARKET_SYMBOLS = frozenset({"ETH-USD"})


@dataclass(frozen=True)
class MarketTick:
    symbol: str
    mid: float
    ts_ms: int
    source: str = "static"


class MarketDataProvider(Protocol):
    """Read-only market data provider interface."""

    def get_snapshot(self, symbol: str) -> MarketSnapshot:
        """Return a validated market snapshot for a symbol."""


def _now_ms() -> int:
    return int(time.time() * 1000)


def validate_market_tick(tick: MarketTick) -> MarketTick:
    if tick.symbol not in ALLOWED_MARKET_SYMBOLS:
        raise ValueError(f"market symbol is not allowed: {tick.symbol}")

    if not math.isfinite(tick.mid):
        raise ValueError("market mid price must be finite")

    if tick.mid <= 0:
        raise ValueError("market mid price must be positive")

    if tick.ts_ms <= 0:
        raise ValueError("market timestamp must be positive")

    if not tick.source.strip():
        raise ValueError("market source is required")

    return tick


class StaticMarketDataProvider:
    """
    Security-first offline market data provider.

    This provider does not call exchanges, APIs, sockets, or network services.
    It exists so the agent can be tested end-to-end with deterministic read-only data.
    """

    def __init__(self, prices: dict[str, float] | None = None):
        self._prices = prices or {"ETH-USD": 3500.0}

    def get_tick(self, symbol: str) -> MarketTick:
        if symbol not in self._prices:
            raise ValueError(f"no static market price configured for: {symbol}")

        tick = MarketTick(
            symbol=symbol,
            mid=float(self._prices[symbol]),
            ts_ms=_now_ms(),
            source="static",
        )

        return validate_market_tick(tick)

    def get_snapshot(self, symbol: str) -> MarketSnapshot:
        tick = self.get_tick(symbol)

        return MarketSnapshot(
            symbol=tick.symbol,
            ts_ms=tick.ts_ms,
            mid=tick.mid,
            meta={"source": tick.source},
        )
