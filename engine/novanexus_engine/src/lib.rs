use pyo3::prelude::*;
use rust_decimal::Decimal;
use serde::{Deserialize, Serialize};
use std::str::FromStr;

#[derive(Debug, Deserialize)]
#[serde(deny_unknown_fields)]
struct OrderProposal {
    proposal_id: String,
    symbol: String,
    side: String,
    qty: Decimal,
    price: Option<Decimal>,
    intent: String,
    dry_run: bool,
    approved: bool,
}

#[derive(Debug, Serialize)]
struct RiskDecision {
    allowed: bool,
    reason: String,
    proposal_id: String,
    engine: String,
}

fn decision(allowed: bool, proposal_id: String, reason: &str) -> String {
    serde_json::to_string(&RiskDecision {
        allowed,
        reason: reason.to_string(),
        proposal_id,
        engine: "novanexus_rust_engine_v0.1".to_string(),
    })
    .expect("risk decision serialization must not fail")
}

fn is_safe_proposal_id(proposal_id: &str) -> bool {
    let len = proposal_id.len();

    if !(8..=128).contains(&len) {
        return false;
    }

    proposal_id
        .bytes()
        .all(|b| b.is_ascii_alphanumeric() || b == b'_' || b == b'-')
}

#[pyfunction]
fn validate_order_json(order_json: &str) -> PyResult<String> {
    let proposal: OrderProposal = match serde_json::from_str(order_json) {
        Ok(p) => p,
        Err(_) => {
            return Ok(decision(
                false,
                "unknown".to_string(),
                "invalid JSON proposal",
            ))
        }
    };

    if !is_safe_proposal_id(&proposal.proposal_id) {
        return Ok(decision(
            false,
            "unknown".to_string(),
            "invalid proposal_id format",
        ));
    }

    if proposal.symbol != "ETH-USD" {
        return Ok(decision(
            false,
            proposal.proposal_id,
            "symbol not allowed by Rust risk policy",
        ));
    }

    if proposal.side != "buy" && proposal.side != "sell" {
        return Ok(decision(false, proposal.proposal_id, "side must be buy or sell"));
    }

    if proposal.qty <= Decimal::ZERO {
        return Ok(decision(false, proposal.proposal_id, "quantity must be positive"));
    }

    let max_qty = Decimal::from_str("0.01").expect("valid decimal literal");
    if proposal.qty > max_qty {
        return Ok(decision(
            false,
            proposal.proposal_id,
            "quantity exceeds max_qty=0.01",
        ));
    }

    if proposal.intent != "DRY_RUN_ORDER" {
        return Ok(decision(
            false,
            proposal.proposal_id,
            "only DRY_RUN_ORDER intent is allowed",
        ));
    }

    if !proposal.dry_run {
        return Ok(decision(
            false,
            proposal.proposal_id,
            "real trading is disabled at Rust engine level",
        ));
    }

    if !proposal.approved {
        return Ok(decision(false, proposal.proposal_id, "manual approval missing"));
    }

    let price = match proposal.price {
        Some(price) => price,
        None => {
            return Ok(decision(
                false,
                proposal.proposal_id,
                "price required for deterministic dry-run validation",
            ))
        }
    };

    if price <= Decimal::ZERO {
        return Ok(decision(
            false,
            proposal.proposal_id,
            "price must be positive",
        ));
    }

    Ok(decision(
        true,
        proposal.proposal_id,
        "dry-run proposal passed Rust risk policy",
    ))
}

#[pymodule]
fn novanexus_engine(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(validate_order_json, m)?)?;
    Ok(())
}
