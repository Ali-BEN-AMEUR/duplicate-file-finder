#!/usr/bin/env python3
"""
Unified Server for Duplicate File Finder
Handles both media serving and file deletion for HTML reports.

Usage:
    python scripts/server.py

The server listens on http://localhost:1080 and provides:
- File serving (all file types, including media)
- File deletion functionality

Examples:
    File serving: http://localhost:1080/?file_path=/path/to/file.jpg
    File deletion: DELETE http://localhost:1080/?file_path=/path/to/file.txt
"""

import os
import sys
import json
import mimetypes
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler

# Import the centralized file manager
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from file_manager import FileManager


class UnifiedHandler(BaseHTTPRequestHandler):
    """HTTP request handler for file serving and deletion."""

    # Common media MIME types
    MEDIA_TYPES = {
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.gif': 'image/gif',
        '.webp': 'image/webp',
        '.svg': 'image/svg+xml',
        '.bmp': 'image/bmp',
        '.tiff': 'image/tiff',
        '.mp4': 'video/mp4',
        '.webm': 'video/webm',
        '.mov': 'video/quicktime',
        '.avi': 'video/x-msvideo',
        '.mkv': 'video/x-matroska',
        '.flv': 'video/x-flv',
        '.wmv': 'video/x-ms-wmv',
        '.m4v': 'video/x-m4v',
        '.mp3': 'audio/mpeg',
        '.wav': 'audio/wav',
        '.flac': 'audio/flac',
        '.aac': 'audio/aac',
        '.ogg': 'audio/ogg',
        '.m4a': 'audio/mp4',
        '.wma': 'audio/x-ms-wma',
        '.opus': 'audio/opus',
    }

    def _send_json_response(self, status_code, status, message):
        """Send a JSON response with proper headers."""
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        response = {
            'status': status,
            'message': message
        }
        self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))

    def _send_error_response(self, status_code, message):
        """Send a JSON error response with proper UTF-8 encoding."""
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        response = {
            'status': 'error',
            'message': message
        }
        self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))

    def _get_valid_file_path(self):
        """
        Extract and validate file path from request.
        
        Handles UTF-8 encoded file paths correctly, including
        characters with accents like 'é', 'à', 'ç', etc.
        """
        try:
            # Parse the query string to get the file path
            parsed_url = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(parsed_url.query)
            file_path = params.get('file_path', [None])[0]

            if not file_path:
                self._send_error_response(400, 'Missing file_path parameter')
                print(f"✗ Missing file_path parameter in request")
                return None

            # Decode the URL-encoded file path (handles UTF-8 correctly)
            file_path = urllib.parse.unquote(file_path, encoding='utf-8')
            
            return file_path

        except Exception as e:
            error_msg = f'Error parsing file path: {str(e)}'
            self._send_error_response(400, error_msg)
            print(f"✗ {error_msg}")
            return None

    def do_DELETE(self):
        """Handle DELETE requests for file deletion."""
        print("Received DELETE request")
        try:
            file_path = self._get_valid_file_path()
            if not file_path:
                return

            print(f"Attempting to delete file: {file_path}")

            # Use centralized FileManager for deletion
            success, message = FileManager.move_to_trash(file_path)

            if success:
                print(f"✓ {message}: {file_path}")
                self._send_json_response(200, 'success', f'{message}: {file_path}')
            else:
                print(f"✗ {message}")
                self._send_error_response(500, message)

        except Exception as e:
            print(f"✗ Server error: {str(e)}")
            self._send_error_response(500, f'Server error: {str(e)}')

    def do_GET(self):
        """Handle GET requests for file serving."""
        print("Received GET request")
        try:
            file_path = self._get_valid_file_path()
            if not file_path:
                return

            print(f"Serving file: {file_path}")

            # Validate file exists and is a file
            if not os.path.exists(file_path):
                self._send_error_response(404, f'File not found: {file_path}')
                print(f"✗ File not found: {file_path}")
                return

            if not os.path.isfile(file_path):
                self._send_error_response(400, f'Path is not a file: {file_path}')
                print(f"✗ Path is not a file: {file_path}")
                return

            # Get file extension and MIME type
            _, file_ext = os.path.splitext(file_path)
            mime_type = self.MEDIA_TYPES.get(file_ext.lower())

            if not mime_type:
                mime_type, _ = mimetypes.guess_type(file_path)
                if not mime_type:
                    # Default to plain text for unknown extensions
                    mime_type = 'text/plain; charset=utf-8'

            # Send file
            try:
                with open(file_path, 'rb') as f:
                    file_size = os.path.getsize(file_path)

                    self.send_response(200)
                    self.send_header('Content-type', mime_type)
                    self.send_header('Content-Length', str(file_size))
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.send_header('Cache-Control', 'public, max-age=3600')
                    # Important pour Safari: ajouter Content-Disposition
                    self.send_header('Content-Disposition', 'inline')
                    self.end_headers()

                    f.seek(0)
                    self.wfile.write(f.read())

                    print(f"✓ Served: {file_path} ({mime_type})")

            except PermissionError:
                self._send_error_response(403, f'Permission denied: {file_path}')
                print(f"✗ Permission denied: {file_path}")

            except Exception as e:
                self._send_error_response(500, f'Error serving file: {str(e)}')
                print(f"✗ Error serving file: {file_path} - {str(e)}")

        except Exception as e:
            print(f"✗ Server error: {str(e)}")
            self._send_error_response(500, f'Server error: {str(e)}')

    def do_OPTIONS(self):
        """Handle CORS preflight requests."""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def log_message(self, format, *args):
        """Override log_message to suppress default logging."""
        pass


def main():
    """Start the unified server."""
    host = 'localhost'
    port = 1080

    server_address = (host, port)
    httpd = HTTPServer(server_address, UnifiedHandler)

    print("=" * 60)
    print("Unified Server for Duplicate File Finder")
    print("=" * 60)
    print(f"Server listening on http://{host}:{port}")

    print("\n✓ Available endpoints:")
    print(f"  File serving: GET http://{host}:{port}/?file_path=/path/to/file")
    print(f"  File deletion: DELETE http://{host}:{port}/?file_path=/path/to/file")

    print(f"\n✓ Deletion method: {FileManager.get_deletion_method()}")

    if FileManager.is_send2trash_available():
        print("  ✓ send2trash library available (cross-platform)")
    else:
        print("  ℹ Using platform-specific methods")
        print("  Optional: Run 'pip install send2trash' for better compatibility")

    print("\nSupported file types:")
    print("  Media:   JPG, PNG, GIF, WebP, SVG, MP4, WebM, MOV, AVI, MKV, MP3, WAV, etc.")
    print("  Other:   All file types (served with appropriate MIME types)")

    print("\n✓ UTF-8 encoding support for international file paths")
    print("  (Supports accented characters: é, à, ç, ñ, etc.)")

    print("\nPress Ctrl+C to stop the server")
    print("=" * 60)
    print()

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\nServer stopped by user")
        httpd.server_close()
        sys.exit(0)


if __name__ == '__main__':
    main()