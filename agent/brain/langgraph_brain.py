from __future__ import annotations

import time
from typing import Any, TypedDict

from langgraph.graph import END, START, StateGraph

from agent.config.settings import load_settings
from agent.core.proposals import Proposal
from agent.core.types import MarketSnapshot
from agent.governance.approvals import approval_path
from agent.trading.execution import Executor
from agent.trading.policy import new_trade_proposal


class BrainState(TypedDict, total=False):
    symbol: str
    mid: float
    proposal_id: str
    snapshot: MarketSnapshot
    proposals: list[Proposal]
    events: list[str]


def build_snapshot(state: BrainState) -> BrainState:
    symbol = state.get("symbol", "ETH-USD")
    mid = float(state.get("mid", 3500.0))

    snapshot = MarketSnapshot(
        symbol=symbol,
        ts_ms=int(time.time() * 1000),
        mid=mid,
    )

    return {
        "snapshot": snapshot,
        "events": state.get("events", []) + ["snapshot_built"],
    }


def create_proposal(state: BrainState) -> BrainState:
    snapshot = state["snapshot"]
    proposal_id = state.get("proposal_id", "langgraph-smoke-0001")

    proposal = new_trade_proposal(
        snapshot.symbol,
        "buy",
        0.005,
        "LangGraph smoke proposal; execution must pass executor and Rust gate",
        proposal_id=proposal_id,
    )

    return {
        "proposals": [proposal],
        "events": state.get("events", []) + ["proposal_created"],
    }


def execute_through_choke_point(state: BrainState) -> BrainState:
    proposal_id = state.get("proposal_id", "langgraph-smoke-0001")

    # Defense-in-depth for this smoke graph:
    # never leave a previous local approval file active for this demo proposal.
    approval_path(proposal_id).unlink(missing_ok=True)

    settings = load_settings()
    executor = Executor(settings)

    for proposal in state.get("proposals", []):
        executor.execute(proposal)

    return {
        "events": state.get("events", []) + ["executor_invoked"],
    }


def build_brain_graph():
    builder = StateGraph(BrainState)

    builder.add_node("build_snapshot", build_snapshot)
    builder.add_node("create_proposal", create_proposal)
    builder.add_node("execute_through_choke_point", execute_through_choke_point)

    builder.add_edge(START, "build_snapshot")
    builder.add_edge("build_snapshot", "create_proposal")
    builder.add_edge("create_proposal", "execute_through_choke_point")
    builder.add_edge("execute_through_choke_point", END)

    return builder.compile()


def run_brain_once(symbol: str = "ETH-USD", mid: float = 3500.0) -> dict[str, Any]:
    graph = build_brain_graph()
    result = graph.invoke(
        {
            "symbol": symbol,
            "mid": mid,
            "proposal_id": "langgraph-smoke-0001",
        }
    )
    return dict(result)
