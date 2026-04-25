#!/usr/bin/env bash
set -euo pipefail

echo "=== NovaNexus security check ==="

echo
echo "=== 1. Verify no tracked obvious secret files ==="
git ls-files | grep -Ei '(^|/)\.env$|id_rsa|id_ed25519|\.pem$|\.key$|\.p12$|wallet|mnemonic|seed|secret|token|api_key' && {
  echo "ERROR: possible secret-like tracked file found"
  exit 1
} || true

echo
echo "=== 2. Run Python/Rust safety tests ==="
pytest -q

echo
echo "=== 3. Run hybrid Rust bridge smoke test ==="
python scripts/run_hybrid_smoke.py

echo
echo "=== 4. Verify no-approval execution is blocked ==="
rm -f approvals/trade-demo-fixed-0001.approved
NO_APPROVAL_OUTPUT="$(python scripts/run_agent.py)"
echo "$NO_APPROVAL_OUTPUT"

echo "$NO_APPROVAL_OUTPUT" | grep -q "BLOCKED: not approved"

echo
echo "=== 5. Verify approval still only dry-runs ==="
touch approvals/trade-demo-fixed-0001.approved
APPROVED_OUTPUT="$(python scripts/run_agent.py)"
echo "$APPROVED_OUTPUT"

echo "$APPROVED_OUTPUT" | grep -q "DRY_RUN"
echo "$APPROVED_OUTPUT" | grep -q "APPROVAL"

echo
echo "=== 6. Clean local runtime files ==="
rm -f approvals/trade-demo-fixed-0001.approved
git restore logs/audit.jsonl logs/state.json 2>/dev/null || true

echo
echo "=== 7. Final git status ==="
git status --short --branch

echo
echo "=== NovaNexus security check passed ==="
