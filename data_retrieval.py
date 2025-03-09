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
            self.create_key_name_mapping(self.raw_data)  # Pass the raw_data DataFrame

    def load_data_from_pickle(self):
        """Load data from Pickle file"""
        try:
            df = pd.read_pickle(self.pickle_file_path)
            print("Data loaded successfully from Pickle.")
            return df
        except Exception as e:
            print(f"Error loading Pickle file: {e}")
            return None

    def create_key_name_mapping(self, df):
        """Create key-name mapping by ensuring there are no missing values in 'Key' and 'Name' columns"""
        # Check if 'Key' and 'Name' columns exist in the DataFrame
        if 'Key' not in df.columns or 'Name' not in df.columns:
            raise ValueError("The required 'Key' and 'Name' columns are not present in the data.")

        # Print initial state of missing values in 'Key' and 'Name' columns for debugging
        print("Missing values in 'Key' and 'Name' columns before cleaning:")
        print(df[['Key', 'Name']].isna().sum())

        # Fill missing values in 'Key' and 'Name' columns
        df['Key'] = df['Key'].fillna('Unknown')  # Replace NaN with 'Unknown'
        df['Name'] = df['Name'].fillna('Unknown')  # Replace NaN with 'Unknown'

        # Replace any empty strings or None with 'Unknown'
        df['Key'] = df['Key'].replace(['', None], 'Unknown')
        df['Name'] = df['Name'].replace(['', None], 'Unknown')

        # Print the state of missing values after cleaning for debugging
        print("Missing values in 'Key' and 'Name' columns after cleaning:")
        print(df[['Key', 'Name']].isna().sum())

        # Check for rows that still have missing values after cleaning
        missing_rows = df[df[['Key', 'Name']].isna().any(axis=1)]
        if missing_rows.shape[0] > 0:
            print(f"There are still missing values in 'Key' or 'Name' columns after cleaning. Rows:")
            print(missing_rows)
            raise ValueError("There are still missing values in 'Key' or 'Name' columns after cleaning.")

        # Create key-name mapping
        self.key_name_mapping = dict(zip(df['Key'], df['Name']))
        print("Key-Name mapping created successfully.")
