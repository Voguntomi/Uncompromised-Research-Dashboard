import pandas as pd
from ecbdata import ecbdata


class DataRetrieval:
    def __init__(self, excel_file_path):
        """
        Initialize the DataRetrieval class with the Excel file path.
        """
        self.DICT_data = {}  # Dictionary to store retrieved data
        self.key_name_mapping = {}  # Mapping of dataset keys to names
        self.raw_data = None  # Raw data loaded from the Excel file
        self.excel_file_path = excel_file_path  # Path to the Excel file

    def load_raw_data(self):
        """
        Load the raw data from the Excel file and clean it.
        """
        print("\nLoading raw data from the Excel file...")
        self.raw_data = pd.read_excel(self.excel_file_path, sheet_name="Sheet1", header=0)

        # Define column names for the dataset
        self.raw_data.columns = [
            "Name", "Key", "Frequency", "Reference area", "Adjustment indicator",
            "Indicators for business statistics", "Activity classification",
            "Prices", "Stocks, Transactions, Other Flows", "Unit of measure",
            "LFS Indicator", "LFS Breakdown", "Age breakdown", "Gender", "Series Variation"
        ]

        # Drop rows where "Name" or "Key" is empty
        self.raw_data = self.raw_data.dropna(subset=["Name", "Key"]).reset_index(drop=True)
        print("Raw data loaded and cleaned successfully.")
        return self.raw_data

    def create_key_name_mapping(self, cleaned_data):
        """
        Create a mapping of dataset keys to their respective names.
        """
        print("\nCreating key-name mapping...")
        self.key_name_mapping = dict(zip(cleaned_data["Key"], cleaned_data["Name"]))
        print("Key-name mapping created successfully.")

    def fetch_data(self, ST_key, start_date=None):
        """
        Fetch data from ECB Data Portal using the ecbdata library.
        """
        try:
            print(f"\nFetching data for key: {ST_key} from ECB Data Portal...")
            df = ecbdata.get_series(ST_key, start=start_date)
            self.DICT_data[ST_key] = df
            print(f"Data for key '{ST_key}' successfully fetched.")
        except Exception as e:
            print(f"Error fetching data for key {ST_key}: {e}")

    def get_adjustment_indicator(self, dataset_name):
        """
        Retrieve the Adjustment Indicator for a given dataset name.
        """
        if dataset_name in self.key_name_mapping.values():
            key = [k for k, v in self.key_name_mapping.items() if v == dataset_name][0]
            row = self.raw_data[self.raw_data["Key"] == key]
            if not row.empty:
                return row.iloc[0]["Adjustment indicator"]
        return "No adjustment indicator available for this dataset."

    def get_name_from_key(self, ST_key):
        """
        Retrieve the name associated with a dataset key.
        """
        return self.key_name_mapping.get(ST_key, "Unknown Key")

    def get_key_from_name(self, name):
        """
        Retrieve the key associated with a dataset name.
        """
        reverse_mapping = {v: k for k, v in self.key_name_mapping.items()}
        return reverse_mapping.get(name, None)