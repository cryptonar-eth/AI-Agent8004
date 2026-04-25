#!/usr/bin/env bash
set -euo pipefail

echo "=== Reset NovaNexus local runtime state ==="

echo
echo "=== Remove local hash-bound approval files ==="
rm -f approvals/*.approved

echo
echo "=== Restore tracked runtime logs/state ==="
git restore logs/audit.jsonl logs/state.json 2>/dev/null || true

echo
echo "=== Runtime reset complete ==="
git status --short --branch
