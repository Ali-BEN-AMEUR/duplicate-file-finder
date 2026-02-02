import hashlib

class HashCalculator:
    def calculate_hash(self, file_path):
        """Calculate the SHA-256 hash of a file."""
        hash_sha256 = hashlib.sha256()
        try:
            with open(file_path, 'rb') as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(byte_block)
            return hash_sha256.hexdigest()
        except (IOError, OSError) as e:
            print(f"Error reading file {file_path}: {e}")
            return None