from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_STRATEGY_POLICY_PATH = PROJECT_ROOT / "config/strategy_policy.example.json"


@dataclass(frozen=True)
class StrategyPolicy:
    version: int
    enabled_strategies: tuple[str, ...]


def load_strategy_policy(path: Path = DEFAULT_STRATEGY_POLICY_PATH) -> StrategyPolicy:
    raw = json.loads(path.read_text(encoding="utf-8"))

    policy = StrategyPolicy(
        version=int(raw["version"]),
        enabled_strategies=tuple(str(name) for name in raw["enabled_strategies"]),
    )

    validate_strategy_policy(policy)
    return policy


def validate_strategy_policy(policy: StrategyPolicy) -> None:
    if policy.version != 1:
        raise ValueError("unsupported strategy policy version")

    if not policy.enabled_strategies:
        raise ValueError("at least one strategy must be enabled")

    if len(set(policy.enabled_strategies)) != len(policy.enabled_strategies):
        raise ValueError("duplicate strategies are not allowed")

    for name in policy.enabled_strategies:
        if not name.strip():
            raise ValueError("strategy names must be non-empty")
