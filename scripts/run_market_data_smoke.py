from __future__ import annotations

from agent.data.market_data import StaticMarketDataProvider


def main() -> None:
    provider = StaticMarketDataProvider({"ETH-USD": 3500.0})
    snapshot = provider.get_snapshot("ETH-USD")

    print("MARKET DATA SNAPSHOT:")
    print(snapshot)


if __name__ == "__main__":
    main()
