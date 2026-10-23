
import json
import winreg
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
REFERENCE_FILE = BASE_DIR / "security_settings_reference_v2_corrected.json"

SETTINGS = {
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
        return {"status": "READ_ERROR", "message": str(error)}


def main():
    print("Create Corrected V2 Reference")
    print("=============================")
    print("Registry access: READ ONLY")

    # Never overwrite an existing reference.
    if REFERENCE_FILE.exists():
        print("\nSTOP: The corrected reference already exists.")
        print("No file was changed.")
        return

    snapshot = {}

    for name, (hive, key_path, value_name) in SETTINGS.items():
        result = read_setting(hive, key_path, value_name)
        snapshot[name] = result
        print(f"{name}: {result['status']}")

    # Do not save an incomplete snapshot.
    if any(item["status"] == "READ_ERROR" for item in snapshot.values()):
        print("\nERROR: At least one Registry value could not be read.")
        print("No reference was created.")
        return

    try:
        # Exclusive creation prevents overwriting an existing file.
        with REFERENCE_FILE.open("x", encoding="utf-8") as file:
            json.dump(snapshot, file, indent=4)

    except FileExistsError:
        print("\nSTOP: The reference appeared during creation.")
        print("No existing file was overwritten.")
        return

    print(f"\nNew reference created: {REFERENCE_FILE}")
    print("Your original reference and backup were not changed.")


if __name__ == "__main__":
    main()
