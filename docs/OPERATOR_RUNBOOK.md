# NovaNexus Operator Runbook

## Active Branch

Current recovery branch:

local-recovery-work

Do not work directly on main until the recovery branch is reviewed and intentionally merged.

## Daily Safety Check

Before every commit or push, run:

    cd ~/projects/NovaNexus
    source .venv/bin/activate
    ./scripts/security_check.sh

Expected result:

    NovaNexus security check passed

## Run Tests

    pytest -q

## Run LangGraph Smoke Test

    python scripts/run_langgraph_smoke.py

Expected behavior: LangGraph creates a proposal, then the executor blocks it because no hash-bound approval exists.

## Run Demo Agent Without Approval

    rm -f approvals/trade-demo-fixed-0001.approved
    python scripts/run_agent.py

Expected behavior:

    [EXEC] BLOCKED: not approved

## Create Hash-Bound Demo Approval

    python scripts/approve_trade_demo.py

This writes:

    approvals/trade-demo-fixed-0001.approved

The approval is bound to the exact proposal payload hash.

## Run Demo Agent With Approval

    python scripts/run_agent.py

Expected behavior:

    [EXEC] DRY_RUN (APPROVAL) TRADE

This is still not real trading.

## Clean Runtime Files

    rm -f approvals/trade-demo-fixed-0001.approved
    rm -f approvals/langgraph-smoke-0001.approved
    git restore logs/audit.jsonl logs/state.json 2>/dev/null || true

## Clean Git Status

    git status --short --branch

Expected clean state:

    ## local-recovery-work...origin/local-recovery-work

## Never Commit

Never commit:

- .env
- .venv
- private keys
- API keys
- wallet seeds
- mnemonic phrases
- Rust target build output
- runtime approval files
- runtime logs/state unless intentionally creating test fixtures

## Current Safety Stack

Execution path:

LangGraph or strategy output
-> proposal_id validation
-> kill switch
-> state/idempotency
-> proposal payload validation
-> hash-bound approval check
-> governance check
-> Python policy gate
-> Rust risk gate
-> dry-run only

## Live Trading Status

Live trading is disabled.

Exchange API integration is not implemented.

Private key handling is not implemented.

No real orders should be possible from the current codebase.
