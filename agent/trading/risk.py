from __future__ import annotations
from dataclasses import dataclass
from agent.core.types import Decision

@dataclass(frozen=True)
class RiskResult:
    approved: bool
    reason: str

class RiskManager:
    def approve(self, decision: Decision) -> RiskResult:
        # SAFE DEFAULT: block any real intents until you explicitly enable later
        if decision.intents:
            return RiskResult(False, "Blocked: trading disabled by default")
        return RiskResult(True, "Approved: no intents")
