import os
from datetime import datetime
from pathlib import Path


class ReportGenerator:
    def __init__(self):
        """Initialize the report generator with template."""
        self.template_path = Path(__file__).parent / 'templates' / 'report_template.jinja2'
        self.template = self._load_template()

    def _load_template(self):
        """Load the HTML template from file."""
        try:
            with open(self.template_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"Template not found at {self.template_path}")

    def generate_report(self, directory_summary, duplicate_groups, file_data, deleted_files=None):
        """
        Generate a comprehensive text report.

        Args:
            directory_summary: {directory: file_count}
            duplicate_groups: {hash: [file_paths]} (already sorted if needed)
            file_data: {file_path: {'hash': hash, 'size': size, 'deleted': bool}}
            deleted_files: List of deleted file paths (if auto-clean was used)
        """
        report_lines = []

        # Summary section
        report_lines.append("=" * 60)
        report_lines.append("DUPLICATE FILE FINDER REPORT")
        report_lines.append("=" * 60)
        report_lines.append("")

        # Directory scan summary
        report_lines.append("SCAN SUMMARY:")
        report_lines.append("-" * 60)
        total_files = 0
        for directory, count in directory_summary.items():
            report_lines.append(f"  Directory: {directory}")
            report_lines.append(f"    Files processed: {count}")
            total_files += count

        report_lines.append("")
        report_lines.append(f"Total files processed: {total_files}")
        report_lines.append("")

        # Auto-clean summary
        if deleted_files:
            deleted_size = sum(file_data[f]['size'] for f in deleted_files if f in file_data)
            report_lines.append("AUTO-CLEAN SUMMARY:")
            report_lines.append("-" * 60)
            report_lines.append(f"  Files deleted: {len(deleted_files)}")
            report_lines.append(f"  Space freed: {self._format_size(deleted_size)}")
            report_lines.append("")

        # Duplicates section
        report_lines.append("DUPLICATES FOUND:")
        report_lines.append("-" * 60)

        if not duplicate_groups:
            report_lines.append("  No duplicate files detected.")
        else:
            for group_num, (file_hash, paths) in enumerate(duplicate_groups.items(), 1):
                report_lines.append(f"  Group {group_num} (Hash: {file_hash[:16]}...):")
                for idx, path in enumerate(paths):
                    if file_data and path in file_data and file_data[path].get('deleted'):
                        report_lines.append(f"    - {path} [DELETED]")
                    elif idx == 0:
                        report_lines.append(f"    - {path} [KEPT]")
                    else:
                        report_lines.append(f"    - {path}")
                report_lines.append("")

        report_lines.append("=" * 60)
        return "\n".join(report_lines)

    def generate_html_report(self, directory_summary, duplicate_groups, file_data, auto_clean=False):
        """
        Generate an HTML report with clickable links to duplicate files.

        Args:
            directory_summary: {directory: file_count}
            duplicate_groups: {hash: [file_paths]} (already sorted if needed)
            file_data: {file_path: {'hash': hash, 'size': size, 'deleted': bool}}
            auto_clean: Boolean indicating if auto-clean was used
        """
        # Generate summary rows
        summary_rows = self._generate_summary_rows(directory_summary)
        total_files = sum(directory_summary.values())

        # Generate duplicates content
        duplicates_content = self._generate_duplicates_content(duplicate_groups, file_data, auto_clean)
        total_duplicate_groups = len(duplicate_groups)
        total_duplicate_files = sum(len(paths) - 1 for paths in duplicate_groups.values())

        # Calculate deleted stats
        deleted_files = [f for f in file_data if file_data[f].get('deleted')]
        deleted_size = sum(file_data[f]['size'] for f in deleted_files)

        # Fill template placeholders
        html = self.template
        html = html.replace('{TIMESTAMP}', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        html = html.replace('{CSS_STYLES}', self._get_css_styles())
        html = html.replace('{JAVASCRIPT_CODE}', self._get_javascript())
        html = html.replace('{SUMMARY_ROWS}', summary_rows)
        html = html.replace('{TOTAL_FILES}', str(total_files))
        html = html.replace('{DUPLICATE_GROUPS}', str(total_duplicate_groups))
        html = html.replace('{DUPLICATE_FILES}', str(total_duplicate_files))
        html = html.replace('{DUPLICATES_CONTENT}', duplicates_content)
        
        # Add auto-clean info if applicable
        if auto_clean:
            auto_clean_info = f'<p class="auto-clean-info">✓ Auto-clean completed: {len(deleted_files)} files deleted, {self._format_size(deleted_size)} space freed</p>'
            html = html.replace('{DUPLICATES_CONTENT}', auto_clean_info + '\n' + duplicates_content)

        return html

    def sort_duplicates_by_size(self, duplicate_groups, file_data):
        """
        Sort duplicate groups by file size in descending order.
        This method is called once in main.py before generating reports.

        Args:
            duplicate_groups: {hash: [file_paths]}
            file_data: {file_path: {'hash': hash, 'size': size}}

        Returns:
            Sorted dictionary of duplicate groups by file size (largest first)
        """
        # Create list of tuples (file_hash, paths, size)
        groups_with_sizes = []

        for file_hash, paths in duplicate_groups.items():
            # Get the file size from the first file in the group
            if paths and paths[0] in file_data:
                file_size = file_data[paths[0]]['size']
            else:
                file_size = 0

            groups_with_sizes.append((file_hash, paths, file_size))

        # Sort by file size in descending order (largest files first)
        sorted_groups = sorted(groups_with_sizes, key=lambda x: x[2], reverse=True)

        # Convert back to dictionary format
        return {file_hash: paths for file_hash, paths, _ in sorted_groups}

    def _generate_summary_rows(self, directory_summary):
        """Generate HTML rows for the summary table."""
        rows = []
        for directory, count in directory_summary.items():
            rows.append(f'                    <tr>')
            rows.append(f'                        <td>{directory}</td>')
            rows.append(f'                        <td>{count}</td>')
            rows.append(f'                    </tr>')
        return '\n'.join(rows)

    def _generate_duplicates_content(self, duplicate_groups, file_data, auto_clean=False):
        """Generate HTML content for duplicates section."""
        if not duplicate_groups:
            return '            <p class="no-duplicates">No duplicate files detected.</p>'

        groups_html = []
        for group_num, (file_hash, paths) in enumerate(duplicate_groups.items(), 1):
            # Get file size
            if paths and paths[0] in file_data:
                file_size = file_data[paths[0]]['size']
                size_str = self._format_size(file_size)
            else:
                size_str = "Unknown"

            # Build group HTML
            group_html = f'            <div class="duplicate-group">\n'
            group_html += f'                <h3>Group {group_num} • {len(paths)} files • {size_str}</h3>\n'
            group_html += f'                <ul class="file-list">\n'

            # Add file items
            for idx, path in enumerate(paths):
                is_deleted = file_data.get(path, {}).get('deleted', False)
                
                group_html += f'                    <li'
                
                # Add CSS class for deleted files
                if is_deleted:
                    group_html += f' class="file-deleted"'
                elif idx == 0:
                    group_html += f' class="file-kept"'
                
                group_html += f'>\n'

                # Show delete button only if not auto-clean and not deleted
                if not auto_clean and not is_deleted:
                    file_url = self._get_file_url(path)
                    delete_url = self._get_delete_url(path)

                    group_html += f'                        <button class="delete-btn" onclick="deleteFile(\'{self._escape_js_string(path)}\', \'{delete_url}\')" title="Delete file">\n'
                    group_html += f'                            &#128465;\n'
                    group_html += f'                        </button>\n'
                    group_html += f'                        <a href="{file_url}">{path}</a>\n'
                else:
                    # Show status for deleted/kept files
                    if is_deleted:
                        group_html += f'                        <span class="file-status deleted">✓ DELETED</span>\n'
                        group_html += f'                        <span class="file-path-deleted">{path}</span>\n'
                    elif idx == 0:
                        file_url = self._get_file_url(path)
                        group_html += f'                        <span class="file-status kept">★ KEPT</span>\n'
                        group_html += f'                        <a href="{file_url}">{path}</a>\n'
                    else:
                        group_html += f'                        <span>{path}</span>\n'

                group_html += f'                    </li>\n'

            group_html += f'                </ul>\n'
            group_html += f'            </div>'

            groups_html.append(group_html)

        return '\n'.join(groups_html)

    def _escape_js_string(self, string):
        """Escape special characters for JavaScript strings."""
        return string.replace("'", "\\'").replace('"', '\\"').replace('\n', '\\n')

    def _get_css_styles(self):
        """Return additional CSS styles for the HTML report."""
        return ''''''

    def _get_javascript(self):
        """Return additional JavaScript code for file deletion functionality."""
        return ''''''

    def _get_file_url(self, file_path):
        """Generate a URL for the file path.
        
        Uses unified server (localhost:1080) for ALL files.
        This ensures compatibility across all browsers (Safari, Firefox, Chrome).
        """
        abs_path = os.path.abspath(file_path)
        from urllib.parse import quote
        
        # Encode the path properly for URL (handles spaces, accents, etc.)
        encoded_path = quote(abs_path, safe='')
        
        # Use unified server for ALL files (not just media)
        return f'http://localhost:1080/?file_path={encoded_path}'

    def _get_file_file_url(self, file_path):
        """Generate a file:// URL for the file path."""
        abs_path = os.path.abspath(file_path)
        if os.name == 'nt':  # Windows
            file_url = 'file:///' + abs_path.replace('\\', '/')
        else:  # macOS/Linux
            file_url = 'file://' + abs_path
        return file_url

    def _get_file_media_url(self, file_path):
        """Generate a URL for the file path.
        
        Uses unified server (localhost:1080) for both:
        - Media files (images, videos, audio) via /media endpoint
        - Other files via file:// protocol
        """
        abs_path = os.path.abspath(file_path)

        # List of media file extensions
        media_extensions = {
            # Images
            '.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg', '.bmp', '.tiff',
            # Videos
            '.mp4', '.webm', '.mov', '.avi', '.mkv', '.flv', '.wmv', '.m4v',
            # Audio
            '.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a', '.wma', '.opus'
        }

        # Get file extension
        _, file_ext = os.path.splitext(file_path)

        # Use unified server for media files
        if file_ext.lower() in media_extensions:
            from urllib.parse import quote
            encoded_path = quote(abs_path, safe='')
            return f'http://localhost:1080/?file_path={encoded_path}'

        # Use file:// protocol for other files
        if os.name == 'nt':  # Windows
            file_url = 'file:///' + abs_path.replace('\\', '/')
        else:  # macOS/Linux
            file_url = 'file://' + abs_path

        return file_url

    def _get_delete_url(self, file_path):
        """Generate a delete URL for the unified server endpoint."""
        abs_path = os.path.abspath(file_path)
        from urllib.parse import quote
        encoded_path = quote(abs_path, safe='')
        return f'http://localhost:1080/?file_path={encoded_path}'

    def _format_size(self, size_bytes):
        """Format bytes to human-readable size."""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} PB"