from __future__ import annotations

from pathlib import Path

from agent.brain.langgraph_brain import run_brain_once


def test_langgraph_brain_creates_proposal_and_uses_executor(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    monkeypatch.chdir(tmp_path)

    result = run_brain_once(symbol="ETH-USD", mid=3500.0)

    captured = capsys.readouterr()

    assert "BLOCKED: not approved" in captured.out
    assert "proposal_created" in result["events"]
    assert "executor_invoked" in result["events"]
    assert result["proposals"][0].proposal_id == "trade-smoke-fixed-0001"
