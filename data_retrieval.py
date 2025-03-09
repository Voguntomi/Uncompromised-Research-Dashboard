import pandas as pd


class DataRetrieval:
    def __init__(self, excel_file_path):
        self.excel_file_path = excel_file_path
        self.raw_data = self.load_raw_data()
        self.DICT_data = {}
        self.key_name_mapping = {}

    def load_raw_data(self):
        # Load data from the Excel file
        try:
            raw_data = pd.read_excel(self.excel_file_path)
            print("Columns in DataFrame:", raw_data.columns)
            print("First few rows of the data:", raw_data.head())
            return raw_data
        except Exception as e:
            raise ValueError(f"Error loading data: {e}")

    def create_key_name_mapping(self, df):
        """ Create key-name mapping by ensuring there are no missing values. """

        # Inspect missing values in 'Key' and 'Name' columns
        print("Missing values in 'Key' and 'Name' columns before cleaning:")
        print(df[['Key', 'Name']].isna().sum())

        # Replacing missing values in 'Key' and 'Name' columns
        df['Key'].fillna('Unknown', inplace=True)
        df['Name'].fillna('Unknown', inplace=True)

        # Handle possible other forms of missing data (like empty strings or None)
        df['Key'] = df['Key'].replace(['', None], 'Unknown')
        df['Name'] = df['Name'].replace(['', None], 'Unknown')

        # After filling missing values, check again for missing values
        print("Missing values in 'Key' and 'Name' columns after cleaning:")
        print(df[['Key', 'Name']].isna().sum())

        # Check for rows that still have missing values
        missing_rows = df[df[['Key', 'Name']].isna().any(axis=1)]
        if missing_rows.shape[0] > 0:
            print(f"There are still missing values in 'Key' or 'Name' columns after cleaning. Rows:")
            print(missing_rows)
            raise ValueError("There are still missing values in 'Key' or 'Name' columns after cleaning.")

        # Create key-name mapping
        self.key_name_mapping = dict(zip(df['Key'], df['Name']))
        print("Key-Name mapping created successfully.")

    def get_key_from_name(self, name):
        """ Fetch key from name using key_name_mapping. """
        return [key for key, value in self.key_name_mapping.items() if value == name]

    def fetch_data(self, key):
        """ Fetch data for a given key. """
        # Fetch data logic can go here. For example, loading data from an API or file.
        pass

