import os

class FileScanner:
    def __init__(self, directories):
        self.directories = directories
        self.file_paths = {}
        # System files to exclude
        self.excluded_files = {
            '.DS_Store',           # macOS
            'Thumbs.db',           # Windows
            'desktop.ini',         # Windows
            '.gitkeep',            # Git
            '.gitignore',          # Git
            '.git',                # Git directory
            '__pycache__',         # Python cache
            '.pytest_cache',       # Pytest cache
            '.vscode',             # VS Code settings
            '.idea',               # JetBrains IDE
            '*.pyc',               # Python compiled files
            '*.pyo',               # Python optimized
        }

    def scan(self):
        """Scan all directories and populate file_paths."""
        for directory in self.directories:
            self._traverse_directory(directory)
        return self.file_paths

    def _is_excluded(self, file_path):
        """Check if file should be excluded from scanning."""
        file_name = os.path.basename(file_path)

        # Check exact matches
        if file_name in self.excluded_files:
            return True

        # Check for system files and directories
        if file_name.startswith('.'):
            return True

        # Check extensions (for .pyc, .pyo, etc.)
        for excluded in self.excluded_files:
            if excluded.startswith('*.'):
                extension = excluded[1:]
                if file_name.endswith(extension):
                    return True

        return False

    def _traverse_directory(self, directory):
        if not os.path.isdir(directory):
            print(f"{directory} is not a valid directory.")
            return

        for root, dirs, files in os.walk(directory):
            # Filter out excluded directories in-place (prevents descending into them)
            dirs[:] = [d for d in dirs if not self._is_excluded(os.path.join(root, d))]

            for file in files:
                file_path = os.path.join(root, file)

                # Skip excluded files
                if self._is_excluded(file_path):
                    continue

                try:
                    file_size = os.path.getsize(file_path)
                    self.file_paths[file_path] = file_size
                except (IOError, OSError) as e:
                    print(f"Error accessing file {file_path}: {e}")

    def get_file_paths(self):
        """Return dictionary of file paths and their sizes."""
        return self.file_paths

    def get_summary(self):
        """Return count of files per directory."""
        summary = {}
        for directory in self.directories:
            count = sum(1 for path in self.file_paths if path.startswith(directory))
            summary[directory] = count
        return summary

""" une liste complète des fichiers systmes a exclure
        # System files to exclude
        self.excluded_files = {
            # macOS
            '.DS_Store',
            '.AppleDouble',
            '.LSOverride',
            '._*',
            '.Spotlight-V100',
            '.Trashes',

            # Windows
            'Thumbs.db',
            'thumbs.db',
            'desktop.ini',
            'Desktop.ini',
            '$RECYCLE.BIN',
            'System Volume Information',
            '.TemporaryItems',
            'ehthumbs.db',
            'ehthumbs_vista.db',

            # Version Control
            '.git',
            '.gitkeep',
            '.gitignore',
            '.gitattributes',
            '.hg',
            '.svn',
            '.cvs',

            # Python
            '__pycache__',
            '.pytest_cache',
            '.pyc',
            '.pyo',
            '.pyd',
            '.so',
            '*.egg-info',
            '.Python',
            'pip-log.txt',
            'pip-delete-this-directory.txt',

            # IDEs
            '.vscode',
            '.idea',
            '.sublime-project',
            '.sublime-workspace',
            '.project',
            '.classpath',
            '.c9',
            '*.swp',
            '*.swo',
            '*~',
            '.DS_Store',

            # Node.js
            'node_modules',
            'npm-debug.log',
            '.npm',

            # Virtual Environments
            'venv',
            'env',
            '.venv',
            '.env',

            # Build/Dist
            'build',
            'dist',
            '*.egg',
            '.eggs',
        }
"""