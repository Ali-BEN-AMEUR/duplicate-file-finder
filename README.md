# Duplicate File Finder

## Overview
The Duplicate File Finder is a Python application designed to locate duplicate files across one or more storage systems. It scans specified directories, computes unique file signatures, and groups duplicate files for easy identification.

## Features
- Scans multiple directories for files across macOS, Windows, and Linux.
- Automatically excludes system files (`.DS_Store`, `Thumbs.db`, cache files, etc.).
- Computes SHA-256 file hashes to identify duplicates.
- Groups and reports duplicate files with detailed statistics.
- Generates both text and HTML reports.
- Groups of duplicate files are sorted by file size in descending order (largest files first)
- **Interactive HTML reports** with clickable file links.
- **Delete functionality** - Remove duplicate files directly from the HTML report.
- **Built-in delete server** - Included Python server for handling file deletion.
- **Auto clean** deletes automatically duplicate files
- Provides a summary of the number of files processed in each directory.

## Installation
The application uses platform-independent file operations and automatically handles path separators across operating systems.
To install the required dependencies, run the following command:

```bash
pip install -r requirements.txt
```

## Quick Start

### 1. Generate Test Data
```bash
python scripts/generate_test_data.py
```

### 2. Start the unified Server (in a separate terminal)
```bash
python scripts/server.py
```

### 3. Run the Application with HTML Report
```bash
python src/main.py --html report.html test_data/
```

### 4. Open the Report
Open `report.html` in your web browser and click delete buttons to remove files.

## Usage

### Basic Usage
To run the application and scan directories:

```bash
python src/main.py /path/to/directory1 /path/to/directory2
```

### Generate HTML Report
To create an HTML report with clickable links to duplicate files:

```bash
python src/main.py --html report.html /path/to/directory1 /path/to/directory2
```

The HTML report includes:
- Summary table of scanned directories
- Grouped duplicate files organized by hash
- Clickable file links that open in your system's default application
- **Delete buttons** (🗑️) to remove files directly from the report
- File size information and duplicate file counts
- Responsive, modern design

## HTML Report Features

### File Links
- Click on any filename to open the file with your system's default application
- Absolute file paths are automatically handled for cross-platform compatibility

## Auto-Clean Feature

When using the `--auto-clean` option:
- ✓ The first file in each duplicate group is **KEPT**
- ✓ All subsequent duplicates are automatically **DELETED** (moved to trash)
- ✓ Space freed is reported in the summary
- ✓ Deleted files are marked as `[DELETED]` in the text report
- ✓ HTML report shows deleted files with strikethrough and no delete buttons
- ✓ The report displays how much space was freed

### Warning
Use `--auto-clean` with caution! The deletion happens automatically without confirmation. Always verify your data before using this option.

## Running the Application

### Step 1: Start the Unified Server

Open a terminal and run:

```bash
python scripts/server.py
```

The server will listen on `http://localhost:1080` and provide:
- **Media serving** - Images, videos, and audio preview
- **File deletion** - Interactive file removal functionality

**Supported media formats:**
- **Images:** JPG, PNG, GIF, WebP, SVG, BMP, TIFF
- **Videos:** MP4, WebM, MOV, AVI, MKV, FLV, WMV, M4V
- **Audio:** MP3, WAV, FLAC, AAC, OGG, M4A, WMA, OPUS

### Step 2: Run the Duplicate Finder

Open another terminal and run:

```bash
python src/main.py [options] [directories...]
```

## Examples

### Scan and generate HTML report with media preview
```bash
python src/main.py --html duplicates.html ~/Documents ~/Downloads
```

### Scan with sorting by file size
```bash
python src/main.py --sort-by-size --html duplicates.html ~/Documents
```

### Scan test data with both options
```bash
python src/main.py --html test_report.html --sort-by-size test_data/
```

## Access the HTML Report

1. Make sure the unified server is running (`python scripts/server.py`)
2. Open the generated HTML file in your browser
3. Click on media files to preview them directly in the browser
4. If `--auto-clean` was NOT used, use the 🗑️ button to delete files manually
5. If `--auto-clean` was used, the report shows which files were deleted

## Server API Endpoints

