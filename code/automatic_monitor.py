
import json
import time
import winreg
from datetime import datetime
from pathlib import Path

# Project paths
BASE_DIR = Path(__file__).resolve().parent
BASELINE_FILE = BASE_DIR / "baseline_all_keys.json"
REPORT_FILE = (
    BASE_DIR.parent / "reports" / "automatic_monitor_report.txt"
)

CHECK_INTERVAL = 60

# Registry locations monitored using read-only access
REGISTRY_LOCATIONS = {
    "HKCU_Run": (
        winreg.HKEY_CURRENT_USER,
        r"Software\Microsoft\Windows\CurrentVersion\Run",
    ),
    "HKCU_RunOnce": (
        winreg.HKEY_CURRENT_USER,
        r"Software\Microsoft\Windows\CurrentVersion\RunOnce",
    ),
    "HKLM_Run": (
        winreg.HKEY_LOCAL_MACHINE,
        r"Software\Microsoft\Windows\CurrentVersion\Run",
    ),
    "HKLM_RunOnce": (
        winreg.HKEY_LOCAL_MACHINE,
        r"Software\Microsoft\Windows\CurrentVersion\RunOnce",
    ),
}


def read_registry_values(location):
    """Read registry values without modifying the registry."""
    if location not in REGISTRY_LOCATIONS:
        raise ValueError(f"Unknown registry location: {location}")

    hive, key_path = REGISTRY_LOCATIONS[location]
    values = {}

    with winreg.OpenKey(
        hive, key_path, 0, winreg.KEY_READ
    ) as key:
        index = 0

        while True:
            try:
                name, data, value_type = winreg.EnumValue(key, index)
            except OSError as error:
                # ERROR_NO_MORE_ITEMS (259) marks the end of enumeration.
                if getattr(error, "winerror", None) == 259:
                    break
                raise

            values[name] = {
                "data": data,
                "type": value_type,
            }
            index += 1

    return values


def load_baseline():
    """Load and validate the existing baseline without modifying it."""
    if not BASELINE_FILE.is_file():
        raise FileNotFoundError(
            f"Baseline file not found: {BASELINE_FILE}"
        )

    with BASELINE_FILE.open("r", encoding="utf-8") as file:
        baseline = json.load(file)

    if not isinstance(baseline, dict):
        raise ValueError("Baseline must contain a JSON object.")

    for location in REGISTRY_LOCATIONS:
        entries = baseline.get(location)

        if not isinstance(entries, dict):
            raise ValueError(
                f"Baseline is missing valid data for {location}."
            )

        for name, entry in entries.items():
            if (
                not isinstance(name, str)
                or not isinstance(entry, dict)
                or "data" not in entry
                or "type" not in entry
            ):
                raise ValueError(
                    f"Invalid baseline entry: {location} / {name}"
                )

    return baseline


def compare_values(baseline, current):
    """Find new, removed, and modified registry entries."""
    changes = []

    for location in REGISTRY_LOCATIONS:
        old_values = baseline[location]
        new_values = current[location]

        for name in sorted(new_values.keys() - old_values.keys()):
            entry = new_values[name]
            changes.append(
                f"NEW | {location} | {name} | "
                f"Data: {entry['data']!r} | Type: {entry['type']}"
            )

        for name in sorted(old_values.keys() - new_values.keys()):
            entry = old_values[name]
            changes.append(
                f"REMOVED | {location} | {name} | "
                f"Previous data: {entry['data']!r} | "
                f"Previous type: {entry['type']}"
            )

        for name in sorted(old_values.keys() & new_values.keys()):
            old_entry = old_values[name]
            new_entry = new_values[name]

            if old_entry != new_entry:
                changes.append(
                    f"MODIFIED | {location} | {name} | "
                    f"Previous data: {old_entry['data']!r} | "
                    f"Current data: {new_entry['data']!r} | "
                    f"Previous type: {old_entry['type']} | "
                    f"Current type: {new_entry['type']}"
                )

    return changes


def save_report(changes):
    """Append detected changes to the report file."""
    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with REPORT_FILE.open("a", encoding="utf-8") as file:
        file.write("\n\n" + "=" * 55 + "\n")
        file.write("WINDOWS REGISTRY CHANGE ALERT\n")
        file.write(f"Check time: {timestamp}\n")
        file.write("=" * 55 + "\n")

        for change in changes:
            file.write(change + "\n")


def main():
    print("Windows Registry Automatic Monitor")
    print("=" * 45)
    print("Registry access: READ ONLY")
    print(f"Check interval: {CHECK_INTERVAL} seconds")
    print(f"Baseline (read only): {BASELINE_FILE}")
    print(f"Report: {REPORT_FILE}")
    print("Press Ctrl + C to stop.\n")

    baseline = load_baseline()
    previous_changes = None

    try:
        while True:
            try:
                # Finish all reads before comparing anything.
                # If one read fails, this cycle is skipped.
                current = {
                    location: read_registry_values(location)
                    for location in REGISTRY_LOCATIONS
                }

                changes = compare_values(baseline, current)
                signature = tuple(changes)

                if changes and signature != previous_changes:
                    timestamp = datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )

                    print("\n" + "=" * 55)
                    print("[ALERT] REGISTRY CHANGES DETECTED")
                    print(f"Time: {timestamp}")
                    print("=" * 55)

                    for change in changes:
                        print(f"  - {change}")

                    save_report(changes)
                    print(f"Report updated: {REPORT_FILE}")

                elif changes:
                    print(
                        "[INFO] The same differences remain. "
                        "No duplicate report created."
                    )
                else:
                    print("[OK] No differences from the original baseline.")

                previous_changes = signature

            except (OSError, ValueError, KeyError, TypeError) as error:
                print(
                    f"[ERROR] Check skipped; "
                    f"no comparison was made: {error}"
                )

            print(f"Next check in {CHECK_INTERVAL} seconds.")
            time.sleep(CHECK_INTERVAL)

    except KeyboardInterrupt:
        print("\nMonitoring stopped safely.")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f"[ERROR] Monitor could not start: {error}")

    print("Program closed.")
