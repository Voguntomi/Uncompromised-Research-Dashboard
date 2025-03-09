# save_excel_to_pickle.py

import pandas as pd

# Load the Excel file
excel_file_path = r"C:\Users\vogun\PycharmProjects\UR Dashboard\data\DATA_FOR_ECB.xlsx"
df = pd.read_excel(excel_file_path)

# Save the dataframe as a pickle file
df.to_pickle('data_for_ecb.pkl')
print("Data saved as pickle file.")

# data_processing.py

import pandas as pd

# Load the pickled data
def load_data_from_pickle(pickle_file_path):
    try:
        # Load the pickle file into a pandas DataFrame
        df = pd.read_pickle(pickle_file_path)
        print("Columns in the DataFrame:", df.columns)
        print("First few rows of the data:", df.head())
        return df
    except Exception as e:
        print(f"Error loading pickled data: {e}")
        return None


# Process the data (this is just an example)
def process_data(df):
    if df is not None:
        print("Missing values in the data:", df.isnull().sum())

        # Avoid inplace=True and explicitly assign the filled column back to the DataFrame
        df['Name'] = df['Name'].fillna('Unknown')

        print("Updated data:")
        print(df.head())
    return df


# Auto-detect frequency (Quarterly or Monthly) based on TIME_PERIOD column
def auto_detect_frequency(df):
    """Detect the dataset's frequency based on time gaps."""
    if "TIME_PERIOD" in df.columns:
        df["TIME_PERIOD"] = pd.to_datetime(df["TIME_PERIOD"])
        time_diff = df["TIME_PERIOD"].diff().mode()[0]
        if time_diff.days in [90, 91, 92]:  # Quarterly
            return "quarterly"
        elif time_diff.days in [30, 31]:  # Monthly
            return "monthly"
    return None
