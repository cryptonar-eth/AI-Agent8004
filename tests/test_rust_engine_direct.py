from __future__ import annotations

import json

import novanexus_engine


def _validate(payload: dict) -> dict:
    raw = novanexus_engine.validate_order_json(json.dumps(payload))
    result = json.loads(raw)

    assert isinstance(result, dict)
    return result


def _safe_payload() -> dict:
    return {
        "proposal_id": "rust-direct-safe-0001",
        "symbol": "ETH-USD",
        "side": "buy",
        "qty": "0.001",
        "price": "2500.00",
        "intent": "DRY_RUN_ORDER",
        "dry_run": True,
        "approved": True,
    }


def test_direct_rust_engine_allows_safe_dry_run() -> None:
    decision = _validate(_safe_payload())

    assert decision["allowed"] is True
    assert decision["engine"] == "novanexus_rust_engine_v0.1"


def test_direct_rust_engine_denies_unapproved_order() -> None:
    payload = _safe_payload()
    payload["approved"] = False

    decision = _validate(payload)

    assert decision["allowed"] is False
    assert "approval" in decision["reason"]


def test_direct_rust_engine_denies_real_trading() -> None:
    payload = _safe_payload()
    payload["dry_run"] = False

    decision = _validate(payload)

    assert decision["allowed"] is False
    assert "real trading" in decision["reason"]


def test_direct_rust_engine_denies_bad_symbol() -> None:
    payload = _safe_payload()
    payload["symbol"] = "BTC-USD"

    decision = _validate(payload)

    assert decision["allowed"] is False
    assert "symbol not allowed" in decision["reason"]


def test_direct_rust_engine_denies_bad_side() -> None:
    payload = _safe_payload()
    payload["side"] = "hold"

    decision = _validate(payload)

    assert decision["allowed"] is False
    assert "side must be buy or sell" in decision["reason"]


def test_direct_rust_engine_denies_missing_price() -> None:
    payload = _safe_payload()
    payload["price"] = None

    decision = _validate(payload)

    assert decision["allowed"] is False
    assert "price required" in decision["reason"]


def test_direct_rust_engine_denies_oversized_quantity() -> None:
    payload = _safe_payload()
    payload["qty"] = "1.0"

    decision = _validate(payload)

    assert decision["allowed"] is False
    assert "quantity exceeds" in decision["reason"]


def test_direct_rust_engine_denies_invalid_json() -> None:
    raw = novanexus_engine.validate_order_json("{not valid json")
    decision = json.loads(raw)

    assert decision["allowed"] is False
    assert decision["proposal_id"] == "unknown"
    assert "invalid JSON" in decision["reason"]


def test_direct_rust_engine_denies_bad_proposal_id() -> None:
    payload = _safe_payload()
    payload["proposal_id"] = "../bad"

    decision = _validate(payload)

    assert decision["allowed"] is False
    assert decision["proposal_id"] == "unknown"
    assert "invalid proposal_id" in decision["reason"]


def test_direct_rust_engine_denies_unknown_fields() -> None:
    payload = _safe_payload()
    payload["unexpected_field"] = "must not be accepted"

    decision = _validate(payload)

    assert decision["allowed"] is False
    assert decision["proposal_id"] == "unknown"
    assert "invalid JSON" in decision["reason"]


def test_direct_rust_engine_denies_zero_quantity() -> None:
    payload = _safe_payload()
    payload["qty"] = "0"

    decision = _validate(payload)

    assert decision["allowed"] is False
    assert "quantity must be positive" in decision["reason"]


def test_direct_rust_engine_denies_negative_quantity() -> None:
    payload = _safe_payload()
    payload["qty"] = "-0.001"

    decision = _validate(payload)

    assert decision["allowed"] is False
    assert "quantity must be positive" in decision["reason"]


def test_direct_rust_engine_denies_zero_price() -> None:
    payload = _safe_payload()
    payload["price"] = "0"

    decision = _validate(payload)

    assert decision["allowed"] is False
    assert "price must be positive" in decision["reason"]


def test_direct_rust_engine_denies_negative_price() -> None:
    payload = _safe_payload()
    payload["price"] = "-2500.00"

    decision = _validate(payload)

    assert decision["allowed"] is False
    assert "price must be positive" in decision["reason"]


def test_direct_rust_engine_denies_missing_required_qty() -> None:
    payload = _safe_payload()
    del payload["qty"]

    decision = _validate(payload)

    assert decision["allowed"] is False
    assert decision["proposal_id"] == "unknown"
    assert "invalid JSON" in decision["reason"]


