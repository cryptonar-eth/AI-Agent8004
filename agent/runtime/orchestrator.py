from __future__ import annotations
import asyncio
import time
from dataclasses import dataclass

from agent.core.types import MarketSnapshot
from agent.ops.audit import log
from agent.strategies.base import Strategy, StrategyContext
from agent.trading.execution import Executor


@dataclass
class OrchestratorConfig:
    symbol: str = "ETH-USD"
    poll_seconds: float = 2.0


class Orchestrator:
    def __init__(
        self,
        execu: Executor,
        strategies: list[Strategy],
        cfg: OrchestratorConfig = OrchestratorConfig(),
    ):
        self.execu = execu
        self.strategies = strategies
        self.cfg = cfg
        self._running = False
        self._exec_lock = asyncio.Lock()  # security: serialize execution

    def stop(self) -> None:
        self._running = False

    async def run(self) -> None:
        self._running = True
        ctx = StrategyContext()

        while self._running:
            ts_ms = int(time.time() * 1000)

            # Proposal-only snapshot (placeholder). Replace later with a snapshot builder.
            snap = MarketSnapshot(symbol=self.cfg.symbol, ts_ms=ts_ms, mid=3500.0)

            proposals = []
            for s in self.strategies:
                try:
                    ps = s.generate(snap, ctx)
                    proposals.extend(ps)
                except Exception as e:
                    # Strategy failure should not crash the whole agent.
                    log("strategy_error", {"strategy": getattr(s, "name", "unknown"), "error": str(e)})

            # Dedupe by proposal_id within this tick (defense-in-depth)
            if proposals:
                uniq: dict[str, object] = {}
                for p in proposals:
                    uniq[p.proposal_id] = p
                proposals = list(uniq.values())

                log("proposals_created", {"count": len(proposals), "ids": [p.proposal_id for p in proposals]})

            # Execute sequentially through the single choke point (with lock)
            async with self._exec_lock:
                for p in proposals:
                    self.execu.execute(p)

            await asyncio.sleep(self.cfg.poll_seconds)