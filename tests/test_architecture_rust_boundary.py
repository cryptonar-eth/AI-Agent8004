from __future__ import annotations

from pathlib import Path


def test_executor_imports_rust_guard() -> None:
    source = Path("agent/trading/execution.py").read_text(encoding="utf-8")

    assert "from agent.engine.rust_guard import RustOrderProposal, validate_with_rust" in source


def test_executor_calls_validate_with_rust() -> None:
    source = Path("agent/trading/execution.py").read_text(encoding="utf-8")

    assert "validate_with_rust(" in source


def test_executor_constructs_rust_order_proposal() -> None:
    source = Path("agent/trading/execution.py").read_text(encoding="utf-8")

    assert "RustOrderProposal(" in source


def test_executor_does_not_contain_live_exchange_order_call_keywords() -> None:
    source = Path("agent/trading/execution.py").read_text(encoding="utf-8").lower()

    forbidden = [
        "create_order",
        "place_order",
        "send_order",
        "submit_order",
        "market_order",
        "limit_order",
    ]

    for keyword in forbidden:
        assert keyword not in source
