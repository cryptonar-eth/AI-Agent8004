from __future__ import annotations

import tomllib
from pathlib import Path


def test_ci_runs_security_check_script() -> None:
    workflow = Path(".github/workflows/ci.yml").read_text(encoding="utf-8")

    assert "./scripts/security_check.sh" in workflow


def test_ci_uses_pinned_rust_toolchain_action() -> None:
    workflow = Path(".github/workflows/ci.yml").read_text(encoding="utf-8")

    assert "dtolnay/rust-toolchain@1.95.0" in workflow
    assert "dtolnay/rust-toolchain@stable" not in workflow


def test_rust_toolchain_file_pins_expected_version() -> None:
    data = tomllib.loads(Path("rust-toolchain.toml").read_text(encoding="utf-8"))

    assert data["toolchain"]["channel"] == "1.95.0"
    assert data["toolchain"]["profile"] == "minimal"
    assert "rustfmt" in data["toolchain"]["components"]


def test_security_check_runs_rust_format_check() -> None:
    script = Path("scripts/security_check.sh").read_text(encoding="utf-8")

    assert "cargo fmt --manifest-path engine/novanexus_engine/Cargo.toml -- --check" in script


def test_security_check_runs_native_rust_tests() -> None:
    script = Path("scripts/security_check.sh").read_text(encoding="utf-8")

    assert "cargo test --manifest-path engine/novanexus_engine/Cargo.toml" in script


def test_security_check_runs_rust_clippy() -> None:
    script = Path("scripts/security_check.sh").read_text(encoding="utf-8")

    assert "cargo clippy --manifest-path engine/novanexus_engine/Cargo.toml --all-targets -- -D warnings" in script


def test_rust_toolchain_file_includes_clippy() -> None:
    data = tomllib.loads(Path("rust-toolchain.toml").read_text(encoding="utf-8"))

    assert "clippy" in data["toolchain"]["components"]


def test_ci_installs_rustfmt_and_clippy_components() -> None:
    workflow = Path(".github/workflows/ci.yml").read_text(encoding="utf-8")

    assert "components: rustfmt, clippy" in workflow
