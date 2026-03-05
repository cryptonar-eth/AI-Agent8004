from __future__ import annotations
import asyncio

from agent.config.settings import load_settings
from agent.runtime.orchestrator import Orchestrator, OrchestratorConfig
from agent.trading.execution import Executor

from agent.strategies.smoke_test import SmokeTestStrategy
from agent.strategies.funding_carry import FundingCarryStrategy
from agent.strategies.trend import TrendStrategy
from agent.strategies.basis import BasisStrategy


async def main() -> None:
    settings = load_settings()
    execu = Executor(settings)

    strategies = [
        SmokeTestStrategy(interval_seconds=10),
        FundingCarryStrategy(),
        TrendStrategy(),
        BasisStrategy(),
    ]

    orch = Orchestrator(
        execu=execu,
        strategies=strategies,
        cfg=OrchestratorConfig(symbol="ETH-USD", poll_seconds=2.0),
    )

    await orch.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nStopped.\n")