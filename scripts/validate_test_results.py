#!/usr/bin/env python3
"""
Script to validate the results of duplicate file finder against expected results.
"""

import json
import sys
from pathlib import Path

def load_expected_results():
    """Load expected results for test data."""
    return {
        'total_files': 31,
        'unique_files': 19,
        'duplicate_groups': 10,
        'duplicate_files': 12,
        'duplicates_by_hash': {
            'hash_q1_report': {
                'files': [
                    'documents/reports/report_2024_Q1.pdf',
                    'documents/reports/backup_report_2024_Q1.pdf'
                ],
                'count': 2
            },
            'hash_q2_report': {
                'files': ['documents/reports/report_2024_Q2.pdf'],
                'count': 1
            },
            'hash_invoice_001': {
                'files': [
                    'documents/invoices/invoice_001.docx',
                    'documents/invoices/invoice_002.docx'
                ],
                'count': 2
            },
            'hash_template': {
                'files': ['documents/invoices/template.docx'],
                'count': 1
            },
            'hash_letter': {
                'files': [
                    'documents/letters/letter_to_client.txt',
                    'documents/letters/letter_to_client_copy.txt'
                ],
                'count': 2
            },
            'hash_vacation_photo': {
                'files': [
                    'media/images/photo_vacation.jpg',
                    'media/images/photo_vacation_backup.jpg'
                ],
                'count': 2
            },
            'hash_family_photo': {
                'files': ['media/images/photo_family.png'],
                'count': 1
            },
            'hash_screenshot': {
                'files': ['media/images/screenshot.png'],
                'count': 1
            },
            'hash_tutorial': {
                'files': [
                    'media/videos/tutorial.mp4',
                    'media/videos/tutorial_archive.mp4'
                ],
                'count': 2
            },
            'hash_song1': {
                'files': [
                    'media/audio/song1.mp3',
                    'media/audio/song1_backup.mp3'
                ],
                'count': 2
            },
            'hash_main_py': {
                'files': [
                    'code/project_a/main.py',
                    'code/project_b/main.py'
                ],
                'count': 2
            },
            'hash_utils_a': {
                'files': ['code/project_a/utils.py'],
                'count': 1
            },
            'hash_utils_b': {
                'files': ['code/project_b/utils.py'],
                'count': 1
            },
            'hash_config': {
                'files': [
                    'code/project_a/config.json',
                    'code/project_b/config.json'
                ],
                'count': 2
            },
            'hash_helper': {
                'files': ['code/libraries/helper.py'],
                'count': 1
            },
            'hash_helper_v2': {
                'files': ['code/libraries/helper_v2.py'],
                'count': 1
            },
            'hash_2023_report': {
                'files': [
                    'archive/old_documents/report_2023.pdf',
                    'archive/old_documents/report_2023_copy.pdf'
                ],
                'count': 2
            },
            'hash_old_photo': {
                'files': [
                    'archive/old_media/old_photo.jpg',
                    'archive/old_media/old_photo_backup.jpg'
                ],
                'count': 2
            }
        }
    }

def validate_results(output_text):
    """Validate the output against expected results."""
    expected = load_expected_results()

    print("=" * 70)
    print("VALIDATION RESULTS")
    print("=" * 70)

    checks = []

    # Check for found files count
    if f"{expected['total_files']} files total" in output_text:
        checks.append(("✓ Total files count", True))
    else:
        checks.append(("✗ Total files count", False))

    # Check for duplicate groups
    if f"Found {expected['duplicate_groups']} duplicate group(s)" in output_text:
        checks.append(("✓ Duplicate groups count", True))
    else:
        checks.append(("✗ Duplicate groups count", False))

    # Check for duplicate files count
    if f"{expected['duplicate_files']} duplicate file(s)" in output_text:
        checks.append(("✓ Duplicate files count", True))
    else:
        checks.append(("✗ Duplicate files count", False))

    # Check for duplicate files count
    if f"{expected['unique_files']} unique file(s)" in output_text:
        checks.append(("✓ Unique files count", True))
    else:
        checks.append(("✗ Unique files count", False))

    # Print validation results
    for check_name, result in checks:
        status = "PASS" if result else "FAIL"
        print(f"{check_name}: {status}")

    print("=" * 70)

    passed = sum(1 for _, result in checks if result)
    total = len(checks)

    print(f"\nValidation Summary: {passed}/{total} checks passed")

    return passed == total

def main():
    """Main validation function."""
    if len(sys.argv) < 2:
        print("Usage: python validate_test_results.py <output_file_or_text>")
        print("\nThis script validates the output of the duplicate file finder.")
        print("Example: python src/main.py test_data/ | python scripts/validate_test_results.py")
        sys.exit(1)

    output_text = sys.argv[1]

    if Path(output_text).is_file():
        with open(output_text, 'r') as f:
            output_text = f.read()

    success = validate_results(output_text)
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()