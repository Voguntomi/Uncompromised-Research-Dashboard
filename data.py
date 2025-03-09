import pandas as pd
import os


class DataHandler:
    def __init__(self, excel_file_path, pickle_file_path):
        self.excel_file_path = excel_file_path
        self.pickle_file_path = pickle_file_path
        self.raw_data = None
        self.key_name_mapping = {}

        # Load Pickle if available; otherwise, convert Excel to Pickle
        if os.path.exists(self.pickle_file_path):
            self.raw_data = self.load_data_from_pickle()
        else:
            self.raw_data = self.convert_excel_to_pickle()

        if self.raw_data is not None:
            self.create_key_name_mapping()

    def convert_excel_to_pickle(self):
        """Convert Excel to Pickle and load data"""
        try:
            df = pd.read_excel(self.excel_file_path)
            if df.empty:
                raise ValueError("The loaded Excel file is empty.")

            df.to_pickle(self.pickle_file_path)
            print(f"Excel data converted to Pickle: {self.pickle_file_path}")
            return df
        except Exception as e:
            print(f"Error converting Excel to Pickle: {e}")
            return None

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

    def get_key_from_name(self, name):
        """Get Key from Name"""
        return [key for key, value in self.key_name_mapping.items() if value == name] or None

    def fetch_data(self, key):
        """Retrieve data by key"""
        return self.raw_data[self.raw_data['Key'] == key] if key in self.raw_data['Key'].values else pd.DataFrame()

    def auto_detect_frequency(self):
        """Detect frequency (Monthly/Quarterly) based on TIME_PERIOD"""
        if "TIME_PERIOD" in self.raw_data.columns:
            self.raw_data["TIME_PERIOD"] = pd.to_datetime(self.raw_data["TIME_PERIOD"])
            time_diff = self.raw_data["TIME_PERIOD"].diff().mode()[0]
            if time_diff.days in [90, 91, 92]:
                return "quarterly"
            elif time_diff.days in [30, 31]:
                return "monthly"
        return None
