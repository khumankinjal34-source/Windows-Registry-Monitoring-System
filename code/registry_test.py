
import json
import winreg
from pathlib import Path

# Read-only prototype for the current user's startup Registry key.
BASE_DIR = Path(__file__).resolve().parent
BASELINE_FILE = BASE_DIR / "baseline.json"

REGISTRY_PATH = r"Software\Microsoft\Windows\CurrentVersion\Run"


def read_startup_values():
    programs = {}

    with winreg.OpenKey(
        winreg.HKEY_CURRENT_USER,
        REGISTRY_PATH,
        0,
        winreg.KEY_READ,
    ) as key:
        index = 0

        while True:
            try:
                name, value, value_type = winreg.EnumValue(key, index)
            except OSError as error:
                if getattr(error, "winerror", None) == 259:
                    break
                raise

            programs[name] = value
            index += 1

    return programs


if __name__ == "__main__":
    # Never overwrite the existing baseline.
    if BASELINE_FILE.exists():
        print("STOP: baseline.json already exists.")
        print("No Registry values were read and no file was changed.")
    else:
        try:
            programs = read_startup_values()

            # Exclusive creation prevents accidental overwriting.
            with BASELINE_FILE.open("x", encoding="utf-8") as file:
                json.dump(programs, file, indent=4)

            print("Baseline created successfully.")
            print("Number of Registry values stored:", len(programs))

        except OSError as error:
            print("ERROR: Could not safely create the baseline.")
            print("Details:", error)
