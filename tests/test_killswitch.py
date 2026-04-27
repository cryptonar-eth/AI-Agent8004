from __future__ import annotations

from pathlib import Path

from agent.config.settings import Settings
from agent.core.proposals import Proposal, ProposalType
from agent.governance.approvals import write_proposal_approval
from agent.ops.killswitch import is_killed, kill, revive
from agent.trading.execution import Executor


def _proposal() -> Proposal:
    return Proposal(
        proposal_id="killswitch-test-0001",
        type=ProposalType.TRADE,
        payload={
            "symbol": "ETH-USD",
            "side": "buy",
            "qty": 0.005,
            "price_usd": 3500.0,
        },
        reason="kill switch test",
    )


def test_killswitch_status_false_by_default(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)

    assert is_killed() is False


def test_killswitch_status_true_when_enabled(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)

    kill("test kill")

    assert is_killed() is True


def test_killswitch_can_be_disabled(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)

    kill("test kill")
    revive()

    assert is_killed() is False


def test_executor_blocks_when_killswitch_enabled_even_with_approval(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    monkeypatch.chdir(tmp_path)

    proposal = _proposal()
    write_proposal_approval(proposal)
    kill("test emergency stop")

    executor = Executor(Settings(dry_run=True))
    executor.execute(proposal)

    captured = capsys.readouterr()

    assert "BLOCKED: kill switch enabled" in captured.out
    assert "DRY_RUN" not in captured.out
