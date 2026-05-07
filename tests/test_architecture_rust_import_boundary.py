from __future__ import annotations

import ast
from pathlib import Path


AGENT_ROOT = Path("agent")
ALLOWED_DIRECT_RUST_ENGINE_IMPORTS = {
    Path("agent/engine/rust_guard.py"),
}


def _agent_python_files() -> list[Path]:
    return [
        path
        for path in AGENT_ROOT.rglob("*.py")
        if "__pycache__" not in path.parts
    ]


def test_only_rust_guard_imports_novanexus_engine_in_agent_code() -> None:
    offenders: list[str] = []

    for path in _agent_python_files():
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name == "novanexus_engine" and path not in ALLOWED_DIRECT_RUST_ENGINE_IMPORTS:
                        offenders.append(f"{path}:{node.lineno}: import {alias.name}")

            if isinstance(node, ast.ImportFrom):
                if node.module == "novanexus_engine" and path not in ALLOWED_DIRECT_RUST_ENGINE_IMPORTS:
                    offenders.append(f"{path}:{node.lineno}: from {node.module}")

    assert offenders == []


def test_executor_uses_rust_guard_not_direct_rust_engine() -> None:
    source = Path("agent/trading/execution.py").read_text(encoding="utf-8")

    assert "from agent.engine.rust_guard import RustOrderProposal, validate_with_rust" in source
    assert "import novanexus_engine" not in source
    assert "from novanexus_engine" not in source