def test_direct_rust_engine_denies_missing_required_symbol() -> None:
    payload = _safe_payload()
    del payload["symbol"]

    decision = _validate(payload)

    assert decision["allowed"] is False
    assert decision["proposal_id"] == "unknown"
    assert "invalid JSON" in decision["reason"]


def test_direct_rust_engine_denies_non_numeric_quantity_string() -> None:
    payload = _safe_payload()
    payload["qty"] = "not-a-number"

    decision = _validate(payload)

    assert decision["allowed"] is False
    assert decision["proposal_id"] == "unknown"
    assert "invalid JSON" in decision["reason"]


def test_direct_rust_engine_denies_nan_quantity_string() -> None:
    payload = _safe_payload()
    payload["qty"] = "NaN"

    decision = _validate(payload)

    assert decision["allowed"] is False
    assert decision["proposal_id"] == "unknown"
    assert "invalid JSON" in decision["reason"]


def test_direct_rust_engine_denies_infinity_price_string() -> None:
    payload = _safe_payload()
    payload["price"] = "Infinity"

    decision = _validate(payload)

    assert decision["allowed"] is False
    assert decision["proposal_id"] == "unknown"
    assert "invalid JSON" in decision["reason"]


def test_direct_rust_engine_denies_wrong_type_for_quantity() -> None:
    payload = _safe_payload()
    payload["qty"] = {"bad": "type"}

    decision = _validate(payload)

    assert decision["allowed"] is False
    assert decision["proposal_id"] == "unknown"
    assert "invalid JSON" in decision["reason"]


def test_direct_rust_engine_denies_real_order_intent_even_if_dry_run_true() -> None:
    payload = _safe_payload()
    payload["intent"] = "REAL_ORDER"
    payload["dry_run"] = True

    decision = _validate(payload)

    assert decision["allowed"] is False
    assert "DRY_RUN_ORDER" in decision["reason"]


def test_direct_rust_engine_denies_blank_intent() -> None:
    payload = _safe_payload()
    payload["intent"] = ""

    decision = _validate(payload)

    assert decision["allowed"] is False
    assert "DRY_RUN_ORDER" in decision["reason"]


def test_direct_rust_engine_denies_wrong_case_intent() -> None:
    payload = _safe_payload()
    payload["intent"] = "dry_run_order"

    decision = _validate(payload)

    assert decision["allowed"] is False
    assert "DRY_RUN_ORDER" in decision["reason"]


def test_direct_rust_engine_denies_missing_required_intent() -> None:
    payload = _safe_payload()
    del payload["intent"]

    decision = _validate(payload)

    assert decision["allowed"] is False
    assert decision["proposal_id"] == "unknown"
    assert "invalid JSON" in decision["reason"]


def test_direct_rust_engine_denies_wrong_type_for_intent() -> None:
    payload = _safe_payload()
    payload["intent"] = {"bad": "type"}

    decision = _validate(payload)

    assert decision["allowed"] is False
    assert decision["proposal_id"] == "unknown"
    assert "invalid JSON" in decision["reason"]


def test_direct_rust_engine_denies_missing_required_dry_run() -> None:
    payload = _safe_payload()
    del payload["dry_run"]

    decision = _validate(payload)

    assert decision["allowed"] is False
    assert decision["proposal_id"] == "unknown"
    assert "invalid JSON" in decision["reason"]


def test_direct_rust_engine_denies_missing_required_approved() -> None:
    payload = _safe_payload()
    del payload["approved"]

    decision = _validate(payload)

    assert decision["allowed"] is False
    assert decision["proposal_id"] == "unknown"
    assert "invalid JSON" in decision["reason"]


def test_direct_rust_engine_denies_wrong_type_for_dry_run() -> None:
    payload = _safe_payload()
    payload["dry_run"] = "true"

    decision = _validate(payload)

    assert decision["allowed"] is False
    assert decision["proposal_id"] == "unknown"
    assert "invalid JSON" in decision["reason"]


def test_direct_rust_engine_denies_wrong_type_for_approved() -> None:
    payload = _safe_payload()
    payload["approved"] = "true"

    decision = _validate(payload)

    assert decision["allowed"] is False
    assert decision["proposal_id"] == "unknown"
    assert "invalid JSON" in decision["reason"]


def test_direct_rust_engine_denies_dry_run_false_even_with_approval() -> None:
    payload = _safe_payload()
    payload["dry_run"] = False
    payload["approved"] = True

    decision = _validate(payload)

    assert decision["allowed"] is False
    assert "real trading" in decision["reason"]


def test_direct_rust_engine_denies_approved_false_even_with_dry_run() -> None:
    payload = _safe_payload()
    payload["dry_run"] = True
    payload["approved"] = False

    decision = _validate(payload)

    assert decision["allowed"] is False
    assert "approval" in decision["reason"]
