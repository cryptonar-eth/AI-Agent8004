from __future__ import annotations
from pathlib import Path

APPROVALS_DIR = Path("approvals")

def approval_path(proposal_id: str) -> Path:
    return APPROVALS_DIR / f"{proposal_id}.approved"

def is_approved(proposal_id: str) -> bool:
    return approval_path(proposal_id).exists()

def write_approval(proposal_id: str, note: str = "approved") -> Path:
    APPROVALS_DIR.mkdir(parents=True, exist_ok=True)
    p = approval_path(proposal_id)
    p.write_text(note)
    return p
