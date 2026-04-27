# NovaNexus

NovaNexus is a security-first AI trading-agent project rebuilt from AI-Agent8004.

Current status: dry-run only. No live exchange execution. No API keys or private keys are implemented.

## Safety stack

LangGraph or strategy output -> strategy registry -> proposal_id validation -> kill switch -> idempotency -> proposal validation -> hash-bound approval -> governance -> Python policy gate -> Rust risk gate -> dry-run only.

## Daily workflow

cd ~/projects/NovaNexus
source .venv/bin/activate
./scripts/reset_runtime.sh
./scripts/security_check.sh

## Tests

pytest -q

## Demo

python scripts/run_agent.py
python scripts/approve_trade_demo.py
python scripts/run_agent.py

## Kill switch

python scripts/killswitch.py status
python scripts/killswitch.py enable
python scripts/killswitch.py disable

## Documentation

See docs/SECURITY_CONTEXT.md, docs/OPERATOR_RUNBOOK.md, and docs/THREAT_MODEL.md.

## Branch

Active recovery branch: local-recovery-work. Do not work directly on main until reviewed.
