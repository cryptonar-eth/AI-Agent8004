from __future__ import annotations

import ast
from pathlib import Path


AGENT_ROOT = Path("agent")


def _agent_python_files() -> list[Path]:
    return [
        path
        for path in AGENT_ROOT.rglob("*.py")
        if "__pycache__" not in path.parts
    ]


def test_only_trading_execution_defines_executor_class() -> None:
    offenders: list[str] = []

    for path in _agent_python_files():
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == "Executor":
                if path != Path("agent/trading/execution.py"):
                    offenders.append(f"{path}:{node.lineno}: class Executor")

    assert offenders == []


def test_executor_file_contains_single_executor_class() -> None:
    path = Path("agent/trading/execution.py")
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))

    executor_classes = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.ClassDef) and node.name == "Executor"
    ]

    assert len(executor_classes) == 1


def test_no_agent_module_defines_live_execution_function_names() -> None:
    forbidden_names = {
        "execute_live",
        "live_execute",
        "place_live_order",
        "send_live_order",
        "submit_live_order",
    }

    offenders: list[str] = []

    for path in _agent_python_files():
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if node.name in forbidden_names:
                    offenders.append(f"{path}:{node.lineno}: function {node.name}")

    assert offenders == []
