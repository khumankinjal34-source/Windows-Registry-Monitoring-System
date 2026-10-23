
"""Test the real comparison function using fake data only."""

import sys
from pathlib import Path

CODE_DIR = Path(__file__).resolve().parents[1] / "code"
sys.path.insert(0, str(CODE_DIR))

from security_settings_monitor_v2 import compare_settings, SECURITY_SETTINGS

def main():
    # Fake reference data. No real Registry values are used.
    reference = {
        name: {"status": "NOT_FOUND"}
        for name in SECURITY_SETTINGS
    }

    # Simulate one changed setting.
    current = {
        name: {"status": "NOT_FOUND"}
        for name in SECURITY_SETTINGS
    }

    current["Defender_DisableRealtimeMonitoring"] = {
        "status": "FOUND",
        "value": 1,
        "type": 4,
    }

    print("Testing the actual security monitor comparison function")
    print("=======================================================")

    changes = compare_settings(reference, current)

    for change in changes:
        print(change)

    assert len(changes) == 1, "Expected exactly one detected change."
    assert changes[0].startswith(
        "CHANGED | Defender_DisableRealtimeMonitoring"
    ), "The wrong setting was reported."

    print("\nPASS: The actual comparison function detected the change.")


if __name__ == "__main__":
    main()
