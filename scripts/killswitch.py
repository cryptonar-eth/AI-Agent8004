from __future__ import annotations

import sys

from agent.ops.killswitch import KILLSWITCH_FILE, is_killed, kill, revive


def status() -> None:
    if is_killed():
        print(f"Kill switch status: ENABLED ({KILLSWITCH_FILE})")
    else:
        print(f"Kill switch status: disabled ({KILLSWITCH_FILE})")


def main() -> None:
    if len(sys.argv) != 2 or sys.argv[1] not in {"enable", "disable", "status"}:
        print("Usage: python scripts/killswitch.py [enable|disable|status]")
        raise SystemExit(2)

    command = sys.argv[1]

    if command == "enable":
        kill("manual emergency stop enabled")
        print(f"Kill switch enabled: {KILLSWITCH_FILE}")
    elif command == "disable":
        revive()
        print(f"Kill switch disabled: {KILLSWITCH_FILE}")
    else:
        status()


if __name__ == "__main__":
    main()
