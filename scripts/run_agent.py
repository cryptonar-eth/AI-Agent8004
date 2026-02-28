from __future__ import annotations
import time
from agent.config.settings import load_settings
from agent.core.types import MarketSnapshot
from agent.trading.policy import TradingPolicy
from agent.trading.risk import RiskManager
from agent.trading.execution import Executor

def main() -> None:
    settings = load_settings()
    policy = TradingPolicy()
    risk = RiskManager()
    execu = Executor(settings)

    snap = MarketSnapshot(symbol="ETH-USD", ts_ms=int(time.time()*1000), mid=3500.0)
    decision = policy.decide(snap)
    risk_result = risk.approve(decision)
    execu.execute(decision, risk_result)

if __name__ == "__main__":
    main()
