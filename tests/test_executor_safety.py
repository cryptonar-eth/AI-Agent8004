from __future__ import annotations

from pathlib import Path

from agent.config.settings import Settings
from agent.core.proposals import Proposal, ProposalType
from agent.governance.approvals import write_proposal_approval
from agent.trading.execution import Executor


def _trade_proposal(proposal_id: str = "trade-test-0001") -> Proposal:
    return Proposal(
        proposal_id=proposal_id,
        type=ProposalType.TRADE,
        payload={
            "symbol": "ETH-USD",
            "side": "buy",
            "qty": 0.005,
            "price_usd": 3500.0,
        },
        reason="pytest safety proposal",
    )


def test_executor_blocks_without_approval(tmp_path: Path, monkeypatch, capsys) -> None:
    monkeypatch.chdir(tmp_path)

    executor = Executor(Settings(dry_run=True))
    executor.execute(_trade_proposal("trade-test-noapproval-0001"))

    captured = capsys.readouterr()
    assert "BLOCKED: not approved" in captured.out


def test_executor_dry_run_with_approval(tmp_path: Path, monkeypatch, capsys) -> None:
    monkeypatch.chdir(tmp_path)

    proposal = _trade_proposal("trade-test-approved-0001")
    write_proposal_approval(proposal)

    executor = Executor(Settings(dry_run=True))
    executor.execute(proposal)

    captured = capsys.readouterr()
    assert "DRY_RUN" in captured.out
    assert "ETH-USD" in captured.out


def test_executor_blocks_bad_symbol_even_with_approval(tmp_path: Path, monkeypatch, capsys) -> None:
    monkeypatch.chdir(tmp_path)

    proposal = Proposal(
        proposal_id="trade-test-badsymbol-0001",
        type=ProposalType.TRADE,
        payload={
            "symbol": "BTC-USD",
            "side": "buy",
            "qty": 0.005,
            "price_usd": 3500.0,
        },
        reason="pytest bad symbol proposal",
    )
    write_proposal_approval(proposal)

    executor = Executor(Settings(dry_run=True))
    executor.execute(proposal)

    captured = capsys.readouterr()
    assert "BLOCKED" in captured.out


def test_executor_blocks_real_execution_even_with_approval(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    monkeypatch.chdir(tmp_path)

    proposal = _trade_proposal("trade-test-realexec-0001")
    write_proposal_approval(proposal)

    executor = Executor(Settings(dry_run=False))
    executor.execute(proposal)

    captured = capsys.readouterr()
    assert "BLOCKED: rust risk" in captured.out
    assert "real trading is disabled" in captured.out


def test_executor_blocks_invalid_payload_before_approval(tmp_path: Path, monkeypatch, capsys) -> None:
    monkeypatch.chdir(tmp_path)

    proposal = Proposal(
        proposal_id="trade-test-invalidshape-0001",
        type=ProposalType.TRADE,
        payload={
            "symbol": "ETH-USD",
            "side": "hold",
            "qty": 0.005,
            "price_usd": 3500.0,
        },
        reason="invalid side should be blocked before approval",
    )

    executor = Executor(Settings(dry_run=True))
    executor.execute(proposal)

    captured = capsys.readouterr()
    assert "BLOCKED: invalid proposal shape" in captured.out
    assert "side" in captured.out
