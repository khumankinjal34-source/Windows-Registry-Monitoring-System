
import hashlib
import json
import tempfile
from pathlib import Path


def calculate_hash(file_path):
    sha256 = hashlib.sha256()

    with file_path.open("rb") as file:
        for chunk in iter(lambda: file.read(4096), b""):
            sha256.update(chunk)

    return sha256.hexdigest()


def main():
    print("Integrity Tamper Detection Test")
    print("===============================")

    # Create a separate temporary directory and test file.
    with tempfile.TemporaryDirectory() as temp_dir:
        test_file = Path(temp_dir) / "sample.txt"
        reference_file = Path(temp_dir) / "reference.json"

        # Save the original sample content.
        test_file.write_text(
            "Original test content",
            encoding="utf-8",
        )

        original_hash = calculate_hash(test_file)

        # Save its reference hash in the temporary directory.
        reference_file.write_text(
            json.dumps({"sample.txt": original_hash}),
            encoding="utf-8",
        )

        saved_reference = json.loads(
            reference_file.read_text(encoding="utf-8")
        )

        # Confirm the original file matches.
        assert calculate_hash(test_file) == saved_reference["sample.txt"]
        print("PASS: Original file matches its reference.")

        # Change only the temporary test file.
        test_file.write_text(
            "Modified test content",
            encoding="utf-8",
        )

        changed_hash = calculate_hash(test_file)

        # Confirm the change is detected.
        assert changed_hash != saved_reference["sample.txt"]
        print("PASS: Modified file was detected.")

    print("PASS: Temporary test files cleaned up.")


if __name__ == "__main__":
    main()
