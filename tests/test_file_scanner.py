import unittest
import tempfile
import os
from src.file_scanner import FileScanner

class TestFileScanner(unittest.TestCase):

    def setUp(self):
        """Create temporary directories for testing."""
        self.temp_dir1 = tempfile.mkdtemp()
        self.temp_dir2 = tempfile.mkdtemp()

        # Create test files in temp_dir1
        self.test_file1 = os.path.join(self.temp_dir1, 'test1.txt')
        with open(self.test_file1, 'w') as f:
            f.write('test content 1')

        self.test_file2 = os.path.join(self.temp_dir1, 'test2.txt')
        with open(self.test_file2, 'w') as f:
            f.write('test content 2')

        # Create subdirectory with file in temp_dir1
        sub_dir = os.path.join(self.temp_dir1, 'subdir')
        os.makedirs(sub_dir)
        self.test_file3 = os.path.join(sub_dir, 'test3.txt')
        with open(self.test_file3, 'w') as f:
            f.write('test content 3')

        # Create test file in temp_dir2
        self.test_file4 = os.path.join(self.temp_dir2, 'test4.txt')
        with open(self.test_file4, 'w') as f:
            f.write('test content 4')

    def tearDown(self):
        """Clean up temporary files."""
        for file_path in [self.test_file1, self.test_file2, self.test_file3, self.test_file4]:
            if os.path.exists(file_path):
                os.remove(file_path)

        sub_dir = os.path.join(self.temp_dir1, 'subdir')
        if os.path.exists(sub_dir):
            os.rmdir(sub_dir)

        os.rmdir(self.temp_dir1)
        os.rmdir(self.temp_dir2)

    def test_scan_single_directory(self):
        """Test scanning a single directory."""
        scanner = FileScanner([self.temp_dir1])
        scanner.scan()

        file_paths = scanner.get_file_paths()

        # Should find 3 files in temp_dir1
        self.assertEqual(len(file_paths), 3)
        self.assertIn(self.test_file1, file_paths)
        self.assertIn(self.test_file2, file_paths)
        self.assertIn(self.test_file3, file_paths)

    def test_scan_multiple_directories(self):
        """Test scanning multiple directories."""
        scanner = FileScanner([self.temp_dir1, self.temp_dir2])
        scanner.scan()

        file_paths = scanner.get_file_paths()

        # Should find 4 files total (3 in temp_dir1, 1 in temp_dir2)
        self.assertEqual(len(file_paths), 4)
        self.assertIn(self.test_file1, file_paths)
        self.assertIn(self.test_file4, file_paths)

    def test_file_sizes(self):
        """Test that file sizes are correctly recorded."""
        scanner = FileScanner([self.temp_dir1])
        scanner.scan()

        file_paths = scanner.get_file_paths()

        # Verify file sizes
        self.assertGreater(file_paths[self.test_file1], 0)
        self.assertGreater(file_paths[self.test_file2], 0)
        self.assertGreater(file_paths[self.test_file3], 0)

    def test_directory_summary(self):
        """Test that directory summary is correct."""
        scanner = FileScanner([self.temp_dir1, self.temp_dir2])
        scanner.scan()

        summary = scanner.get_summary()

        # Should have summary for both directories
        self.assertIn(self.temp_dir1, summary)
        self.assertIn(self.temp_dir2, summary)

        # Verify counts
        self.assertEqual(summary[self.temp_dir1], 3)
        self.assertEqual(summary[self.temp_dir2], 1)

    def test_empty_directory(self):
        """Test scanning an empty directory."""
        empty_dir = tempfile.mkdtemp()

        try:
            scanner = FileScanner([empty_dir])
            scanner.scan()

            file_paths = scanner.get_file_paths()

            # Should find no files
            self.assertEqual(len(file_paths), 0)
        finally:
            os.rmdir(empty_dir)

    def test_invalid_directory(self):
        """Test behavior with invalid directory path."""
        invalid_dir = '/nonexistent/path/to/directory'

        scanner = FileScanner([invalid_dir])
        scanner.scan()

        file_paths = scanner.get_file_paths()

        # Should handle gracefully and return empty
        self.assertEqual(len(file_paths), 0)

if __name__ == '__main__':
    unittest.main()