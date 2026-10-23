
import hashlib
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

FILES_TO_CHECK = [
    BASE_DIR / "baseline.json",
    BASE_DIR / "baseline_all_keys.json",
    BASE_DIR / "integrity_test_sample.txt",
]

HASH_FILE = BASE_DIR / "integrity_reference_hashes.json"


def calculate_hash(file_path):
    """Calculate the SHA-256 hash of a file."""
    sha256 = hashlib.sha256()

    with file_path.open("rb") as file:
        for chunk in iter(lambda: file.read(4096), b""):
            sha256.update(chunk)

    return sha256.hexdigest()


def load_hashes():
    """Load and validate saved reference hashes."""
    # utf-8-sig supports JSON files with or without a UTF-8 BOM.
    with HASH_FILE.open("r", encoding="utf-8-sig") as file:
        saved_hashes = json.load(file)

    if not isinstance(saved_hashes, dict):
        raise ValueError("Hash reference must be a JSON object.")

    for name, digest in saved_hashes.items():
        if not isinstance(name, str) or not isinstance(digest, str):
            raise ValueError("Hash reference contains an invalid entry.")

        if len(digest) != 64 or any(
            character not in "0123456789abcdef"
            for character in digest.lower()
        ):
            raise ValueError(f"Invalid SHA-256 hash for: {name}")

    return saved_hashes


def main():
    print("Project Baseline Integrity Checker")
    print("==================================")
    print("Mode: Read-only verification")

    if not HASH_FILE.is_file():
        print("\nERROR: Hash reference file was not found.")
        print("No files were changed.")
        return

    try:
        saved_hashes = load_hashes()
    except (OSError, json.JSONDecodeError, ValueError) as error:
        print("\nERROR: Could not use the hash reference:", error)
        print("No files were changed.")
        return

    print("\nVerification results:")

    for file_path in FILES_TO_CHECK:
        if not file_path.is_file():
            print(f"UNVERIFIED: {file_path.name} was not found.")
            continue

        try:
            current_hash = calculate_hash(file_path)
        except OSError as error:
            print(f"ERROR: Could not read {file_path.name}: {error}")
            continue

        saved_hash = saved_hashes.get(file_path.name)

        if saved_hash is None:
            print(f"UNVERIFIED: No saved hash for {file_path.name}.")
        elif current_hash == saved_hash.lower():
            print(f"PASS: {file_path.name} matches its saved hash.")
        else:
            print(f"WARNING: {file_path.name} differs from its saved hash.")

    print("\nVerification finished.")


if __name__ == "__main__":
    main()
