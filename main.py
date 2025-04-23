from data_retrieval import DataRetrieval
from data_manipulation import DataManipulation
from data_visualization import DataVisualization


class ECBDataProcessor:
    def __init__(self, pickle_file_path):
        self.data_retrieval = DataRetrieval(pickle_file_path)
        self.data_manipulation = None
        self.data_visualization = None

    def process(self, ST_key):
        print(f"\n🔄 Processing data for key: {ST_key}")
        self.data_retrieval.fetch_data(ST_key)

        if ST_key not in self.data_retrieval.raw_data:
            print(f"❌ No data retrieved for key {ST_key}. Skipping processing.")
            return

        print(f"🔍 Performing data manipulation for key: {ST_key}")
        self.data_manipulation = DataManipulation(self.data_retrieval.raw_data)

        self.data_manipulation.missing_values(ST_key)
        self.data_manipulation.summary_statistics(ST_key)
        self.data_manipulation.outlier_detection(ST_key, method='zscore', threshold=3)
        self.data_manipulation.extract_year_quarter(ST_key)
        self.data_manipulation.calculate_pct_change(ST_key)
        self.data_manipulation.calculate_cum_sum(ST_key)
        self.data_manipulation.seasonal_adj_desc(ST_key)
        self.data_manipulation.obs_stat_desc(ST_key)
        self.data_manipulation.indicator_grouping(ST_key)

        print(f"📊 Initializing data visualization for key: {ST_key}")
        self.data_visualization = DataVisualization(self.data_retrieval.raw_data)

        print(f"✅ Processing completed for key: {ST_key}")


if __name__ == "__main__":
    pickle_file_path = "ecb_dashboard_data.pkl"  # Updated path
    ST_keys = ['Sheet1', 'Sheet2']  # Replace with actual sheet names from your Excel file

    processor = ECBDataProcessor(pickle_file_path)
    for key in ST_keys:
        processor.process(key)
