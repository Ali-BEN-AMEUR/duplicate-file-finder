class DuplicateDetector:
    def __init__(self, file_paths_with_hashes):
        # Structure: {file_path: {'hash': hash_value, 'size': file_size}}
        self.file_data = file_paths_with_hashes
        self.duplicates_by_hash = {}

    def find_duplicates(self):
        """Group files by their hash signature."""
        for file_path, data in self.file_data.items():
            file_hash = data['hash']

            if file_hash not in self.duplicates_by_hash:
                self.duplicates_by_hash[file_hash] = []

            self.duplicates_by_hash[file_hash].append(file_path)

    def get_duplicate_groups(self):
        """Return only groups with multiple files (actual duplicates)."""
        if not self.duplicates_by_hash:
            self.find_duplicates()
        return {
            hash_key: paths 
            for hash_key, paths in self.duplicates_by_hash.items() 
            if len(paths) > 1
        }

    def get_unique_files(self):
        """Return only groups with a single file (unique files)."""
        if not self.duplicates_by_hash:
            self.find_duplicates()
        return {
            hash_key: paths 
            for hash_key, paths in self.duplicates_by_hash.items() 
            if len(paths) == 1
        }

    def get_all_groups(self):
        """Return all hash groups."""
        self.find_duplicates()
        return self.duplicates_by_hash