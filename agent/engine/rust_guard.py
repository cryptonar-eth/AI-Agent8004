from __future__ import annotations

import json
from dataclasses import dataclass
from decimal import Decimal
from typing import Any

import novanexus_engine


@dataclass(frozen=True)
class RustOrderProposal:
    proposal_id: str
    symbol: str
    side: str
    qty: Decimal
    price: Decimal | None
    intent: str = "DRY_RUN_ORDER"
    dry_run: bool = True
    approved: bool = False

    def to_engine_json(self) -> str:
        return json.dumps(
            {
                "proposal_id": self.proposal_id,
                "symbol": self.symbol,
                "side": self.side,
                "qty": str(self.qty),
                "price": str(self.price) if self.price is not None else None,
                "intent": self.intent,
                "dry_run": self.dry_run,
                "approved": self.approved,
            },
            sort_keys=True,
        )


def validate_with_rust(proposal: RustOrderProposal) -> dict[str, Any]:
    raw = novanexus_engine.validate_order_json(proposal.to_engine_json())
    result = json.loads(raw)

    if not isinstance(result, dict):
        raise RuntimeError("Rust engine returned non-dict result")

    return result
