import pickle
import pandas as pd
from ecbdata import ecbdata

class DataRetrieval:
    def __init__(self, pickle_file_path):
        self.pickle_file_path = pickle_file_path
        self.DICT_data = {}  # Dictionary to store retrieved data
        self.key_name_mapping = {}  # Mapping of dataset keys to names
        self.raw_data = None  # Raw data loaded from the Pickle file
        self.load_pickle_data()

    def load_pickle_data(self):
        try:
            with open(self.pickle_file_path, "rb") as file:
                data = pickle.load(file)

                # Check if the loaded data is a DataFrame
                if isinstance(data, pd.DataFrame):
                    expected_columns = [
                        "Name", "Key", "Frequency", "Reference area", "Adjustment indicator",
                        "Indicators for business statistics", "Activity classification",
                        "Prices", "Stocks, Transactions, Other Flows", "Unit of measure",
                        "LFS Indicator", "LFS Breakdown", "Age breakdown", "Gender", "Series Variation"
                    ]
                    if all(col in data.columns for col in expected_columns):
                        self.raw_data = data.dropna(subset=["Name", "Key"]).reset_index(drop=True)
                        self.create_key_name_mapping(self.raw_data)
                        print("✅ Raw data loaded and cleaned successfully.")
                    else:
                        print("❌ Error: Data does not match the expected format.")
                        self.raw_data = pd.DataFrame()  # Create an empty DataFrame for safety
                else:
                    print("❌ Error: Loaded data is not a DataFrame.")
                    self.raw_data = pd.DataFrame()  # Create an empty DataFrame for safety

        except Exception as e:
            print(f"❌ Error loading Pickle file: {e}")
            self.raw_data = pd.DataFrame()  # Ensure the class can still function

    def create_key_name_mapping(self, cleaned_data):
        self.key_name_mapping = dict(zip(cleaned_data["Key"], cleaned_data["Name"]))
        print("✅ Key-name mapping created successfully.")

    def fetch_data(self, ST_key, start_date=None):
        try:
            print(f"🌍 Fetching data for key: {ST_key} from ECB Data Portal...")
            df = ecbdata.get_series(ST_key, start=start_date)
            self.DICT_data[ST_key] = df
            print(f"✅ Data for key '{ST_key}' successfully fetched.")
        except Exception as e:
            print(f"❌ Error fetching data for key {ST_key}: {e}")

    def get_adjustment_indicator(self, dataset_name):
        if dataset_name in self.key_name_mapping.values():
            key = [k for k, v in self.key_name_mapping.items() if v == dataset_name][0]
            row = self.raw_data[self.raw_data["Key"] == key]
            if not row.empty:
                return row.iloc[0]["Adjustment indicator"]
        return "⚠️ No adjustment indicator available for this dataset."

    def get_name_from_key(self, ST_key):
        return self.key_name_mapping.get(ST_key, "❓ Unknown Key")

    def get_key_from_name(self, name):
        reverse_mapping = {v: k for k, v in self.key_name_mapping.items()}
        return reverse_mapping.get(name, None)
