from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Literal


class ProposalType(str, Enum):
    TRADE = "trade"
    TRADE_BUNDLE = "trade_bundle"  # atomic multi-leg trade intent

    SOCIAL_POST = "social_post"
    NFT_MINT = "nft_mint"
    TOKEN_DEPLOY = "token_deploy"
    QUEST = "quest"


@dataclass(frozen=True)
class Proposal:
    proposal_id: str
    type: ProposalType
    payload: dict[str, Any]
    reason: str


# --- Optional typed helpers (the system still accepts dict payloads) ---

InstrumentType = Literal["spot", "perp"]
SideType = Literal["buy", "sell"]


@dataclass(frozen=True)
class TradePayload:
    symbol: str
    side: SideType
    qty: float
    price_usd: float | None = None  # optional hint


@dataclass(frozen=True)
class TradeLeg:
    """
    One leg inside an atomic bundle.
    Keep this conservative; executor/governance can enforce stricter constraints later.
    """
    venue: str
    instrument: InstrumentType
    symbol: str
    side: SideType

    # For spot: qty is typical. For perps: you may prefer notional_usd.
    qty: float | None = None
    notional_usd: float | None = None

    leverage: float | None = None
    reduce_only: bool = False

    price_usd: float | None = None  # optional hint for risk estimation


@dataclass(frozen=True)
class TradeBundlePayload:
    legs: list[TradeLeg]
    max_slippage_bps: int | None = None
    min_expected_edge_usd: float | None = None
    client_order_id: str | None = None  # optional idempotency at venue later
    