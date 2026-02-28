from __future__ import annotations
from agent.core.types import Decision
from agent.trading.risk import RiskResult
from agent.config.settings import Settings

class Executor:
    def __init__(self, settings: Settings):
        self.settings = settings

    def execute(self, decision: Decision, risk: RiskResult) -> None:
        if not risk.approved:
            print(f"[EXEC] BLOCKED: {risk.reason}")
            return
        if self.settings.dry_run:
            print(f"[EXEC] DRY_RUN: would execute {len(decision.intents)} intents")
            for it in decision.intents:
                print(f"  - {it.side} {it.qty} {it.symbol} :: {it.reason}")
            return
        raise NotImplementedError("Live execution not implemented yet")
