
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

# Allow this test to import the script from the sibling code folder.
CODE_DIR = Path(__file__).resolve().parents[1] / "code"
sys.path.insert(0, str(CODE_DIR))

import automatic_monitor


print("Testing Registry enumeration failure...")

fake_key = MagicMock()
fake_key.__enter__.return_value = fake_key
fake_key.__exit__.return_value = False

with patch(
    "automatic_monitor.winreg.OpenKey",
    return_value=fake_key,
):
    with patch(
        "automatic_monitor.winreg.EnumValue",
        side_effect=OSError(
            "Simulated enumeration failure",
        ),
    ):
        try:
            automatic_monitor.read_registry_values("HKCU_Run")
        except OSError as error:
            print("PASS: Enumeration error was raised safely.")
            print(f"Message: {error}")
        else:
            print("FAIL: Enumeration error was treated as normal completion.")
