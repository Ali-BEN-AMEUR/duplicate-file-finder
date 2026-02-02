import argparse
import time
import sys
from file_scanner import FileScanner
from hash_calculator import HashCalculator
from duplicate_detector import DuplicateDetector
from report_generator import ReportGenerator
from file_manager import FileManager

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        prog='duplicate-file-finder',
        description='Locate duplicate files across directories',
        epilog='Example: python main.py --html report.html --no-sort --auto-clean /path/to/dir1 /path/to/dir2'
    )
    parser.add_argument(
        '--html',
        metavar='FILE',
        help='Generate HTML report and save to specified file'
    )
    parser.add_argument(
        '--no-sort',
        action='store_true',
        help='Sort duplicate groups by file size in descending order (largest first)'
    )
    parser.add_argument(
        '--auto-clean',
        action='store_true',
        help='Automatically delete duplicate files, keeping only the first one found'
    )
    parser.add_argument(
        'directories',
        nargs='+',
        help='Directories to scan for duplicate files'
    )
    return parser.parse_args()

def format_duration(seconds):
    """Format duration in HH:MM:SS.mmm format."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = seconds % 60
    milliseconds = int((secs % 1) * 1000)
    secs = int(secs)

    return f"{hours:02d}:{minutes:02d}:{secs:02d}.{milliseconds:03d}"

def format_decimal_duration(seconds):
    """Format duration in human-readable format."""
    if seconds < 60:
        return f"{seconds:.2f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.2f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.2f}h"

def get_user_input(prompt, valid_responses=None):
    """
    Get user input from the terminal, even if stdout is redirected.
    
    Args:
        prompt: The prompt to display
        valid_responses: List of valid responses (case-insensitive)
        
    Returns:
        str: The user's response in lowercase
    """
    # Determine the terminal device based on platform
    if sys.platform == 'win32':
        terminal_device = 'CON:'
    else:
        terminal_device = '/dev/tty'
    
    try:
        # Try to open the terminal device for interactive input
        with open(terminal_device, 'r') as tty:
            # Print the prompt to stderr (visible even if stdout is redirected)
            sys.stderr.write(prompt)
            sys.stderr.flush()
            
            # Read from terminal
            user_response = tty.readline().strip().lower()
            
            # Validate response if valid_responses is provided
            if valid_responses:
                while user_response not in valid_responses:
                    sys.stderr.write(f"Invalid response. Please enter one of: {', '.join(valid_responses)}: ")
                    sys.stderr.flush()
                    user_response = tty.readline().strip().lower()
            
            return user_response
    
    except (FileNotFoundError, IOError, OSError):
        # Terminal device not available (e.g., in non-interactive environment)
        sys.stderr.write(f"⚠️  WARNING: Interactive terminal not available\n")
        sys.stderr.write(f"Cannot confirm auto-clean operation.\n")
        sys.stderr.write(f"Please run the command interactively or use a shell script.\n")
        return None

def confirm_auto_clean(duplicate_groups, file_data):
    """
    Ask user to confirm auto-clean operation.
    Works even when stdout is redirected to a file.
    
    Args:
        duplicate_groups: {hash: [file_paths]}
        file_data: {file_path: {'hash': hash, 'size': size, 'deleted': bool}}
    
    Returns:
        bool: True if user confirms, False otherwise
    """
    # Calculate statistics
    total_files_to_delete = 0
    total_size_to_delete = 0
    
    for file_hash, paths in duplicate_groups.items():
        # All files except the first one will be deleted
        for file_path in paths[1:]:
            total_files_to_delete += 1
            if file_path in file_data:
                total_size_to_delete += file_data[file_path]['size']
    if total_files_to_delete == 0:
        sys.stderr.write("No duplicate files to delete.\n")
        return False

    # Format size for display
    report_gen = ReportGenerator()
    size_str = report_gen._format_size(total_size_to_delete)
    
    # Display confirmation dialog on stderr (visible even if stdout is redirected)
    sys.stderr.write("\n" + "=" * 60 + "\n")
    sys.stderr.write("AUTO-CLEAN CONFIRMATION\n")
    sys.stderr.write("=" * 60 + "\n")
    sys.stderr.write(f"\n⚠️  WARNING: This operation will permanently delete files!\n")
    sys.stderr.write(f"\nStatistics:\n")
    sys.stderr.write(f"  Files to delete: {total_files_to_delete}\n")
    sys.stderr.write(f"  Space to free:   {size_str}\n")
    sys.stderr.write(f"\nAction: Keeping the first file in each duplicate group\n")
    sys.stderr.write(f"        and deleting all copies\n")
    sys.stderr.write("\n" + "-" * 60 + "\n")
    sys.stderr.flush()
    
    # Get user confirmation
    response = get_user_input("\nAre you sure you want to proceed? (yes/no): ", ['yes', 'y', 'no', 'n'])
    
    if response is None:
        # Terminal not available
        return False
    
    if response in ['yes', 'y']:
        sys.stderr.write("\n✓ Confirmed. Starting auto-clean...\n")
        sys.stderr.write("=" * 60 + "\n\n")
        sys.stderr.flush()
        return True
    else:
        sys.stderr.write("\n✗ Cancelled. Auto-clean aborted.\n")
        sys.stderr.write("=" * 60 + "\n\n")
        sys.stderr.flush()
        return False

def main():
    # Start timing
    start_time = time.time()

    args = parse_arguments()
    directories = args.directories

    # Step 1: Scan all directories for files
    print("Step 1: Scanning directories...")
    step1_start = time.time()

    file_scanner = FileScanner(directories)
    file_scanner.scan()
    file_paths = file_scanner.get_file_paths()
    directory_summary = file_scanner.get_summary()

    step1_duration = time.time() - step1_start

    if not file_paths:
        print("No files found in specified directories.")
        return

    print(f"  Found {len(file_paths)} files total")
    print(f"  Time: {format_duration(step1_duration)}")

    # Step 2: Calculate hash for each file
    print("\nStep 2: Calculating file hashes...")
    step2_start = time.time()

    hash_calculator = HashCalculator()
    file_data = {}

    for file_path, file_size in file_paths.items():
        file_hash = hash_calculator.calculate_hash(file_path)
        if file_hash is not None:
            file_data[file_path] = {
                'hash': file_hash,
                'size': file_size,
                'deleted': False
            }

    step2_duration = time.time() - step2_start

    print(f"  Hashes calculated for {len(file_data)} files")
    print(f"  Time: {format_duration(step2_duration)}")

    # Step 3: Detect duplicates
    print("\nStep 3: Detecting duplicates...")
    step3_start = time.time()

    duplicate_detector = DuplicateDetector(file_data)
    duplicate_groups = duplicate_detector.get_duplicate_groups()
    unique_files = duplicate_detector.get_unique_files()

    step3_duration = time.time() - step3_start

    duplicate_count = sum(len(paths) - 1 for paths in duplicate_groups.values())
    print(f"  Found {len(duplicate_groups)} duplicate group(s) totalling {duplicate_count} duplicate file(s) and {len(unique_files)+len(duplicate_groups)} unique file(s)")
    print(f"  Time: {format_duration(step3_duration)}")

    # Step 4: Apply sorting once (if requested)
    print("\nStep 4: Processing duplicate groups...")
    step4_start = time.time()

    report_generator = ReportGenerator()

    # Sort once at the beginning if requested
    if not args.no_sort:
        duplicate_groups = report_generator.sort_duplicates_by_size(duplicate_groups, file_data)

    step4_duration = time.time() - step4_start
    print(f"  Time: {format_duration(step4_duration)}")

    # Step 5: Auto-clean if requested
    deleted_files = []
    if args.auto_clean:
        # Ask for confirmation before proceeding
        if not confirm_auto_clean(duplicate_groups, file_data):
            print("Skipping auto-clean and proceeding to report generation...")
            args.auto_clean = False  # Don't mark as auto_clean in reports
            current_step = 5
        else:
            print("Step 5: Auto-cleaning duplicates...")
            print(f"  Using deletion method: {FileManager.get_deletion_method()}")
            step5_start = time.time()

            deleted_count = 0
            deleted_size = 0

            for file_hash, paths in duplicate_groups.items():
                # Keep the first file, delete the rest
                for file_path in paths[1:]:
                    success, message = FileManager.move_to_trash(file_path)
                    
                    if success:
                        file_data[file_path]['deleted'] = True
                        deleted_files.append(file_path)
                        deleted_count += 1
                        deleted_size += file_data[file_path]['size']
                        print(f"  ✓ Deleted: {file_path}")
                    else:
                        print(f"  ✗ Error: {message} - {file_path}")

            step5_duration = time.time() - step5_start
            print(f"  Deleted {deleted_count} files ({report_generator._format_size(deleted_size)})")
            print(f"  Time: {format_duration(step5_duration)}")
            current_step = 6
    else:
        step5_duration = 0
        current_step = 5

    # Step 6/7: Generate text report
    print(f"\nStep {current_step}: Generating text report...")
    step_text_start = time.time()

    report = report_generator.generate_report(
        directory_summary,
        duplicate_groups,
        file_data,
        deleted_files if args.auto_clean else None
    )
    print("\n" + report)

    step_text_duration = time.time() - step_text_start
    print(f"Time: {format_duration(step_text_duration)}")

    # Step 7/8: Generate HTML report if requested
    step_html_duration = 0
    if args.html:
        print(f"\nStep {current_step + 1}: Generating HTML report...")
        step_html_start = time.time()

        html_report = report_generator.generate_html_report(
            directory_summary,
            duplicate_groups,
            file_data,
            args.auto_clean
        )
        with open(args.html, 'w', encoding='utf-8') as f:
            f.write(html_report)

        step_html_duration = time.time() - step_html_start
        print(f"  HTML report saved to: {args.html}")
        print(f"  Time: {format_duration(step_html_duration)}")

    # Total duration
    total_duration = time.time() - start_time

    print("\n" + "=" * 60)
    print("EXECUTION TIME SUMMARY")
    print("=" * 60)
    print(f"  Step 1 (Scanning):       {format_duration(step1_duration)}")
    print(f"  Step 2 (Hashing):        {format_duration(step2_duration)}")
    print(f"  Step 3 (Detection):      {format_duration(step3_duration)}")
    print(f"  Step 4 (Processing):     {format_duration(step4_duration)}")
    if args.auto_clean:
        print(f"  Step 5 (Auto-clean):     {format_duration(step5_duration)}")
        print(f"  Step 6 (Text Report):    {format_duration(step_text_duration)}")
        if args.html:
            print(f"  Step 7 (HTML Report):    {format_duration(step_html_duration)}")
    else:
        print(f"  Step 5 (Text Report):    {format_duration(step_text_duration)}")
        if args.html:
            print(f"  Step 6 (HTML Report):    {format_duration(step_html_duration)}")
    print("-" * 60)
    print(f"  TOTAL TIME:              {format_duration(total_duration)}")
    print("=" * 60)

if __name__ == "__main__":
    main()