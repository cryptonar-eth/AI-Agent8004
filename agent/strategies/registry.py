from __future__ import annotations

from collections.abc import Callable

from agent.strategies.base import Strategy
from agent.strategies.basis import BasisStrategy
from agent.strategies.funding_carry import FundingCarryStrategy
from agent.strategies.smoke_test import SmokeTestStrategy
from agent.strategies.trend import TrendStrategy


StrategyFactory = Callable[[], Strategy]

_ALLOWED_STRATEGY_FACTORIES: dict[str, StrategyFactory] = {
    "smoke_test": SmokeTestStrategy,
    "funding_carry": FundingCarryStrategy,
    "trend": TrendStrategy,
    "basis": BasisStrategy,
}

DEFAULT_STRATEGY_NAMES: tuple[str, ...] = ("smoke_test",)


def allowed_strategy_names() -> tuple[str, ...]:
    return tuple(sorted(_ALLOWED_STRATEGY_FACTORIES.keys()))


def build_strategy(name: str) -> Strategy:
    if name not in _ALLOWED_STRATEGY_FACTORIES:
        allowed = ", ".join(allowed_strategy_names())
        raise ValueError(f"strategy is not allowlisted: {name}. allowed={allowed}")

    strategy = _ALLOWED_STRATEGY_FACTORIES[name]()

    if getattr(strategy, "name", None) != name:
        raise ValueError(
            f"strategy factory mismatch: requested={name}, built={getattr(strategy, 'name', None)}"
        )

    return strategy


def build_strategies(names: list[str] | tuple[str, ...] | None = None) -> list[Strategy]:
    selected = tuple(names) if names is not None else DEFAULT_STRATEGY_NAMES

    if not selected:
        raise ValueError("at least one strategy must be selected")

    seen: set[str] = set()
    strategies: list[Strategy] = []

    for name in selected:
        if name in seen:
            raise ValueError(f"duplicate strategy selected: {name}")

        seen.add(name)
        strategies.append(build_strategy(name))

    return strategies
