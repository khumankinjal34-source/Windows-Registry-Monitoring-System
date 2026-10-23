import hashlib
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

FILES_TO_HASH = [
    "baseline.json",
    "baseline_all_keys.json",
    "integrity_test_sample.txt",
]

hashes = {}

for filename in FILES_TO_HASH:
    file_path = BASE_DIR / filename
    if not file_path.is_file():
        raise FileNotFoundError(f"Required file not found: {filename}")

    digest = hashlib.sha256(file_path.read_bytes()).hexdigest()
    hashes[filename] = digest

output_file = BASE_DIR / "integrity_reference_hashes.json"
output_file.write_text(json.dumps(hashes, indent=4) + "\n", encoding="utf-8")

print("Integrity reference hashes generated successfully.")
for filename, digest in hashes.items():
    print(f"{filename}: {digest}")