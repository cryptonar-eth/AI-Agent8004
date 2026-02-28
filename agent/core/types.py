from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Any

class Side(str, Enum):
    BUY = "buy"
    SELL = "sell"

@dataclass(frozen=True)
class MarketSnapshot:
    symbol: str
    ts_ms: int
    mid: float
    meta: dict[str, Any] | None = None

@dataclass(frozen=True)
class OrderIntent:
    symbol: str
    side: Side
    qty: float
    reason: str

@dataclass(frozen=True)
class Decision:
    intents: list[OrderIntent]
    notes: str = ""
