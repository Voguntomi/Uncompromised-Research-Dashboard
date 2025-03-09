import pandas as pd
import os


class DataRetrieval:
    def __init__(self, pickle_file_path):
        self.pickle_file_path = pickle_file_path
        self.raw_data = None
        self.key_name_mapping = {}

        # Load Pickle if available
        if os.path.exists(self.pickle_file_path):
            self.raw_data = self.load_data_from_pickle()
        else:
            print(f"Pickle file {self.pickle_file_path} does not exist.")
            self.raw_data = None

        if self.raw_data is not None:
            self.create_key_name_mapping()

    def load_data_from_pickle(self):
        """Load data from Pickle file"""
        try:
            df = pd.read_pickle(self.pickle_file_path)
            print("Data loaded successfully from Pickle.")
            return df
        except Exception as e:
            print(f"Error loading Pickle file: {e}")
            return None

    def create_key_name_mapping(self):
        """Create Key-Name mapping from dataset"""
        if 'Key' not in self.raw_data.columns or 'Name' not in self.raw_data.columns:
            raise ValueError("Missing 'Key' or 'Name' columns in data.")

        self.raw_data.loc[:, 'Key'] = self.raw_data['Key'].fillna('Unknown')
        self.raw_data.loc[:, 'Name'] = self.raw_data['Name'].fillna('Unknown')
        self.key_name_mapping = dict(zip(self.raw_data['Key'], self.raw_data['Name']))
        print("Key-Name mapping created successfully.")
