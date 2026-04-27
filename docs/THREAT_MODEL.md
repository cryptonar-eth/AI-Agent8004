# NovaNexus Threat Model

## Purpose

NovaNexus is a security-first AI trading-agent project. The current system is intentionally dry-run only. This threat model documents assets, trust boundaries, attack paths, and current controls before any real exchange/API/key integration is added.

## Current Status

Live trading is disabled.

Exchange API integration is not implemented.

Private key handling is not implemented.

Wallet seed/mnemonic handling is not implemented.

No real order should be possible from the current codebase.

## Protected Assets

The project must protect:

- trading capital
- future exchange API keys
- future wallet/private keys
- strategy logic
- local approval files
- audit logs
- runtime state
- GitHub repository integrity
- policy files under config/
- Rust execution/risk boundary
- local development environment

## Trust Boundaries

### Untrusted

The following are treated as untrusted:

- LLM output
- LangGraph state
- strategy-generated proposals
- market data input
- user-editable runtime files
- environment variables
- future API responses
- future web/dashboard requests
- future exchange responses

### Trusted Only After Validation

The following are trusted only after validation:

- proposal IDs
- proposal payloads
- strategy names
- risk policy
- strategy policy
- approval files
- market snapshots

### High-Trust Boundary

The highest-trust application boundary is:

Python executor choke point
-> Python policy gate
-> Rust risk gate

Rust remains the final risk validator before any future execution layer.

## Current Execution Path

LangGraph or strategy output
-> explicit strategy registry
-> proposal_id validation
-> kill switch
-> state/idempotency
-> proposal payload validation
-> hash-bound approval check
-> governance check
-> Python policy gate
-> Rust risk gate
-> dry-run only

## Current Controls

### Kill Switch

Execution is blocked if:

approvals/KILL_SWITCH

exists.

The kill switch has tests and a control script:

python scripts/killswitch.py status
python scripts/killswitch.py enable
python scripts/killswitch.py disable

### Hash-Bound Approvals

Approvals are bound to:

- proposal_id
- proposal type
- payload
- reason

A reused approval file does not approve a changed payload.

### Proposal Shape Validation

Proposal payloads must pass strict shape validation before approval and execution.

Invalid side, quantity, price, bundle leg, or unsupported type is blocked.

### Strategy Registry

Strategies must be explicitly allowlisted.

Unknown strategies are rejected.

Default strategy policy enables only:

smoke_test

### Strategy Policy

Strategy selection is controlled by:

config/strategy_policy.example.json

The policy loader fails closed on invalid version, empty strategy list, duplicate strategies, or blank strategy names.

### Risk Policy

Risk rules are controlled by:

config/risk_policy.example.json

Current policy:

- dry_run_only
- ETH-USD only
- buy/sell only
- max qty 0.01
- DRY_RUN_ORDER intent only
- manual approval required
- price required
- live trading disabled

### Python Policy Gate

The Python policy gate blocks bad symbols, bad sides, missing approval, missing price, oversized quantity, live trading, and unsupported intent before Rust is called.

### Rust Risk Gate

The Rust risk engine enforces final dry-run risk rules.

Current Rust module:

engine/novanexus_engine

Current Python bridge:

agent/engine/rust_guard.py

### Audit Redaction

Audit logging redacts sensitive key fragments such as:

- api_key
- secret
- token
- password
- private_key
- mnemonic
- seed
- authorization
- auth

### Runtime Files Are Not Tracked

The following are runtime-only and ignored by Git:

- approvals/*.approved
- approvals/KILL_SWITCH
- logs/
- Rust target build output
- local build dist output

## Main Threats

### LLM Generates Dangerous Proposal

Risk:

An LLM or agent node proposes a real trade, oversized trade, unsupported symbol, or malformed payload.

Controls:

- proposal shape validation
- strategy registry
- risk policy
- Python policy gate
- Rust risk gate
- dry-run only
- manual approval

### Approval Replay

Risk:

A proposal ID is approved, then reused with changed payload.

Controls:

- hash-bound approval
- proposal hash check
- idempotency

### Secret Leakage Into Logs

Risk:

Future API keys, private keys, tokens, or mnemonics appear in audit logs.

Controls:

- audit redaction
- no secrets committed
- secret-file scan in security_check.sh

### Runtime Files Accidentally Committed

Risk:

Approval files, logs, or state get committed to GitHub.

Controls:

- .gitignore
- security_check.sh
- reset_runtime.sh
- Git status review before commit

### Unknown Strategy Execution

Risk:

Future code loads a random or malicious strategy by name.

Controls:

- controlled strategy registry
- strategy policy validation
- tests for unknown strategy rejection

### Live Trading Accidentally Enabled

Risk:

A config or environment setting enables real order flow.

Controls:

- dry_run default
- risk policy requires dry_run_only
- live_trading_enabled must be false
- Rust rejects dry_run=false
- executor live path not implemented
- tests verify real execution is blocked

## Not Yet Implemented

The following must not be added without a separate security review:

- real exchange API integration
- API key storage
- wallet/private key signing
- real order placement
- autonomous trading loop
- dashboard control plane
- networked market data
- cloud deployment
- multi-user auth
- remote approval workflow

## Required Before Any Real Exchange Integration

Before adding exchange sandbox or live APIs, NovaNexus must have:

- CI passing security_check.sh
- threat model reviewed
- key-management design
- sandbox-only exchange adapter
- no live keys
- circuit breakers
- rate limits
- order idempotency
- exchange error handling
- audit log review
- manual release checklist
- separate branch and pull request

## Current Operator Rule

Every future change must answer:

Can this change cause real money movement, key exposure, network exposure, approval bypass, or loss of control?

If yes, the change must be blocked, mocked, sandboxed, tested, or reviewed before implementation.
