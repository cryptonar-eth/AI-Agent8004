from __future__ import annotations

import ast
from pathlib import Path


SOURCE_ROOTS = (
    Path("agent"),
    Path("scripts"),
)

FORBIDDEN_LIVE_ORDER_CALLS = {
    "create_order",
    "place_order",
    "submit_order",
    "send_order",
    "market_order",
    "limit_order",
}

FORBIDDEN_NETWORK_EXCHANGE_IMPORT_PREFIXES = {
    "ccxt",
    "binance",
    "coinbase",
    "kraken",
    "kucoin",
    "bybit",
    "okx",
}

FORBIDDEN_SECRET_FUNCTION_CALLS = {
    "from_key",
    "from_mnemonic",
    "sign_transaction",
    "sign_message",
}


def _source_files() -> list[Path]:
    files: list[Path] = []

    for root in SOURCE_ROOTS:
        if not root.exists():
            continue

        files.extend(
            path
            for path in root.rglob("*.py")
            if "__pycache__" not in path.parts
        )

    return files


def _parse(path: Path) -> ast.AST:
    return ast.parse(path.read_text(encoding="utf-8"), filename=str(path))


def _call_name(node: ast.Call) -> str | None:
    func = node.func

    if isinstance(func, ast.Name):
        return func.id

    if isinstance(func, ast.Attribute):
        return func.attr

    return None


def test_no_live_exchange_order_calls_in_agent_or_scripts() -> None:
    offenders: list[str] = []

    for path in _source_files():
        tree = _parse(path)

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                name = _call_name(node)

                if name in FORBIDDEN_LIVE_ORDER_CALLS:
                    offenders.append(f"{path}:{node.lineno}: call {name}")

    assert offenders == []


def test_no_exchange_sdk_imports_in_agent_or_scripts() -> None:
    offenders: list[str] = []

    for path in _source_files():
        tree = _parse(path)

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    root_name = alias.name.split(".")[0].lower()
                    if root_name in FORBIDDEN_NETWORK_EXCHANGE_IMPORT_PREFIXES:
                        offenders.append(f"{path}:{node.lineno}: import {alias.name}")

            if isinstance(node, ast.ImportFrom) and node.module:
                root_name = node.module.split(".")[0].lower()
                if root_name in FORBIDDEN_NETWORK_EXCHANGE_IMPORT_PREFIXES:
                    offenders.append(f"{path}:{node.lineno}: from {node.module}")

    assert offenders == []


def test_no_private_key_or_seed_signing_calls_in_agent_or_scripts() -> None:
    offenders: list[str] = []

    for path in _source_files():
        tree = _parse(path)

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                name = _call_name(node)

                if name in FORBIDDEN_SECRET_FUNCTION_CALLS:
                    offenders.append(f"{path}:{node.lineno}: call {name}")

    assert offenders == []