### Media Serving
```
GET http://localhost:1080/?file_path=/path/to/image.jpg
```
Serves media files with appropriate MIME types and caching headers.

### File Deletion
```
DELETE http://localhost:1080/?file_path=/path/to/file.txt
```
Moves files to trash/recycle bin or deletes them if necessary.

### Delete Functionality
- Each file has a delete button (🗑️) next to it
- Click the delete button to remove a file
- A confirmation dialog will appear before deletion
- The deletion request is sent to: `http://localhost:1080/?file_path=<file_path>`
- **Note**: The included delete server must be running to handle deletion requests

### Unified Server Implementation
To enable file deletion, you need to run the provided http server on port 1080:

```bash
python scripts/server.py
```

The server output will show:
```
============================================================
Unified Server for Duplicate File Finder
============================================================
Server listening on http://localhost:1080

✓ Available endpoints:
  Media serving: GET http://localhost:1080/?file_path=/path/to/file
  File deletion: DELETE http://localhost:1080/?file_path=/path/to/file

⚠ send2trash library NOT found
  Run: pip install send2trash
  Fallback to platform-specific methods

Supported media formats:
  Images: JPG, PNG, GIF, WebP, SVG, BMP, TIFF
  Videos: MP4, WebM, MOV, AVI, MKV, FLV, WMV, M4V
  Audio:  MP3, WAV, FLAC, AAC, OGG, M4A, WMA, OPUS

Press Ctrl+C to stop the server
============================================================
```

## Built-in Server (Recommended)
The project includes a custom Python delete server at `scripts/server.py`:

Start it with:
```bash
python scripts/server.py
```

The server will:
- Listen on `localhost:1080`
- Handle DELETE requests with `file_path` parameter
- Return JSON responses with status information
- Display deletion activity in the terminal
- Require confirmation before deletion (via HTML UI)
- Handle GET requests with `file_path` parameter
- Returns the file content with the appropriate mime type

#### Features
- ✅ Cross-platform compatibility (macOS, Windows, Linux)
- ✅ Permission checking before deletion (via HTML UI)
- ✅ Error handling with informative messages
- ✅ JSON response format
- ✅ Uploading files
- ✅ Activity logging to console

#### Example Requests
```bash
# Delete a file using curl
curl -X DELETE "http://localhost:1080/?file_path=/Users/user/Documents/duplicate.txt"

# Using Python requests library
python -c "
import requests
response = requests.delete('http://localhost:1080/?file_path=/path/to/file')
print(response.json())
"
```

## Testing

### Generate Test Data
To create realistic test data for validation:

```bash
python scripts/generate_test_data.py
```

This creates a `test_data/` directory with 31 files including:
- 10 duplicate groups
- 12 duplicate files
- 19 unique files
- Multiple file types (PDF, DOCX, images, videos, audio, code)

### Run Application on Test Data

**Text Report:**
```bash
python src/main.py test_data/
```

**HTML Report:**
```bash
python src/main.py --html report.html test_data/
```

Then open `report.html` in your web browser.

### Complete Test Workflow
```bash
# Terminal 1: Start the delete server
python scripts/server.py

# Terminal 2: Generate test data and run the application
python scripts/generate_test_data.py
python src/main.py --html test_report.html test_data/

# Open test_report.html in your browser and test the delete buttons
```

### Validate Results
After running the application on test data, validate the results:

```bash
python src/main.py test_data/ > output.txt
python scripts/validate_test_results.py output.txt
```

Expected output:
```
======================================================================
VALIDATION RESULTS
======================================================================
✓ Total files count: PASS
✓ Duplicate groups count: PASS
✓ Duplicate files count: PASS
✓ Unique files count: PASS
======================================================================

Validation Summary: 4/4 checks passed
```

### Run Unit Tests
To run all unit tests:

```bash
python -m pytest tests/ -v
```

Or using unittest:
```bash
python -m unittest discover tests/
```

## Expected Test Results
When running on test data, the application should report:
- **Total files**: 31
- **Duplicate groups**: 10
- **Duplicate files**: 12
- **Unique files**: 19
- **Summary**: Files processed across test_data/ directory

