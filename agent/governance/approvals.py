from __future__ import annotations
from pathlib import Path
import re

APPROVALS_DIR = Path("approvals")

# Security: proposal_id may eventually come from untrusted sources (API/task queue/LLM).
# Enforce a strict, path-safe identifier to prevent path traversal and weird filesystem tricks.
_SAFE_ID_RE = re.compile(r"^[A-Za-z0-9_-]{8,128}$")

def validate_proposal_id(proposal_id: str) -> str:
    if not isinstance(proposal_id, str):
        raise TypeError("proposal_id must be a string")
    if not _SAFE_ID_RE.fullmatch(proposal_id):
        raise ValueError("Invalid proposal_id format (expected [A-Za-z0-9_-], length 8-128)")
    return proposal_id

def approval_path(proposal_id: str) -> Path:
    pid = validate_proposal_id(proposal_id)
    return APPROVALS_DIR / f"{pid}.approved"

def is_approved(proposal_id: str) -> bool:
    return approval_path(proposal_id).exists()

def write_approval(proposal_id: str, note: str = "approved") -> Path:
    APPROVALS_DIR.mkdir(parents=True, exist_ok=True)
    p = approval_path(proposal_id)
    p.write_text(note, encoding="utf-8")
    return p
