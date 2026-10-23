
import json
import winreg
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent
REFERENCE_FILE = BASE_DIR / "security_settings_reference_v2_corrected.json"
REPORT_FILE = (
    BASE_DIR.parent / "reports" / "security_settings_report_v2.txt"
)

# Read-only checks. Missing policy values are reported as NOT_FOUND,
# not automatically treated as evidence of a security problem.
SECURITY_SETTINGS = {
    "Defender_DisableAntiSpyware": (
        winreg.HKEY_LOCAL_MACHINE,
        r"SOFTWARE\Policies\Microsoft\Windows Defender",
        "DisableAntiSpyware",
    ),
    "Defender_DisableRealtimeMonitoring": (
        winreg.HKEY_LOCAL_MACHINE,
        r"SOFTWARE\Policies\Microsoft\Windows Defender\Real-Time Protection",
        "DisableRealtimeMonitoring",
    ),
    "Defender_DisableBehaviorMonitoring": (
        winreg.HKEY_LOCAL_MACHINE,
        r"SOFTWARE\Policies\Microsoft\Windows Defender\Real-Time Protection",
        "DisableBehaviorMonitoring",
    ),
    "Firewall_DomainProfile_EnableFirewall": (
        winreg.HKEY_LOCAL_MACHINE,
        r"SYSTEM\CurrentControlSet\Services\SharedAccess\Parameters\FirewallPolicy\DomainProfile",
        "EnableFirewall",
    ),
    "Firewall_PrivateProfile_EnableFirewall": (
        winreg.HKEY_LOCAL_MACHINE,
        r"SYSTEM\CurrentControlSet\Services\SharedAccess\Parameters\FirewallPolicy\StandardProfile",
        "EnableFirewall",
    ),
    "Firewall_PublicProfile_EnableFirewall": (
        winreg.HKEY_LOCAL_MACHINE,
        r"SYSTEM\CurrentControlSet\Services\SharedAccess\Parameters\FirewallPolicy\PublicProfile",
        "EnableFirewall",
    ),
    "UAC_EnableLUA": (
        winreg.HKEY_LOCAL_MACHINE,
        r"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System",
        "EnableLUA",
    ),
    "UAC_ConsentPromptBehaviorAdmin": (
        winreg.HKEY_LOCAL_MACHINE,
        r"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System",
        "ConsentPromptBehaviorAdmin",
    ),
    "Shell_Userinit": (
        winreg.HKEY_LOCAL_MACHINE,
        r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon",
        "Userinit",
    ),
    "Shell_Shell": (
        winreg.HKEY_LOCAL_MACHINE,
        r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon",
        "Shell",
    ),
}


def read_setting(hive, key_path, value_name):
    """Read one Registry value without changing it."""
    try:
        with winreg.OpenKey(
            hive, key_path, 0, winreg.KEY_READ
        ) as key:
            value, value_type = winreg.QueryValueEx(key, value_name)

        return {
            "status": "FOUND",
            "value": value,
            "type": value_type,
        }

    except FileNotFoundError:
        return {"status": "NOT_FOUND"}

    except OSError as error:
        return {
            "status": "READ_ERROR",
            "message": str(error),
        }


def collect_settings():
    """Collect the selected settings."""
    snapshot = {}

    for name, (hive, key_path, value_name) in SECURITY_SETTINGS.items():
        snapshot[name] = read_setting(hive, key_path, value_name)

    return snapshot


def load_reference():
    """Load and validate the separate V2 reference."""
    with REFERENCE_FILE.open("r", encoding="utf-8-sig") as file:
        reference = json.load(file)

    if not isinstance(reference, dict):
        raise ValueError("Reference must be a JSON object.")

    if set(reference) != set(SECURITY_SETTINGS):
        raise ValueError("Reference has missing or unexpected settings.")

    for name, result in reference.items():
        if not isinstance(result, dict):
            raise ValueError(f"Invalid reference entry: {name}")

        status = result.get("status")

        if status == "FOUND":
            if "value" not in result or "type" not in result:
                raise ValueError(f"Incomplete reference entry: {name}")
        elif status != "NOT_FOUND":
            raise ValueError(f"Unusable reference status for {name}: {status}")

    return reference


def save_reference(snapshot):
    """Create a new reference without overwriting an existing one."""
    with REFERENCE_FILE.open("x", encoding="utf-8") as file:
        json.dump(snapshot, file, indent=4)


def compare_settings(reference, current):
    """Identify changes and readings that could not be verified."""
    changes = []

    for name in SECURITY_SETTINGS:
        old = reference[name]
        new = current[name]

        if old.get("status") == "READ_ERROR" or new.get("status") == "READ_ERROR":
            changes.append(
                f"UNVERIFIED | {name} | A Registry read failed; "
                "change status cannot be confirmed."
            )
        elif old != new:
            changes.append(
                f"CHANGED | {name} | Previous: {old} | Current: {new}"
            )

    return changes


def save_report(changes):
    """Append findings to a separate report file."""
    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with REPORT_FILE.open("a", encoding="utf-8") as file:
        file.write(f"\n\nSecurity settings check: {timestamp}\n")
        for change in changes:
            file.write(change + "\n")


def main():
    print("Windows Security Settings Monitor V2")
    print("=====================================")
    print("Registry access: READ ONLY")
    print("Existing V1 reference will not be changed.")

    current = collect_settings()

    for name, result in current.items():
        print(f"{name}: {result['status']}")

    # Do not establish a reference from incomplete readings.
    if any(
        result["status"] == "READ_ERROR"
        for result in current.values()
    ):
        print("\nERROR: At least one setting could not be read.")
        print("Reference creation/comparison is stopped.")
        return

    if not REFERENCE_FILE.exists():
        try:
            save_reference(current)
        except FileExistsError:
            print("Reference appeared during creation; stopping safely.")
            return

        print(f"\nNew V2 reference created: {REFERENCE_FILE}")
        print("Run again to compare against this reference.")
        return

    try:
        reference = load_reference()
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"\nERROR: Reference could not be used: {error}")
        print("The existing reference was not changed.")
        return

    changes = compare_settings(reference, current)

    if changes:
        print("\nChanges detected or readings unverified:")
        for change in changes:
            print("-", change)

        try:
            save_report(changes)
            print(f"\nReport appended: {REPORT_FILE}")
        except OSError as error:
            print(f"\nERROR: Could not save the report: {error}")
    else:
        print("\nPASS: No differences from the V2 reference.")


if __name__ == "__main__":
    main()




    