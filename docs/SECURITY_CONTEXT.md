# NovaNexus Security Context

## Current Project Identity

NovaNexus was originally named AI-Agent8004. The project is being rebuilt on Ubuntu after the original Windows development environment was lost.

The current recovery branch is:

local-recovery-work

The main branch must not be touched until the recovery branch is stable, tested, and reviewed.

## Security-First Rule

Security is the first priority for every design, implementation, dependency, runtime decision, and future feature.

The agent must fail closed.

No real trading is allowed until the project has complete tests, review, key management, exchange sandbox validation, circuit breakers, monitoring, and a manual release decision.

## Current Architecture

Python is the AI brain and orchestration layer.

Python responsibilities:
- strategy logic
- proposal creation
- RAG and memory later
- LangGraph orchestration later
- tool calling later
- audit/log coordination
- human approval workflow

Rust is the safety and execution core.

Rust responsibilities:
- final risk validation
- order validation
- max size enforcement
- allowed-symbol enforcement
- dry-run enforcement
- future signing boundary
- future exchange execution boundary
- future circuit breakers

Current Rust module:

engine/novanexus_engine

Current Python bridge:

agent/engine/rust_guard.py

Current integrated execution path:

Python proposal
-> proposal_id validation
-> kill switch check
-> idempotency check
-> manual approval check
-> Python governance check
-> Python risk percentage check
-> Rust risk gate
-> audit log
-> dry-run only

## Current Safety Gates

The following gates are active:

1. Manual approval required unless explicit autonomy flags are enabled.
2. Kill switch blocks execution.
3. Proposal IDs are validated against a strict safe format.
4. Idempotency prevents executing the same proposal twice.
5. Governance restricts allowed trade behavior.
6. Python risk state checks trade exposure.
7. Rust risk gate rejects unsafe proposals.
8. Dry-run mode is enabled by default.
9. Live execution is not implemented.
10. No exchange API keys or wallet keys are configured.

## Rust Risk Gate Current Policy

Current allowed symbol:

ETH-USD

Current max quantity:

0.01

Current allowed intent:

DRY_RUN_ORDER

Current requirements:
- dry_run must be true
- approved must be true
- side must be buy or sell
- qty must be positive
- price must be present
- symbol must be allowed

Any violation is denied.

## Non-Negotiable Build Rules

Do not add real exchange execution yet.

Do not add API keys.

Do not add private keys.

Do not add wallet seed phrases.

Do not commit .env files.

Do not commit .venv.

Do not commit Rust target/ build output.

Do not commit runtime approval files.

Do not commit runtime logs/state unless intentionally preserving a test fixture.

Do not merge to main until tests pass.

Do not add a dashboard until the core safety tests exist.

Do not add autonomous loops until dry-run tests and circuit breakers exist.

Python/LLM output is untrusted. Rust must remain the final execution gate.

## Current Good Checkpoints

The following commits exist on local-recovery-work:

- Add Rust risk engine for NovaNexus
- Add Python bridge for Rust risk engine
- Integrate Rust risk gate into trade executor

The branch has been pushed to GitHub:

origin/local-recovery-work

## Next Development Milestones

1. Add pytest safety tests.
2. Test Rust risk allowed/denied decisions.
3. Test executor no-approval block.
4. Test executor approval dry-run path.
5. Test real-trading denial.
6. Add README recovery/build instructions.
7. Add GitHub Actions CI.
8. Add LangGraph only after safety tests pass.
9. Add market data in read-only mode.
10. Add exchange sandbox only after another security review.

## Current Operating Rule

Every future feature must pass this question:

Can this change cause real money movement, key exposure, network exposure, or loss of control?

If yes, it must be blocked, mocked, sandboxed, or reviewed before implementation.
