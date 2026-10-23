
"""Test Registry comparison logic using sample data only.

This test does not access Windows Registry or modify project baselines.
"""


def compare_snapshots(baseline, current):
    """Return new, removed, and modified entries."""
    new_entries = []
    removed_entries = []
    modified_entries = []

    for name in current:
        if name not in baseline:
            new_entries.append(name)
        elif current[name] != baseline[name]:
            modified_entries.append(name)

    for name in baseline:
        if name not in current:
            removed_entries.append(name)

    return new_entries, removed_entries, modified_entries


def main():
    # Sample saved snapshot
    baseline = {
        "OneDrive": "OneDrive_old.exe",
        "MicrosoftLists": "Lists.exe",
        "OldProgram": "OldProgram.exe",
    }

    # Sample current snapshot
    current = {
        "OneDrive": "OneDrive_old.exe",
        "MicrosoftLists": "Lists_new.exe",
        "NewProgram": "NewProgram.exe",
    }

    print("Testing Registry comparison with sample data only.")

    new_entries, removed_entries, modified_entries = (
        compare_snapshots(baseline, current)
    )

    print("\nChecking for new entries...")
    for name in new_entries:
        print("New entry detected:", name)

    print("\nChecking for removed entries...")
    for name in removed_entries:
        print("Removed entry detected:", name)

    print("\nChecking for modified entries...")
    for name in modified_entries:
        print("Modified entry detected:", name)
        print("Old data:", baseline[name])
        print("New data:", current[name])

    print("\nChange Summary")
    print("--------------")
    print("New entries:", len(new_entries))
    print("Removed entries:", len(removed_entries))
    print("Modified entries:", len(modified_entries))

    # Verify the expected results
    assert new_entries == ["NewProgram"]
    assert removed_entries == ["OldProgram"]
    assert modified_entries == ["MicrosoftLists"]

    print("\nPASS: All expected comparison results are correct.")


if __name__ == "__main__":
    main()
