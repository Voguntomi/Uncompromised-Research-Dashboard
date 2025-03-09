import pandas as pd
import os

class DataRetrieval:
    def __init__(self, file_path):
        self.file_path = file_path
        self.DICT_data = {}
        self.key_name_mapping = {}

    def load_raw_data_from_local(self):
        """Load raw data from a local embedded Excel file."""
        try:
            # Check if the file exists in the local path
            if os.path.exists(self.file_path):
                # Load the Excel data from the local path
                raw_data = pd.read_excel(self.file_path, sheet_name=None)  # Load all sheets as a dictionary
                return raw_data
            else:
                raise FileNotFoundError(f"The file {self.file_path} does not exist in the repository.")
        except Exception as e:
            print(f"Error loading data: {e}")
            return None

    def create_key_name_mapping(self, raw_data):
        """Create a mapping between keys (sheet names) and dataset names."""
        if raw_data:
            for sheet_name in raw_data.keys():
                self.key_name_mapping[sheet_name] = sheet_name  # Simple key-name mapping
            return self.key_name_mapping
        return {}

    def get_key_from_name(self, dataset_name):
        """Return the key(s) associated with a dataset name."""
        return [key for key, name in self.key_name_mapping.items() if name == dataset_name]

    def fetch_data(self, key):
        """Fetch the data associated with the specified key."""
        if key in self.DICT_data:
            return self.DICT_data[key]
        # Assuming raw data is loaded and stored in a dictionary of DataFrames (by sheet names)
        raw_data = self.load_raw_data_from_local()
        if raw_data:
            self.DICT_data[key] = raw_data.get(key)
            return self.DICT_data[key]
        return None
