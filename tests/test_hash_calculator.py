import unittest
import tempfile
import os
from src.hash_calculator import HashCalculator

class TestHashCalculator(unittest.TestCase):

    def setUp(self):
        """Create temporary test files."""
        self.hash_calculator = HashCalculator()

        # Create temporary file with known content
        self.temp_file1 = tempfile.NamedTemporaryFile(mode='w', delete=False)
        self.temp_file1.write('test content')
        self.temp_file1.close()

        # Create another file with same content
        self.temp_file2 = tempfile.NamedTemporaryFile(mode='w', delete=False)
        self.temp_file2.write('test content')
        self.temp_file2.close()

        # Create file with different content
        self.temp_file3 = tempfile.NamedTemporaryFile(mode='w', delete=False)
        self.temp_file3.write('different content')
        self.temp_file3.close()

    def tearDown(self):
        """Clean up temporary files."""
        for temp_file in [self.temp_file1, self.temp_file2, self.temp_file3]:
            if os.path.exists(temp_file.name):
                os.remove(temp_file.name)

    def test_calculate_hash(self):
        """Test that hash is calculated correctly."""
        hash_value = self.hash_calculator.calculate_hash(self.temp_file1.name)

        # Hash should be a valid SHA-256 hex string (64 characters)
        self.assertIsNotNone(hash_value)
        if (hash_value is not None):
            self.assertEqual(len(hash_value), 64)
            self.assertTrue(all(c in '0123456789abcdef' for c in hash_value))

    def test_identical_files_same_hash(self):
        """Test that identical files produce the same hash."""
        hash1 = self.hash_calculator.calculate_hash(self.temp_file1.name)
        hash2 = self.hash_calculator.calculate_hash(self.temp_file2.name)

        self.assertEqual(hash1, hash2)

    def test_different_files_different_hash(self):
        """Test that different files produce different hashes."""
        hash1 = self.hash_calculator.calculate_hash(self.temp_file1.name)
        hash3 = self.hash_calculator.calculate_hash(self.temp_file3.name)

        self.assertNotEqual(hash1, hash3)

    def test_nonexistent_file(self):
        """Test handling of nonexistent file."""
        hash_value = self.hash_calculator.calculate_hash('/nonexistent/file.txt')

        # Should return None for nonexistent file
        self.assertIsNone(hash_value)

    def test_large_file_hash(self):
        """Test hash calculation for larger file."""
        # Create a larger temporary file
        large_file = tempfile.NamedTemporaryFile(mode='w', delete=False)
        large_file.write('x' * 1000000)  # 1MB of data
        large_file.close()

        try:
            hash_value = self.hash_calculator.calculate_hash(large_file.name)

            # Should successfully hash the large file
            self.assertIsNotNone(hash_value)
            if (hash_value is not None):
                self.assertEqual(len(hash_value), 64)
        finally:
            os.remove(large_file.name)

    def test_binary_file_hash(self):
        """Test hash calculation for binary file."""
        binary_file = tempfile.NamedTemporaryFile(delete=False)
        binary_file.write(b'\x00\x01\x02\x03\x04\x05')
        binary_file.close()

        try:
            hash_value = self.hash_calculator.calculate_hash(binary_file.name)

            # Should successfully hash binary file
            self.assertIsNotNone(hash_value)
            if (hash_value is not None):
                self.assertEqual(len(hash_value), 64)
        finally:
            os.remove(binary_file.name)

if __name__ == '__main__':
    unittest.main()