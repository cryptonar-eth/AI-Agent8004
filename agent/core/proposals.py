from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Any

class ProposalType(str, Enum):
    TRADE = "trade"
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

@dataclass(frozen=True)
class TradePayload:
    symbol: str
    side: str  # "buy" / "sell"
    qty: float
