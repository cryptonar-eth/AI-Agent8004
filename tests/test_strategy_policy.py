from __future__ import annotations

import json
from pathlib import Path

import pytest

from agent.config.strategy_policy import load_strategy_policy
from agent.strategies.registry import build_strategies_from_policy


def _write_policy(tmp_path: Path, data: dict) -> Path:
    path = tmp_path / "strategy_policy.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


def _valid_policy() -> dict:
    return {
        "version": 1,
        "enabled_strategies": ["smoke_test"],
    }


def test_load_default_strategy_policy() -> None:
    policy = load_strategy_policy()

    assert policy.version == 1
    assert policy.enabled_strategies == ("smoke_test",)


def test_default_strategy_policy_loads_after_chdir(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)

    policy = load_strategy_policy()

    assert policy.enabled_strategies == ("smoke_test",)


def test_strategy_policy_rejects_empty_strategy_list(tmp_path: Path) -> None:
    data = _valid_policy()
    data["enabled_strategies"] = []

    with pytest.raises(ValueError, match="at least one"):
        load_strategy_policy(_write_policy(tmp_path, data))


def test_strategy_policy_rejects_duplicate_strategy(tmp_path: Path) -> None:
    data = _valid_policy()
    data["enabled_strategies"] = ["smoke_test", "smoke_test"]

    with pytest.raises(ValueError, match="duplicate"):
        load_strategy_policy(_write_policy(tmp_path, data))


def test_registry_rejects_unknown_strategy_from_policy(tmp_path: Path) -> None:
    data = _valid_policy()
    data["enabled_strategies"] = ["unknown_strategy"]

    policy = load_strategy_policy(_write_policy(tmp_path, data))

    with pytest.raises(ValueError, match="not allowlisted"):
        build_strategies_from_policy(policy)


def test_registry_builds_strategy_from_policy() -> None:
    strategies = build_strategies_from_policy()

    assert [strategy.name for strategy in strategies] == ["smoke_test"]