## System File Exclusion

The application automatically excludes the following system and cache files across all platforms:

**macOS:**
- `.DS_Store`, `.AppleDouble`, `.LSOverride`, `.Spotlight-V100`, `.Trashes`

**Windows:**
- `Thumbs.db`, `desktop.ini`, `$RECYCLE.BIN`, `System Volume Information`, `ehthumbs.db`

**Development/Cache:**
- `__pycache__`, `.pytest_cache`, `.git`, `.vscode`, `.idea`
- `node_modules`, `.env`, `venv`, `build`, `dist`

**File Extensions:**
- `*.pyc`, `*.pyo`, `*.egg`, `*.swp`, `*~`

## Output Reports

### Text Report Format
- Standard output 
```
============================================================
DUPLICATE FILE FINDER REPORT
============================================================

SCAN SUMMARY:
------------------------------------------------------------
  Directory: test_data/
    Files processed: 31

Total files processed: 31

DUPLICATES FOUND:
------------------------------------------------------------
  Group 1 (Hash: 998f08b84dfd24e5...):
    - test_data/archive/old_media/old_photo_backup.jpg
    - test_data/archive/old_media/old_photo.jpg
  
  [... more groups ...]
```
- Output for --auto-clean option
```
============================================================
AUTO-CLEAN CONFIRMATION
============================================================

⚠️  WARNING: This operation will permanently delete files!

Statistics:
  Files to delete: 12
  Space to free:   4.29 MB

Action: Keeping the first file in each duplicate group
        and deleting all copies

------------------------------------------------------------

Are you sure you want to proceed? (yes/no): y

✓ Confirmed. Starting auto-clean...
============================================================
...
============================================================
DUPLICATE FILE FINDER REPORT
============================================================

SCAN SUMMARY:
------------------------------------------------------------
  Directory: test_data/
    Files processed: 31

Total files processed: 31

AUTO-CLEAN SUMMARY:
------------------------------------------------------------
  Files deleted: 5
  Space freed: 1.25 GB

DUPLICATES FOUND:
------------------------------------------------------------
  Group 1 (Hash: a1b2c3d4e5f6...):
    - /home/user/file1.mp4 [KEPT]
    - /home/user/Documents/file1_copy.mp4 [DELETED]
    - /home/user/backup/file1_backup.mp4 [DELETED]

```

### HTML Report Format
The HTML report provides a visual interface with:
- **Group headers** showing: `Group N • X files • Size`
- **Clickable file names** that open in new tab
- **Delete buttons** (🗑️) for removing files
- **Interactive hover effects** for better UX
- **Responsive design** that works on all screen sizes
- **Color-coded sections** for easy navigation

Example HTML structure:
```html
Group 1 • 2 files • 1.07 MB
  🗑️ old_photo_backup.jpg
  🗑️ old_photo.jpg
```

## Command Line Options

```bash
python src/main.py [options] [directories...]

optional arguments:
  --html FILE          Generate HTML report and save to specified file
  --no-sort            Do not sort duplicate groups by file size in descending order (largest first)
  --auto-clean         Automatically delete duplicate files, keeping only the first one found

positional arguments:
  directories          Directories to scan for duplicate files (one or more)
```

## Examples

### Scan single directory with size sorting (largest files first)
```bash
python src/main.py ~/Documents
```

### Scan multiple directories with size sorting (largest files first)
```bash
python src/main.py ~/Documents ~/Downloads ~/Pictures
```

### Scan with HTML report with size sorting (largest files first)
```bash
python src/main.py --html duplicates.html ~/Documents ~/Downloads
```

### Scan without size sorting
```bash
python src/main.py --no-sort ~/Documents
```

### Scan and automatically move duplicates to trash
```bash
python src/main.py --auto-clean ~/Documents
```

### Scan with HTML report and without size sorting
```bash
python src/main.py --html duplicates.html --no-sort ~/Documents ~/Downloads
```

### Scan with HTML report and auto-clean
```bash
python src/main.py --html duplicates.html --auto-clean ~/Documents ~/Downloads
```

### Scan test data with both outputs
```bash
python src/main.py --html test_report.html test_data/
```

