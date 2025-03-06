import pandas as pd
from ecbdata import ecbdata
import requests
import pandas as pd
import io


class DataRetrieval:
    def __init__(self, excel_file_url):
        self.excel_file_url = excel_file_url
        self.raw_data = self.load_raw_data()
        self.DICT_data = self.create_dict_data()  # Create DICT_data as a dictionary

    def load_raw_data(self):
        # Download the Excel file from the GitHub URL
        response = requests.get(self.excel_file_url)

        # Check if the request was successful
        if response.status_code == 200:
            # Use io.BytesIO to treat the downloaded content as a file-like object
            excel_data = io.BytesIO(response.content)

            # Read the Excel data into a pandas DataFrame
            return pd.read_excel(excel_data, sheet_name="Sheet1", header=0)
        else:
            # If the request fails, raise an error
            raise FileNotFoundError(f"Failed to download the file from {self.excel_file_url}")

    def create_dict_data(self):
        # Print the columns and first few rows to inspect the data
        print("Columns in DataFrame:", self.raw_data.columns)
        print("First few rows of the data:", self.raw_data.head())  # To inspect the data

        # Use 'Key' as the column to set as the index
        return self.raw_data.set_index('Key').T.to_dict('dict')
        # Replace 'YourActualColumnName' with the correct column name
        return self.raw_data.set_index('YourActualColumnName').T.to_dict('dict')

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