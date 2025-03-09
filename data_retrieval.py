import pandas as pd


class DataRetrieval:
    def __init__(self, excel_file_path):
        self.excel_file_path = excel_file_path
        self.raw_data = self.load_raw_data()  # Load raw data on initialization
        self.DICT_data = {}
        self.key_name_mapping = {}

    def load_raw_data(self):
        """ Load data from the Excel file """
        try:
            # Read the Excel file
            raw_data = pd.read_excel(self.excel_file_path)

            # Check if the dataframe is empty
            if raw_data.empty:
                raise ValueError("The loaded data is empty.")

            # Print the first few rows and column names for debugging
            print("Columns in DataFrame:", raw_data.columns)
            print("First few rows of the data:", raw_data.head())

            return raw_data

        except Exception as e:
            raise ValueError(f"Error loading data: {e}")

    def create_key_name_mapping(self, df):
        """ Create key-name mapping by ensuring there are no missing values in 'Key' and 'Name' columns """
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

    def get_key_from_name(self, name):
        """ Fetch the key from name using the key_name_mapping. """
        matching_keys = [key for key, value in self.key_name_mapping.items() if value == name]
        return matching_keys if matching_keys else None

    def fetch_data(self, key):
        """ Fetch the data for a given key from the DICT_data.
        If the data is not found, attempt to load it.
        """
        if key in self.DICT_data:
            return self.DICT_data[key]
        else:
            # Logic to fetch data for the key (you can load from file, API, etc.)
            print(f"Data for key '{key}' not found. Attempting to fetch data...")
            # Placeholder: logic to load data
            # self.DICT_data[key] = some_function_to_fetch_data(key)
            return pd.DataFrame()  # Returning an empty DataFrame as a fallback
