
import json
import winreg
from datetime import datetime
from pathlib import Path

# Project paths
BASE_DIR = Path(__file__).resolve().parent
BASELINE_FILE = BASE_DIR / "baseline_all_keys.json"
REPORT_FILE = BASE_DIR / "change_report_all_keys.txt"

# Registry locations monitored with read-only access
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


def load_baseline():
    """Load and validate the existing baseline without modifying it."""
    if not BASELINE_FILE.is_file():
        raise FileNotFoundError(
            f"Baseline file not found: {BASELINE_FILE}"
        )

    with BASELINE_FILE.open("r", encoding="utf-8") as file:
        baseline = json.load(file)

    if not isinstance(baseline, dict):
        raise ValueError("Baseline must be a JSON object.")

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


def collect_current_values(location):
    """Read one registry location without modifying it."""
    if location not in REGISTRY_LOCATIONS:
        raise ValueError(f"Unknown registry location: {location}")

    root_key, sub_key = REGISTRY_LOCATIONS[location]
    values = {}

    try:
        with winreg.OpenKey(
            root_key, sub_key, 0, winreg.KEY_READ
        ) as key:
            index = 0

            while True:
                try:
                    name, data, value_type = winreg.EnumValue(
                        key, index
                    )
                except OSError as error:
                    # ERROR_NO_MORE_ITEMS means enumeration is complete.
                    if getattr(error, "winerror", None) == 259:
                        break
                    raise

                values[name] = {
                    "data": data,
                    "type": value_type,
                }
                index += 1

    except OSError as error:
        raise RuntimeError(
            f"Could not read {location}: {error}"
        ) from error

    return values


def compare_location(location, old_values, current_values):
    """Compare entries and return changes with summary counts."""
    changes = []
    new_count = 0
    removed_count = 0
    modified_count = 0

    for name in sorted(current_values.keys() - old_values.keys()):
        entry = current_values[name]
        new_count += 1

        changes.append(
            f"NEW | {location} | {name} | "
            f"Data: {entry['data']!r} | "
            f"Type: {entry['type']}"
        )

    for name in sorted(old_values.keys() - current_values.keys()):
        entry = old_values[name]
        removed_count += 1

        changes.append(
            f"REMOVED | {location} | {name} | "
            f"Previous data: {entry['data']!r} | "
            f"Previous type: {entry['type']}"
        )

    for name in sorted(old_values.keys() & current_values.keys()):
        old_entry = old_values[name]
        new_entry = current_values[name]

        if old_entry != new_entry:
            modified_count += 1

            changes.append(
                f"MODIFIED | {location} | {name} | "
                f"Previous data: {old_entry['data']!r} | "
                f"Current data: {new_entry['data']!r} | "
                f"Previous type: {old_entry['type']} | "
                f"Current type: {new_entry['type']}"
            )

    return changes, new_count, removed_count, modified_count


def save_report(changes, new_count, removed_count, modified_count):
    """Append a timestamped report while preserving report history."""
    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)

    report_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with REPORT_FILE.open("a", encoding="utf-8") as file:
        file.write("\n\n" + "=" * 55 + "\n")
        file.write("WINDOWS REGISTRY CHANGE REPORT\n")
        file.write(f"Report generated at: {report_time}\n")
        file.write("=" * 55 + "\n\n")

        file.write("REGISTRY CHANGE SUMMARY\n")
        file.write("-----------------------\n")
        file.write(f"New entries: {new_count}\n")
        file.write(f"Removed entries: {removed_count}\n")
        file.write(f"Modified entries: {modified_count}\n\n")

        file.write("DETAILED CHANGES\n")
        file.write("----------------\n")

        if changes:
            for change in changes:
                file.write(change + "\n")
        else:
            file.write("No changes detected.\n")


def main():
    baseline = load_baseline()

    print("Windows Registry Change Detection")
    print("=" * 40)
    print("Registry access: READ ONLY")
    print(f"Baseline: {BASELINE_FILE}")
    print(f"Report: {REPORT_FILE}")
    print("Saved baseline loaded successfully.")

    # Read every location before comparing or writing a report.
    current_by_location = {}

    for location in REGISTRY_LOCATIONS:
        print(f"\nChecking: {location}")

        current_by_location[location] = collect_current_values(location)

        print(
            "Current entries:",
            len(current_by_location[location]),
        )

    all_changes = []
    total_new = 0
    total_removed = 0
    total_modified = 0

    for location in REGISTRY_LOCATIONS:
        changes, new_count, removed_count, modified_count = (
            compare_location(
                location,
                baseline[location],
                current_by_location[location],
            )
        )

        all_changes.extend(changes)
        total_new += new_count
        total_removed += removed_count
        total_modified += modified_count

    # Report only after all registry reads and comparisons succeed.
    save_report(
        all_changes,
        total_new,
        total_removed,
        total_modified,
    )

    print("\nRegistry Change Summary")
    print("-----------------------")
    print("New entries:", total_new)
    print("Removed entries:", total_removed)
    print("Modified entries:", total_modified)

    if all_changes:
        print("\nDetected differences:")
        for change in all_changes:
            print(change)
    else:
        print("\nNo differences detected.")

    print(f"\nReport appended to {REPORT_FILE}")


if __name__ == "__main__":
    try:
        main()
    except (
        OSError,
        ValueError,
        KeyError,
        TypeError,
        RuntimeError,
    ) as error:
        print("\nThe comparison could not be completed.")
        print("Reason:", error)
        print("The saved baseline was not intentionally modified.")
