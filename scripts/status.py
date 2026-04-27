from __future__ import annotations

import json
import subprocess

import novanexus_engine

from agent.config.risk_policy import load_risk_policy
from agent.config.strategy_policy import load_strategy_policy
from agent.ops.killswitch import is_killed


def _run(cmd: list[str]) -> str:
    return subprocess.check_output(cmd, text=True).strip()


def main() -> None:
    print("=== NovaNexus Safety Status ===")

    print()
    print("Git:")
    print(_run(["git", "status", "--short", "--branch"]))

    print()
    print("Risk policy:")
    risk_policy = load_risk_policy()
    print(risk_policy)

    print()
    print("Strategy policy:")
    strategy_policy = load_strategy_policy()
    print(strategy_policy)

    print()
    print("Kill switch:")
    print("ENABLED" if is_killed() else "disabled")

    print()
    print("Rust engine:")
    payload = {
        "proposal_id": "status-check-0001",
        "symbol": "ETH-USD",
        "side": "buy",
        "qty": "0.001",
        "price": "2500.00",
        "intent": "DRY_RUN_ORDER",
        "dry_run": True,
        "approved": True,
    }
    decision = json.loads(novanexus_engine.validate_order_json(json.dumps(payload)))
    print(decision)

    print()
    print("Safety summary:")
    print("- live trading: disabled")
    print("- exchange execution: not implemented")
    print("- private keys: not implemented")
    print("- approvals: hash-bound")
    print("- final risk gate: Rust")


if __name__ == "__main__":
    main()
