import streamlit as st
import pandas as pd
from data import DataRetrieval
from data_manipulation import DataManipulation
from data_visualization import DataVisualization


# Set page config at the top of the script (must be the first command)
st.set_page_config(page_title="Uncompromised Research Dashboard", layout="wide")


class Dashboard:
    def __init__(self, pickle_file_path):
        """
        Initialize the Dashboard class with a Pickle file.
        """
        # Initialize DataRetrieval using the Pickle file
        self.data_retrieval = DataRetrieval(pickle_file_path=pickle_file_path)
        self.df = self.data_retrieval.raw_data  # Get the loaded data
        self.df = self.process_data(self.df)  # Process the data (e.g., handle missing values)
        self.visualization = DataVisualization(self.df)  # Initialize visualization

    def process_data(self, df):
        """Process the data (e.g., handle missing values)."""
        if df.isnull().any().any():
            df = df.fillna(method="ffill")  # Forward fill missing values
        return df

    def auto_detect_frequency(self, df):
        """Detect the dataset's frequency based on time gaps."""
        if "TIME_PERIOD" in df.columns:
            df["TIME_PERIOD"] = pd.to_datetime(df["TIME_PERIOD"])
            time_diff = df["TIME_PERIOD"].diff().mode()[0]
            if time_diff.days in [90, 91, 92]:  # Quarterly
                return "quarterly"
            elif time_diff.days in [30, 31]:  # Monthly
                return "monthly"
        return None

    def run(self):
        # Set the title and header of the dashboard
        st.markdown("<h1 style='text-align: center;'>📊 Uncompromised Research Dashboard</h1>", unsafe_allow_html=True)

        # Select dataset
        dataset_names = [name for name in self.df['Name'].unique()]
        selected_name = st.sidebar.selectbox("Select Dataset:", options=dataset_names, key="single_selection")

        view_option = st.sidebar.radio("View Option:", ["Original Data", "Period-on-Period", "Interannual"], key="view_option")

        # Multi-year quarter comparison
        compare_quarters = st.sidebar.checkbox("Compare Specific Quarters Across Years")

        if selected_name:
            # Filter the data based on the selected dataset
            selected_data = self.df[self.df['Name'] == selected_name]

            if selected_data.empty:
                st.error(f"No data found for the selected dataset: {selected_name}")
                return

            frequency = self.auto_detect_frequency(selected_data)

            if "TIME_PERIOD" in selected_data.columns:
                selected_data["TIME_PERIOD"] = pd.to_datetime(selected_data["TIME_PERIOD"])
                min_date, max_date = selected_data["TIME_PERIOD"].min(), selected_data["TIME_PERIOD"].max()

                start_date = st.sidebar.date_input("Start Date", min_date, key="start_date")
                end_date = st.sidebar.date_input("End Date", max_date, key="end_date")

                filtered_data = selected_data[(selected_data["TIME_PERIOD"] >= pd.to_datetime(start_date)) &
                                              (selected_data["TIME_PERIOD"] <= pd.to_datetime(end_date))]

                if filtered_data.empty:
                    st.warning("No data found for the selected date range.")
                    return

            else:
                st.error("The dataset does not contain the 'TIME_PERIOD' column.")
                return

            # View Options
            if view_option == "Original Data":
                chart = self.visualization.line_chart(filtered_data, y_column="OBS_VALUE", title=f"Original Data for {selected_name}")
                st.plotly_chart(chart)
                st.dataframe(filtered_data)

            elif view_option == "Period-on-Period":
                filtered_data["Variance"] = filtered_data["OBS_VALUE"].pct_change(periods=1) * 100
                chart = self.visualization.period_on_period_chart(filtered_data, title=f"Period-on-Period Change for {selected_name}")
                st.plotly_chart(chart)
                st.dataframe(filtered_data)

            elif view_option == "Interannual":
                filtered_data["Year"] = filtered_data["TIME_PERIOD"].dt.year
                chart = self.visualization.interannual_chart(filtered_data, title=f"Interannual Change for {selected_name}")
                st.plotly_chart(chart)
                st.dataframe(filtered_data)

            # Quarter comparison option
            if compare_quarters:
                selected_quarters = st.sidebar.multiselect("Select Quarters:", ["Q1", "Q2", "Q3", "Q4"], key="quarter_selection")
                if selected_quarters:
                    quarter_chart = self.visualization.quarterly_comparison_chart(filtered_data, selected_quarters)
                    st.plotly_chart(quarter_chart)


# Main execution
if __name__ == "__main__":
    st.write("🚀 App started!")

    # Provide the path to the Pickle file
    pickle_file_path = r"data_for_ecb.pkl"  # Path to your Pickle file

    # Initialize and run the dashboard
    dashboard = Dashboard(pickle_file_path=pickle_file_path)  # Use the pickle file
    dashboard.run()
