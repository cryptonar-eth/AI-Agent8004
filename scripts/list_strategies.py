from __future__ import annotations

from agent.strategies.registry import allowed_strategy_names, build_strategies


def main() -> None:
    print("ALLOWED STRATEGIES:")
    for name in allowed_strategy_names():
        print(f"- {name}")

    print("\nDEFAULT STRATEGIES:")
    for strategy in build_strategies():
        print(f"- {strategy.name}")


if __name__ == "__main__":
    main()
