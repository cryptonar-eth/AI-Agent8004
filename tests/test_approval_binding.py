from __future__ import annotations

from pathlib import Path

from agent.core.proposals import Proposal, ProposalType
from agent.governance.approvals import (
    is_approved_for_proposal,
    proposal_hash,
    write_approval,
    write_proposal_approval,
)


def _proposal(qty: float = 0.005) -> Proposal:
    return Proposal(
        proposal_id="approval-test-0001",
        type=ProposalType.TRADE,
        payload={
            "symbol": "ETH-USD",
            "side": "buy",
            "qty": qty,
            "price_usd": 3500.0,
        },
        reason="approval binding test",
    )


def test_hash_bound_approval_passes_for_exact_proposal(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.chdir(tmp_path)

    proposal = _proposal()
    write_proposal_approval(proposal)

    assert is_approved_for_proposal(proposal) is True


def test_hash_bound_approval_rejects_changed_payload(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.chdir(tmp_path)

    original = _proposal(qty=0.005)
    changed = _proposal(qty=0.009)

    write_proposal_approval(original)

    assert proposal_hash(original) != proposal_hash(changed)
    assert is_approved_for_proposal(changed) is False


def test_legacy_touch_style_approval_is_not_valid_for_execution(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.chdir(tmp_path)

    proposal = _proposal()
    write_approval(proposal.proposal_id)

    assert is_approved_for_proposal(proposal) is False
