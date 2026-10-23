# Windows Registry Change Monitoring System

## Project Overview

The Windows Registry Change Monitoring System is a Python-based defensive security project developed as part of the Unified Mentor internship.

It monitors selected Windows Registry locations, compares current values with saved baselines, and records detected changes to help identify potentially suspicious modifications.

## Objectives

- Monitor selected Windows startup Registry locations.
- Detect new, removed, or modified Registry entries.
- Check selected Windows security settings, including Firewall and User Account Control (UAC).
- Verify the integrity of selected baseline files using reference hashes.
- Generate reports to support security analysis and testing.

## Key Components

- **Registry Monitoring:** Checks configured startup Registry locations.
- **Change Detection:** Compares current Registry values with saved baselines.
- **Security Settings Monitoring:** Checks selected Defender, Firewall, UAC, and Windows logon settings.
- **Baseline Integrity Checking:** Checks whether selected files have changed relative to saved reference hashes.
- **Automated Reporting:** Records monitoring results in report files.
- **Testing:** Includes comparison, error-handling, and security-monitoring tests.

## Technologies Used

- Python
- Windows Registry (`winreg`)
- JSON
- SHA-256 file hashing
- Windows operating system

## Project Structure

- `code/` — Main Python scripts and configuration files.
- `tests/` — Test scripts for checking project components.
- `report/` — Project documentation in Word/PDF format.
- `reports/` — Location for generated monitoring reports.
- `screenshots/` — Project screenshots reviewed for privacy before publication.

## Testing Results

The following test scripts were executed, and all four passed:

- `test_comparison.py`
- `test_integrity_detection.py`
- `test_monitor_errors.py`
- `test_security_comparison.py`

These tests cover sample change detection, baseline integrity checking, error handling, and security-setting comparison.

## Platform and Usage

This project is designed for Windows and uses Python's Windows Registry interface. Registry access and the availability of certain security settings may vary depending on the Windows configuration and permissions.

Run scripts only in an authorized test environment. Review each script and its required input files before execution. Some scripts read local Registry values or create and update files.

## Safety and Limitations

- The project is intended for defensive monitoring and educational use.
- It focuses only on the Registry locations and security settings configured in the code.
- A detected change is not, by itself, proof of malware or malicious activity.
- Results depend on the baseline, permissions, and Windows configuration.
- The project does not replace a full endpoint detection or antivirus solution.

## Project Documentation

Refer to the project report included in the `report/` folder for the design, implementation, testing approach, results, and limitations.

## Author

Developed as part of the Unified Mentor internship.