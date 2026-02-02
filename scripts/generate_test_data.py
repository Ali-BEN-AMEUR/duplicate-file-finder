#!/usr/bin/env python3
"""
Script to generate realistic test data for the Duplicate File Finder application.
Creates a directory structure with duplicate and unique files of various types.
"""

import os
import shutil
from pathlib import Path

def create_directory_structure(base_path):
    """Create the test directory structure."""
    directories = [
        'documents/reports',
        'documents/invoices',
        'documents/letters',
        'media/images',
        'media/videos',
        'media/audio',
        'code/project_a',
        'code/project_b',
        'code/project_c',
        'code/libraries',
        'archive/old_documents',
        'archive/old_media',
    ]

    for directory in directories:
        os.makedirs(os.path.join(base_path, directory), exist_ok=True)

def create_test_files(base_path):
    """Create test files with specific content."""

    files_to_create = [
        # documents/reports
        ('documents/reports/report_2024_Q1.pdf', b'PDF Report Q1 ' * 10000),        # Duplicate backup_report_2024_Q1.pdf
        ('documents/reports/report_2024_Q2.pdf', b'PDF Report Q2 ' * 13000),        # Unique file
        ('documents/reports/backup_report_2024_Q1.pdf', b'PDF Report Q1 ' * 10000), # Duplicate report_2024_Q1.pdf

        # documents/invoices
        ('documents/invoices/invoice_001.docx', b'DOCX Invoice 001 ' * 1500),   # Duplicate invoice_002.docx
        ('documents/invoices/invoice_002.docx', b'DOCX Invoice 001 ' * 1500),   # Duplicate invoice_001.docx
        ('documents/invoices/template.docx', b'DOCX Template ' * 1200),         # Unique file

        # documents/letters
        ('documents/letters/letter_to_client.txt', b'Dear Client,\nThis is a sample letter.' * 200),        # Duplicate letter_to_client_copy.txt
        ('documents/letters/letter_to_client_copy.txt', b'Dear Client,\nThis is a sample letter.' * 200),   # Duplicate letter_to_client.txt

        # media/images
        ('media/images/photo_vacation.jpg', b'JPEG Photo Vacation ' * 100000),          # Duplicate photo_vacation_backup.jpg
        ('media/images/photo_vacation_backup.jpg', b'JPEG Photo Vacation ' * 100000),   # Duplicate photo_vacation.jpg
        ('media/images/photo_family.png', b'PNG Photo Family ' * 150000),               # Unique file
        ('media/images/screenshot.png', b'PNG Screenshot ' * 25000),                    # Unique file

        # media/videos
        ('media/videos/tutorial.mp4', b'MP4 Video Tutorial ' * 2500000),          # Duplicate tutorial_archive.mp4
        ('media/videos/tutorial_archive.mp4', b'MP4 Video Tutorial ' * 2500000),  # Duplicate tutorial.mp4

        # media/audio
        ('media/audio/song1.mp3', b'MP3 Audio Song1 ' * 320000),         # Duplicate song1_backup.mp3
        ('media/audio/song1_backup.mp3', b'MP3 Audio Song1 ' * 320000),  # Duplicate song1.mp3

        # code/project_a
        ('code/project_a/main.py', b'def main():\n    print("Hello World")\n' * 500),   # Duplicate code/project_b/main.py code/project_c/main.py
        ('code/project_a/utils.py', b'def helper():\n    return True\n' * 400),         # Unique file
        ('code/project_a/config.json', b'{"version": "1.0", "debug": true}' * 60),      # Duplicate code/project_b/config.json

        # code/project_b
        ('code/project_b/main.py', b'def main():\n    print("Hello World")\n' * 500),   # Duplicate code/project_a/main.py code/project_c/main.py
        ('code/project_b/utils.py', b'def helper():\n    return False\n' * 400),        # Unique file
        ('code/project_b/config.json', b'{"version": "1.0", "debug": true}' * 60),      # Duplicate code/project_a/config.json code/project_c/config.json

        # code/project_c
        ('code/project_c/main.py', b'def main():\n    print("Hello World")\n' * 500),   # Duplicate code/project_a/main.py code/project_b/main.py
        ('code/project_c/utils.py', b'def helper():\n    return None\n' * 400),        # Unique file
        ('code/project_c/config.json', b'{"version": "1.0", "debug": true}' * 60),      # Duplicate code/project_a/config.json code/project_b/config.json

        # code/libraries
        ('code/libraries/helper.py', b'class Helper:\n    pass\n' * 300),        # Unique file
        ('code/libraries/helper_v2.py', b'class HelperV2:\n    pass\n' * 350),   # Unique file

        # archive/old_documents
        ('archive/old_documents/report_2023.pdf', b'PDF Report 2023 ' * 11000),         # Duplicate report_2023_copy.pdf
        ('archive/old_documents/report_2023_copy.pdf', b'PDF Report 2023 ' * 11000),    # Duplicate report_2023.pdf

        # archive/old_media
        ('archive/old_media/old_photo.jpg', b'JPEG Old Photo ' * 75000),            # Duplicate old_photo_backup.jpg
        ('archive/old_media/old_photo_backup.jpg', b'JPEG Old Photo ' * 75000),     # Duplicate old_photo.jpg
    ]

    for relative_path, content in files_to_create:
        file_path = os.path.join(base_path, relative_path)
        with open(file_path, 'wb') as f:
            f.write(content)
        print(f"Created: {relative_path}")

def main():
    """Main function to generate test data."""
    base_path = Path(__file__).parent.parent / 'test_data'

    # Remove existing test_data if present
    if base_path.exists():
        print(f"Removing existing test_data directory: {base_path}")
        shutil.rmtree(base_path)

    print(f"\nCreating test data in: {base_path}")

    # Create directory structure
    create_directory_structure(base_path)
    print("✓ Directory structure created")

    # Create test files
    create_test_files(base_path)
    print("\n✓ Test files created successfully")

    print(f"\nTest data location: {base_path}")
    print("You can now run: python src/main.py test_data/")

if __name__ == '__main__':
    main()