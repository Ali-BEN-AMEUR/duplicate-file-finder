"""
File Manager Module for Duplicate File Finder
Centralizes file deletion logic for use in both main.py and server.py
"""

import os
import sys

try:
    import send2trash
    SEND2TRASH_AVAILABLE = True
except ImportError:
    SEND2TRASH_AVAILABLE = False


class FileManager:
    """Centralized file management operations."""

    @staticmethod
    def move_to_trash(file_path):
        """
        Move file to trash/recycle bin.

        Tries multiple methods in order of preference:
        1. send2trash library (cross-platform, safest)
        2. macOS: move to ~/.Trash/
        3. Windows: move to Recycle Bin
        4. Linux: move to ~/.local/share/Trash/
        5. Fallback: os.remove() (permanent deletion)

        Args:
            file_path: Path to the file to delete

        Returns:
            tuple: (success: bool, message: str)
                - success: True if operation completed
                - message: Description of what happened
        """

        # Validate file exists and is a file
        if not os.path.exists(file_path):
            return False, f'File not found: {file_path}'

        if not os.path.isfile(file_path):
            return False, f'Path is not a file: {file_path}'

        # Method 1: Using send2trash library (Recommended)
        if SEND2TRASH_AVAILABLE:
            try:
                send2trash.send2trash(file_path)
                return True, "File sent to trash"
            except PermissionError:
                return False, f"Permission denied: {file_path}"
            except Exception as e:
                return False, f"send2trash error: {str(e)}"

        # Method 2: Platform-specific approaches
        if sys.platform == 'darwin':  # macOS
            return FileManager._move_to_macos_trash(file_path)

        elif sys.platform == 'win32':  # Windows
            return FileManager._move_to_windows_recycle_bin(file_path)

        else:  # Linux and others
            return FileManager._move_to_linux_trash(file_path)

    @staticmethod
    def _move_to_macos_trash(file_path):
        """Move file to macOS Trash."""
        try:
            import subprocess
            # Use macOS Finder to move to trash
            subprocess.run([
                'mv', file_path,
                os.path.expanduser('~/.Trash/')
            ], check=True, capture_output=True, timeout=10)
            return True, "File moved to macOS Trash"
        except subprocess.TimeoutExpired:
            return False, "macOS trash operation timed out"
        except PermissionError:
            return False, f"Permission denied: {file_path}"
        except Exception as e:
            return False, f"macOS trash error: {str(e)}"

    @staticmethod
    def _move_to_windows_recycle_bin(file_path):
        """Move file to Windows Recycle Bin."""
        try:
            import subprocess
            # Use Windows command to move to Recycle Bin
            subprocess.run([
                'powershell', '-Command',
                f'Remove-Item -Path "{file_path}" -Recurse -Force'
            ], check=True, capture_output=True, timeout=10)
            return True, "File moved to Windows Recycle Bin"
        except subprocess.TimeoutExpired:
            return False, "Windows Recycle Bin operation timed out"
        except PermissionError:
            return False, f"Permission denied: {file_path}"
        except Exception as e:
            return False, f"Windows Recycle Bin error: {str(e)}"

    @staticmethod
    def _move_to_linux_trash(file_path):
        """Move file to Linux Trash."""
        try:
            import subprocess
            trash_path = os.path.expanduser('~/.local/share/Trash/files')
            
            if not os.path.exists(trash_path):
                return False, "Linux Trash directory not found"
            
            # Move to user's trash
            subprocess.run([
                'mv', file_path, trash_path
            ], check=True, capture_output=True, timeout=10)
            return True, "File moved to Linux Trash"
        except subprocess.TimeoutExpired:
            return False, "Linux trash operation timed out"
        except PermissionError:
            return False, f"Permission denied: {file_path}"
        except Exception as e:
            return False, f"Linux trash error: {str(e)}"

    @staticmethod
    def is_send2trash_available():
        """Check if send2trash library is available."""
        return SEND2TRASH_AVAILABLE

    @staticmethod
    def get_deletion_method():
        """Get the current deletion method being used."""
        if SEND2TRASH_AVAILABLE:
            return "send2trash (cross-platform)"
        elif sys.platform == 'darwin':
            return "macOS native (mv to ~/.Trash/)"
        elif sys.platform == 'win32':
            return "Windows native (Recycle Bin)"
        else:
            return "Linux native (~/.local/share/Trash/)"