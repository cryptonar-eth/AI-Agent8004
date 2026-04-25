from __future__ import annotations

import pytest

from agent.core.types import MarketSnapshot
from agent.strategies.base import StrategyContext
from agent.strategies.registry import (
    allowed_strategy_names,
    build_strategies,
    build_strategy,
)


def test_allowed_strategy_names_are_explicit() -> None:
    assert allowed_strategy_names() == (
        "basis",
        "funding_carry",
        "smoke_test",
        "trend",
    )


def test_build_default_strategies_uses_smoke_test_only() -> None:
    strategies = build_strategies()

    assert [strategy.name for strategy in strategies] == ["smoke_test"]


def test_unknown_strategy_is_rejected() -> None:
    with pytest.raises(ValueError, match="not allowlisted"):
        build_strategy("random_import")


def test_duplicate_strategy_is_rejected() -> None:
    with pytest.raises(ValueError, match="duplicate"):
        build_strategies(["smoke_test", "smoke_test"])


def test_smoke_strategy_from_registry_generates_safe_proposal() -> None:
    strategy = build_strategy("smoke_test")
    snapshot = MarketSnapshot(symbol="ETH-USD", ts_ms=1, mid=3500.0)

    proposals = strategy.generate(snapshot, StrategyContext())

    assert len(proposals) == 1
    assert proposals[0].proposal_id == "trade-smoke-fixed-0001"
    assert proposals[0].payload["symbol"] == "ETH-USD"
    assert proposals[0].payload["side"] == "buy"
    assert proposals[0].payload["qty"] == 0.001


def test_placeholder_strategies_emit_no_proposals_by_default() -> None:
    snapshot = MarketSnapshot(symbol="ETH-USD", ts_ms=1, mid=3500.0)

    for name in ("basis", "trend", "funding_carry"):
        strategy = build_strategy(name)
        assert strategy.generate(snapshot, StrategyContext()) == []
