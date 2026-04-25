from __future__ import annotations

import pytest

from agent.data.market_data import MarketTick, StaticMarketDataProvider, validate_market_tick


def test_static_market_data_provider_returns_valid_snapshot() -> None:
    provider = StaticMarketDataProvider({"ETH-USD": 3500.0})

    snapshot = provider.get_snapshot("ETH-USD")

    assert snapshot.symbol == "ETH-USD"
    assert snapshot.mid == 3500.0
    assert snapshot.ts_ms > 0
    assert snapshot.meta == {"source": "static"}


def test_market_data_denies_unapproved_symbol() -> None:
    provider = StaticMarketDataProvider({"BTC-USD": 100000.0})

    with pytest.raises(ValueError, match="not allowed"):
        provider.get_snapshot("BTC-USD")


def test_market_data_denies_non_positive_price() -> None:
    with pytest.raises(ValueError, match="positive"):
        validate_market_tick(
            MarketTick(
                symbol="ETH-USD",
                mid=0.0,
                ts_ms=1,
                source="static",
            )
        )


def test_market_data_denies_non_finite_price() -> None:
    with pytest.raises(ValueError, match="finite"):
        validate_market_tick(
            MarketTick(
                symbol="ETH-USD",
                mid=float("nan"),
                ts_ms=1,
                source="static",
            )
        )
