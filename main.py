# main.py
from data_retrieval import DataRetrieval
from data_manipulation import DataManipulation
from data_visualization import DataVisualization

class ECBDataProcessor:
    def __init__(self):
        # Initializing the data retrieval, manipulation, and visualization classess
        self.data_retrieval = DataRetrieval()
        self.data_manipulation = None
        self.data_visualization = None

    def process(self, ST_key):
        """Process data for a given ST_key."""
        print(f"\nProcessing data for key: {ST_key}")

        # Step 1: Fetch data
        print(f"Fetching data for key: {ST_key}")
        self.data_retrieval.fetch_data(ST_key)

        # Step 2: Perform data manipulation (EDA)
        print(f"Performing data manipulation for key: {ST_key}")
        self.data_manipulation = DataManipulation(self.data_retrieval.DICT_data)

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
