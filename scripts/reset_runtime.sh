#!/usr/bin/env bash
set -euo pipefail

echo "=== Reset NovaNexus local runtime state ==="

echo
echo "=== Remove local hash-bound approval files ==="
rm -f approvals/*.approved

echo
echo "=== Remove local runtime logs/state ==="
rm -f logs/audit.jsonl logs/state.json

echo
echo "=== Runtime reset complete ==="
git status --short --branch
