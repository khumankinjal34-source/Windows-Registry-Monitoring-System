
import json
import winreg
from pathlib import Path

# Windows Registry Change Monitoring System
# Safely create an initial snapshot of four startup Registry keys.

BASE_DIR = Path(__file__).resolve().parent
BASELINE_FILE = BASE_DIR / "baseline_all_keys.json"

registry_keys = [
    ("HKCU_Run", winreg.HKEY_CURRENT_USER,
     r"Software\Microsoft\Windows\CurrentVersion\Run"),
    ("HKCU_RunOnce", winreg.HKEY_CURRENT_USER,
     r"Software\Microsoft\Windows\CurrentVersion\RunOnce"),
    ("HKLM_Run", winreg.HKEY_LOCAL_MACHINE,
     r"Software\Microsoft\Windows\CurrentVersion\Run"),
    ("HKLM_RunOnce", winreg.HKEY_LOCAL_MACHINE,
     r"Software\Microsoft\Windows\CurrentVersion\RunOnce"),
]


def read_registry_values(root_key, sub_key):
    values = {}

    # KEY_READ allows reading; it does not write or delete Registry values.
    with winreg.OpenKey(root_key, sub_key, 0, winreg.KEY_READ) as key:
        index = 0

        while True:
            try:
                name, value, value_type = winreg.EnumValue(key, index)
            except OSError as error:
                # Windows error 259 means no more values to enumerate.
                if getattr(error, "winerror", None) == 259:
                    break
                raise

            values[name] = {
                "data": value,
                "type": value_type,
            }
            index += 1

    return values


def collect_registry_snapshot():
    snapshot = {}

    for name, root_key, sub_key in registry_keys:
        print(f"Reading: {name}")
        snapshot[name] = read_registry_values(root_key, sub_key)
        print(f"Entries found: {len(snapshot[name])}")

    return snapshot


def save_baseline(snapshot):
    # Exclusive creation: never overwrite an existing baseline.
    with BASELINE_FILE.open("x", encoding="utf-8") as file:
        json.dump(snapshot, file, indent=4)

    print(f"\nBaseline saved to: {BASELINE_FILE}")


if __name__ == "__main__":
    print("Windows Registry Change Monitoring System")
    print("==========================================")

    if BASELINE_FILE.exists():
        print("\nSTOP: A baseline file already exists.")
        print("No Registry values were read, and no file was changed.")
        print(f"Existing baseline: {BASELINE_FILE}")
    else:
        try:
            print("\nCollecting the initial Registry snapshot...")
            snapshot = collect_registry_snapshot()
            save_baseline(snapshot)
            print("\nInitial Registry baseline created successfully.")

        except (OSError, PermissionError, json.JSONDecodeError) as error:
            print("\nERROR: Could not create the baseline safely.")
            print(f"Details: {error}")
            print("No baseline should be used unless collection succeeds.")
