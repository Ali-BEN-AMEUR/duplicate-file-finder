import unittest
from src.duplicate_detector import DuplicateDetector

class TestDuplicateDetector(unittest.TestCase):

    def setUp(self):
        """Set up test fixtures."""
        self.file_data = {
            '/path/file1.txt': {'hash': 'hash1', 'size': 1024},
            '/path/file2.txt': {'hash': 'hash2', 'size': 2048},
            '/path/file3.txt': {'hash': 'hash1', 'size': 1024},  # Duplicate of file1.txt
            '/path/file4.txt': {'hash': 'hash1', 'size': 1024},  # Another duplicate of file1.txt
            '/path/file5.txt': {'hash': 'hash3', 'size': 512},
        }

    def test_identify_duplicates(self):
        """Test that duplicates are correctly identified."""
        detector = DuplicateDetector(self.file_data)
        duplicates = detector.get_duplicate_groups()

        # Should find duplicates only for hash1 (3 files)
        self.assertEqual(len(duplicates), 1)
        self.assertIn('hash1', duplicates)
        self.assertEqual(len(duplicates['hash1']), 3)
        self.assertIn('/path/file1.txt', duplicates['hash1'])
        self.assertIn('/path/file3.txt', duplicates['hash1'])
        self.assertIn('/path/file4.txt', duplicates['hash1'])

    def test_no_duplicates(self):
        """Test when no duplicates exist."""
        file_data = {
            '/path/file1.txt': {'hash': 'hash1', 'size': 1024},
            '/path/file2.txt': {'hash': 'hash2', 'size': 2048},
            '/path/file3.txt': {'hash': 'hash3', 'size': 512},
        }

        detector = DuplicateDetector(file_data)
        duplicates = detector.get_duplicate_groups()

        # Should find no duplicates
        self.assertEqual(len(duplicates), 0)

    def test_all_groups(self):
        """Test retrieval of all hash groups including non-duplicates."""
        detector = DuplicateDetector(self.file_data)
        all_groups = detector.get_all_groups()

        # Should contain all hashes
        self.assertEqual(len(all_groups), 3)
        self.assertIn('hash1', all_groups)
        self.assertIn('hash2', all_groups)
        self.assertIn('hash3', all_groups)

        # Verify counts
        self.assertEqual(len(all_groups['hash1']), 3)
        self.assertEqual(len(all_groups['hash2']), 1)
        self.assertEqual(len(all_groups['hash3']), 1)

    def test_single_file_per_hash(self):
        """Test when each file has unique hash."""
        file_data = {
            '/path/unique1.txt': {'hash': 'unique_hash1', 'size': 100},
            '/path/unique2.txt': {'hash': 'unique_hash2', 'size': 200},
        }

        detector = DuplicateDetector(file_data)
        duplicates = detector.get_duplicate_groups()

        self.assertEqual(len(duplicates), 0)

if __name__ == '__main__':
    unittest.main()