### Scan test data without sorting
```bash
python src/main.py --html test_report.html --no-sort test_data/
```

### Scan test data with all options
```bash
python src/main.py --html test_report.html --no-sort --auto-clean test_data/
```

### Debug with VS Code
Use the launch configurations in `.vscode/launch.json`:
- `Duplicate File Finder: test_data/` - Scans test data without HTML
- `Duplicate File Finder: test_data/ with HTML` - Scans test data and generates HTML report

## Project Structure
```
duplicate-file-finder/
├── src/
│   ├── __init__.py
│   ├── main.py                         # Main entry point, prompts user even if stdout and stderr are redirected
│   ├── file_scanner.py                 # Scans directories (excludes system files)
│   ├── file_manager.py                 # Centralizes file deletion logic
│   ├── hash_calculator.py              # Computes SHA-256 hashes
│   ├── duplicate_detector.py           # Groups duplicate files by hash
│   ├── report_generator.py             # Generates text and HTML reports
│   └── templates/
│       └── report_template.jinja2      # Template for HTML report
├── tests/                              # Tests unitaires
│   ├── __init__.py
│   ├── test_file_scanner.py
│   ├── test_hash_calculator.py
│   └── test_duplicate_detector.py
├── scripts/
│   ├── generate_test_data.py           # Creates realistic test data
│   ├── validate_test_results.py        # Validates output against expected results
│   └── server.py                       # Built-in unified server for media serving and  file removal
├── .vscode/
│   └── launch.json                     # VS Code debug configurations
├── test_data/                          # Generated test data directory
│   ├── documents/
│   ├── media/
│   ├── code/
│   └── archive/
├── requirements.txt
└── README.md
```

## Performance Considerations

- **Hash Calculation**: Uses SHA-256 for reliable duplicate detection
- **Streaming File Reading**: Processes files in 4KB chunks to minimize memory usage
- **Efficient Directory Traversal**: Single pass through each directory structure
- **System File Filtering**: Excludes system files before processing to save time
- **Platform Optimization**: Platform-independent file operations with automatic path handling

## Troubleshooting

### No files found
- Ensure the directory path is correct
- Check that you have read permissions for the directory
- Verify the directory contains files (not just subdirectories)

### Permission denied errors
- Run with appropriate permissions or specify directories you have access to
- Some system directories may require elevated privileges

### Large file processing
- The application processes files in 4KB chunks, so large files are handled efficiently
- Very large directories may take time depending on disk speed

### Delete button not working
- Ensure the unified server is running: `python scripts/server.py`
- Check that the server is listening on `localhost:1080`
- Open browser console (F12) to see any errors
- Verify file permissions allow deletion

### Delete server won't start
- Check if port 1080 is already in use: `lsof -i :1080` (macOS/Linux)
- Try a different port if needed
- Ensure you have permission to bind to port 1080

### HTML report not displaying
- Ensure the file path is writable
- Check browser console for JavaScript errors
- Verify file links work by clicking on a filename
- Make sure delete server is running if using delete buttons

### CORS errors in browser
- The delete server uses `no-cors` mode to avoid CORS issues
- If you still get errors, check browser console for details

## Server Setup for File Deletion

### Quick Setup
1. Start the built-in unified server:
```bash
python scripts/server.py
```

2. Generate test data and create HTML report:
```bash
python scripts/generate_test_data.py
python src/main.py --html report.html test_data/
```

3. Open the report and click delete buttons

### Server Health Check
```bash
# Test if server is running
curl -X DELETE "http://localhost:1080/?file_path=/tmp/test.txt"

# Expected response (if file exists):
# {"status": "success", "message": "File deleted: /tmp/test.txt"}
```

## Contributing
Contributions are welcome! Please feel free to submit a pull request or open an issue for any enhancements or bug fixes.

## License
This project is licensed under the MIT License. See the LICENSE file for more details.

## Platform Compatibility
- ✅ **macOS** - Full support with `.DS_Store` exclusion
- ✅ **Windows** - Full support with `Thumbs.db` and system file exclusion
- ✅ **Linux** - Full support with standard cache exclusions

The application uses platform-independent file operations and automatically handles path separators across operating systems.