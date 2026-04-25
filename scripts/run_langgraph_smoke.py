from __future__ import annotations

from agent.brain.langgraph_brain import run_brain_once


def main() -> None:
    result = run_brain_once()
    print("LANGGRAPH RESULT:")
    print(result)


if __name__ == "__main__":
    main()
