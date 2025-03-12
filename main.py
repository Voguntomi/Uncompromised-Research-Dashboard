# main.py
from data_retrieval import DataRetrieval
from data_manipulation import DataManipulation
from data_visualization import DataVisualization


class ECBDataProcessor:
    def __init__(self, pickle_file_path):
        """Initialize the data retrieval, manipulation, and visualization classes."""
        self.data_retrieval = DataRetrieval(pickle_file_path)  # ✅ Pass the file path
        self.data_manipulation = None
        self.data_visualization = None

    def process(self, ST_key):
        """Process data for a given ST_key."""
        print(f"\n🔄 Processing data for key: {ST_key}")

        # Step 1: Fetch data
        print(f"🌍 Fetching data for key: {ST_key}")
        self.data_retrieval.fetch_data(ST_key)

        # Ensure data retrieval was successful
        if ST_key not in self.data_retrieval.raw_data:
            print(f"❌ No data retrieved for key {ST_key}. Skipping processing.")
            return

        # Step 2: Perform data manipulation (EDA)
        print(f"🔍 Performing data manipulation for key: {ST_key}")
        self.data_manipulation = DataManipulation(self.data_retrieval.raw_data)

        # Check for missing values
        self.data_manipulation.missing_values(ST_key)

        # Generate summary statistics
        self.data_manipulation.summary_statistics(ST_key)

        # Detect outliers using Z-score method
        self.data_manipulation.outlier_detection(ST_key, method='zscore', threshold=3)

        # Perform Year and Quarter Extraction
        self.data_manipulation.extract_year_quarter(ST_key)

        # Calculate percentage change in OBS_VALUE
        self.data_manipulation.calculate_pct_change(ST_key)

        # Calculate cumulative sum of OBS_VALUE
        self.data_manipulation.calculate_cum_sum(ST_key)

        # Convert Seasonal Adjustment (Y/N) into text (Adj/Not Adj)
        self.data_manipulation.seasonal_adj_desc(ST_key)

        # Map Observation Status to descriptive labels (e.g., 'A' to 'Acc')
        self.data_manipulation.obs_stat_desc(ST_key)

        # Group INDICATOR into broader categories
        self.data_manipulation.indicator_grouping(ST_key)

        # Step 3: Initialize Visualization
        print(f"📊 Initializing data visualization for key: {ST_key}")
        self.data_visualization = DataVisualization(self.data_retrieval.raw_data)

        # Additional visualization steps can be added here
        print(f"✅ Processing completed for key: {ST_key}")


# Example usage:
if __name__ == "__main__":
    # Define the path to the Pickle file
    pickle_file_path = "data_for_ecb.pkl"  # ✅ Make sure this file exists!

    # List of keys to be processed
    ST_keys = [
        'LCI.Q.I9.Y.LCI_O.BTN',   # Key 1
        'LCI.Q.I9.W.LCI_WAG.BTN', # Key 2
        'MNA.Q.Y.I9.W2.S1.S1.D.D11._Z.BTF._Z.XDC.V.N'  # Key 3
    ]

    # Initialize the processor class with the correct Pickle file path
    processor = ECBDataProcessor(pickle_file_path)

    # Loop through all keys and process them
    for key in ST_keys:
        processor.process(key)
