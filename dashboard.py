import streamlit as st
import pandas as pd
from data import DataHandler  # Import the class
from data_visualization import DataVisualization

# Set page config at the top of the script (must be the first command)
st.set_page_config(page_title="Uncompromised Research Dashboard", layout="wide")


class Dashboard:
    def __init__(self, excel_file_path, pickle_file_path):
        # Initialize DataHandler
        self.data_handler = DataHandler(excel_file_path, pickle_file_path)
        self.df = self.data_handler.raw_data  # Load data

        if self.df is None:
            st.error("Failed to load data.")
            return

        self.visualization = DataVisualization(self.df)  # Initialize visualization

    def auto_detect_frequency(self, df):
        """Detect the dataset's frequency based on time gaps."""
        return self.data_handler.auto_detect_frequency()  # Use the method from DataHandler

    def run(self):
        st.markdown("<h1 style='text-align: center;'>📊 Uncompromised Research Dashboard</h1>", unsafe_allow_html=True)

        # Select dataset
        dataset_names = [name for name in self.df['Name'].unique()]
        selected_name = st.sidebar.selectbox("Select Dataset:", options=dataset_names, key="single_selection")

        view_option = st.sidebar.radio("View Option:", ["Original Data", "Period-on-Period", "Interannual"], key="view_option")

        # Multi-year quarter comparison
        compare_quarters = st.sidebar.checkbox("Compare Specific Quarters Across Years")

        if selected_name:
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

    # Define file paths
    excel_path = "data/DATA_FOR_ECB.xlsx"
    pickle_path = "data/DATA_FOR_ECB.pkl"

    dashboard = Dashboard(excel_path, pickle_path)
    dashboard.run()

