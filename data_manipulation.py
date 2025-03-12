import numpy as np
import pandas as pd
from scipy import stats

class DataManipulation:
    # Class for performing data manipulation tasks on datasets.

    def __init__(self, data_dict):
        # Initialize with a dictionary containing dataset keys and their data.
        self.data_dict = data_dict

    def clean_dataset(self, data_df):
        # Clean the dataset by removing rows with missing 'Name' or 'Key'.
        if "Name" in data_df.columns and "Key" in data_df.columns:
            return data_df.dropna(subset=["Name", "Key"])
        else:
            raise ValueError("The dataset must contain 'Name' and 'Key' columns for cleaning.")

    def filter_by_date_range(self, st_key, start_date, end_date):
        # Filter the dataset for a specific date range.
        if st_key not in self.data_dict:
            print(f"No data found for key: {st_key}. Please fetch data first.")
            return None

        df_data = pd.DataFrame(self.data_dict[st_key])

        if "TIME_PERIOD" not in df_data.columns:
            print(f"'TIME_PERIOD' column not found in data for {st_key}. Skipping date filtering.")
            return df_data

        # Ensure the TIME_PERIOD column is in datetime format
        df_data["TIME_PERIOD"] = pd.to_datetime(df_data["TIME_PERIOD"], errors="coerce")

        # Filter data based on the date range
        filtered_data = df_data[(df_data["TIME_PERIOD"] >= pd.to_datetime(start_date)) &
                                 (df_data["TIME_PERIOD"] <= pd.to_datetime(end_date))]

        print(f"Filtered data for key '{st_key}' from {start_date} to {end_date}:")
        print(filtered_data.head())
        return filtered_data

    def missing_values(self, st_key):
        # Check for missing values in the dataset.
        if st_key not in self.data_dict:
            print(f"No data found for key: {st_key}. Please fetch data first.")
            return

        df_data = pd.DataFrame(self.data_dict[st_key])
        missing_values = df_data.isnull().sum()

        if missing_values.any():
            print(f"Missing values for each column in data for {st_key}:")
            print(missing_values)
        else:
            print(f"No missing values found for {st_key}.")

    def summary_statistics(self, st_key):
        # Generate summary statistics for the dataset.
        if st_key not in self.data_dict:
            print(f"No data found for key: {st_key}. Please fetch data first.")
            return

        df_data = pd.DataFrame(self.data_dict[st_key])
        print(f"Summary Statistics for {st_key}:")
        print(df_data.describe(include="all"))

    def clean_data(self, st_key, method="drop", fill_value=None):
        # Handle missing values in the dataset.
        if st_key not in self.data_dict:
            print(f"No data found for key: {st_key}. Please fetch data first.")
            return

        df_data = pd.DataFrame(self.data_dict[st_key])

        if method == "drop":
            return df_data.dropna()
        elif method == "fill" and fill_value is not None:
            return df_data.fillna(fill_value)
        else:
            print(f"Invalid method or fill_value. Use 'drop' or 'fill' with a valid value.")
            return

    def remove_duplicates(self, st_key):
        # Remove duplicate rows from the dataset.
        if st_key not in self.data_dict:
            print(f"No data found for key: {st_key}. Please fetch data first.")
            return

        df_data = pd.DataFrame(self.data_dict[st_key])
        return df_data.drop_duplicates()

    def outlier_detection(self, st_key, method="zscore", threshold=3):
        # Detect outliers using either Z-score or IQR method.
        if st_key not in self.data_dict:
            raise KeyError(f"No data found for key: {st_key}. Please fetch data first.")

        df_data = pd.DataFrame(self.data_dict[st_key])

        if method == "zscore":
            z_scores = np.abs(stats.zscore(df_data.select_dtypes(include=[np.number])))
            outliers = (z_scores > threshold).sum(axis=0)
            print(f"Outliers detected using Z-score (threshold={threshold}):")
            print(outliers)
        elif method == "iqr":
            Q1 = df_data.quantile(0.25)
            Q3 = df_data.quantile(0.75)
            IQR = Q3 - Q1
            outliers = ((df_data < (Q1 - 1.5 * IQR)) | (df_data > (Q3 + 1.5 * IQR))).sum(axis=0)
            print("Outliers detected using IQR:")
            print(outliers)
        else:
            print("Invalid method. Use 'zscore' or 'iqr'.")

    def extract_year_quarter(self, st_key):
        # Extract year and quarter from TIME_PERIOD.
        if st_key not in self.data_dict:
            print(f"No data found for key: {st_key}. Please fetch data first.")
            return

        df_data = pd.DataFrame(self.data_dict[st_key])
        df_data["TIME_PERIOD"] = pd.to_datetime(df_data["TIME_PERIOD"], errors="coerce")
        df_data["ST_year_qtr"] = df_data["TIME_PERIOD"].dt.to_period("Q")
        print(f"Year and Quarter extraction for {st_key}:")
        print(df_data[["TIME_PERIOD", "ST_year_qtr"]])

    def calculate_pct_change(self, st_key):
        # Calculate percentage change of OBS_VALUE over time.
        if st_key not in self.data_dict:
            print(f"No data found for key: {st_key}. Please fetch data first.")
            return

        df_data = pd.DataFrame(self.data_dict[st_key])
        df_data["ST_pct_chg"] = df_data["OBS_VALUE"].pct_change() * 100
        print(f"Percentage Change calculation for {st_key}:")
        print(df_data[["OBS_VALUE", "ST_pct_chg"]])

    def calculate_cum_sum(self, st_key):
        # Calculate cumulative sum of OBS_VALUE.
        if st_key not in self.data_dict:
            print(f"No data found for key: {st_key}. Please fetch data first.")
            return

        df_data = pd.DataFrame(self.data_dict[st_key])
        df_data["ST_cum_sum"] = df_data["OBS_VALUE"].cumsum()
        print(f"Cumulative Sum calculation for {st_key}:")
        print(df_data[["OBS_VALUE", "ST_cum_sum"]])

    def rolling_average(self, st_key, window=5):
        # Calculate the rolling average of OBS_VALUE.
        if st_key not in self.data_dict:
            print(f"No data found for key: {st_key}. Please fetch data first.")
            return

        df_data = pd.DataFrame(self.data_dict[st_key])
        if "OBS_VALUE" in df_data.columns:
            df_data["ST_roll_avg"] = df_data["OBS_VALUE"].rolling(window=window).mean()
            print(f"Rolling Average for {st_key}:")
            print(df_data[["OBS_VALUE", "ST_roll_avg"]])
        else:
            print(f"Column 'OBS_VALUE' not found for {st_key}. Skipping calculation.")

    def seasonal_adj_desc(self, st_key):
        """Convert SEASONAL_ADJUST values into descriptive text (e.g., 'Y' to 'Adjusted', 'N' to 'Not Adjusted')."""
        if st_key not in self.data_dict:
            print(f"No data found for key: {st_key}. Please fetch data first.")
            return

        df_data = pd.DataFrame(self.data_dict[st_key])
        if 'SEASONAL_ADJUST' in df_data.columns:
            # Map 'Y' to 'Adjusted' and 'N' to 'Not Adjusted'
            df_data['SEASONAL_ADJUST_DESC'] = df_data['SEASONAL_ADJUST'].map({'Y': 'Adjusted', 'N': 'Not Adjusted'})
            print(f"Seasonal Adjustment Description added for {st_key}:")
            print(df_data[['SEASONAL_ADJUST', 'SEASONAL_ADJUST_DESC']].head())
        else:
            print(f"'SEASONAL_ADJUST' column not found in data for {st_key}. Skipping seasonal adjustment description.")

    def obs_stat_desc(self, st_key):
        """
        Map observation status codes to descriptive text.
        """
        if st_key not in self.data_dict:
            print(f"No data found for key: {st_key}. Please fetch data first.")
            return

        df_data = pd.DataFrame(self.data_dict[st_key])
        if 'OBS_STATUS' in df_data.columns:
            # Define a mapping dictionary for observation status codes
            obs_status_mapping = {
                'A': 'Normal value',
                'E': 'Estimated value',
                'F': 'Forecasted value',
                'P': 'Provisional value',
                'N': 'Not significant',
                # Add more mappings as needed
            }
            # Map the 'OBS_STATUS' codes to their descriptions
            df_data['OBS_STATUS_DESC'] = df_data['OBS_STATUS'].map(obs_status_mapping)
            print(f"Observation Status Description added for {st_key}:")
            print(df_data[['OBS_STATUS', 'OBS_STATUS_DESC']].head())
        else:
            print(f"'OBS_STATUS' column not found in data for {st_key}. Skipping observation status description.")

    def indicator_grouping(self, st_key, indicator_column='default_column'):
        """
        Group the dataset by a specified indicator and compute summary statistics for each group.

        Parameters:
        - st_key: str
            The key identifying the dataset within data_dict.
        - indicator_column: str
            The column name to group by in the dataset.

        Returns:
        - grouped_stats: DataFrame
            A DataFrame containing summary statistics for each group.
        """
        if st_key not in self.data_dict:
            print(f"No data found for key: {st_key}. Please fetch data first.")
            return None

        df_data = pd.DataFrame(self.data_dict[st_key])

        if indicator_column not in df_data.columns:
            print(f"'{indicator_column}' column not found in data for {st_key}.")
            return None

        # Group by the specified indicator column
        grouped = df_data.groupby(indicator_column)

        # Compute summary statistics for each group
        grouped_stats = grouped.describe()

        print(f"Summary statistics for each group in '{indicator_column}' for {st_key}:")
        print(grouped_stats)

        return grouped_stats
