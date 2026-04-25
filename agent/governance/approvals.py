from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

from agent.core.proposals import Proposal


APPROVALS_DIR = Path("approvals")

# Security: proposal_id may eventually come from untrusted sources.
# Enforce a strict, path-safe identifier to prevent path traversal.
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


def _canonical_proposal_payload(proposal: Proposal) -> dict[str, Any]:
    return {
        "proposal_id": proposal.proposal_id,
        "type": str(proposal.type.value),
        "payload": proposal.payload,
        "reason": proposal.reason,
    }


def proposal_hash(proposal: Proposal) -> str:
    validate_proposal_id(proposal.proposal_id)

    encoded = json.dumps(
        _canonical_proposal_payload(proposal),
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    ).encode("utf-8")

    return hashlib.sha256(encoded).hexdigest()


def write_proposal_approval(proposal: Proposal, note: str = "approved") -> Path:
    APPROVALS_DIR.mkdir(parents=True, exist_ok=True)

    record = {
        "proposal_id": proposal.proposal_id,
        "proposal_hash": proposal_hash(proposal),
        "approved": True,
        "note": note,
    }

    p = approval_path(proposal.proposal_id)
    p.write_text(json.dumps(record, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    return p


def is_approved_for_proposal(proposal: Proposal) -> bool:
    p = approval_path(proposal.proposal_id)

    if not p.exists():
        return False

    try:
        record = json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return False

    if not isinstance(record, dict):
        return False

    if record.get("approved") is not True:
        return False

    if record.get("proposal_id") != proposal.proposal_id:
        return False

    if record.get("proposal_hash") != proposal_hash(proposal):
        return False

    return True


# Backward-compatible helpers for non-execution checks.
# The executor must use is_approved_for_proposal(), not this ID-only helper.
def is_approved(proposal_id: str) -> bool:
    return approval_path(proposal_id).exists()


def write_approval(proposal_id: str, note: str = "approved") -> Path:
    APPROVALS_DIR.mkdir(parents=True, exist_ok=True)
    p = approval_path(proposal_id)
    p.write_text(note, encoding="utf-8")
    return p
