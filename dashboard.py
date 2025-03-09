import streamlit as st
import pandas as pd
from data_retrieval import DataRetrieval
from data_visualization import DataVisualization


# Set page config at the top of the script (must be the first command)
st.set_page_config(page_title="Uncompromised Research Dashboard", layout="wide")


class Dashboard:
    def __init__(self, excel_file_path):
        self.data_retrieval = DataRetrieval(excel_file_path)
        self.raw_data = self.data_retrieval.load_raw_data_from_local()
        self.data_retrieval.create_key_name_mapping(self.raw_data)
        self.visualization = DataVisualization(self.data_retrieval.DICT_data)

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
        st.set_page_config(page_title="Uncompromised Research Dashboard", layout="wide")
        st.markdown("<h1 style='text-align: center;'>📊 Uncompromised Research Dashboard</h1>", unsafe_allow_html=True)

        dataset_names = [name for name in self.data_retrieval.key_name_mapping.values() if name]
        selected_name = st.sidebar.selectbox("Select Dataset:", options=dataset_names, key="single_selection")

        view_option = st.sidebar.radio("View Option:", ["Original Data", "Period-on-Period", "Interannual"], key="view_option")

        # Multi-year quarter comparison
        compare_quarters = st.sidebar.checkbox("Compare Specific Quarters Across Years")

        if selected_name:
            selected_key = self.data_retrieval.get_key_from_name(selected_name)
            if selected_key is None:
                st.error(f"No data found for the selected dataset: {selected_name}")
                return

            if isinstance(selected_key, list):
                st.error(f"Multiple keys found for the selected dataset: {selected_name}. Please refine the selection.")
                return

            if selected_key not in self.data_retrieval.DICT_data:
                self.data_retrieval.fetch_data(selected_key)

            data_df = self.data_retrieval.DICT_data.get(selected_key, pd.DataFrame())

            if not data_df.empty:
                frequency = self.auto_detect_frequency(data_df)

                if "TIME_PERIOD" in data_df.columns:
                    data_df["TIME_PERIOD"] = pd.to_datetime(data_df["TIME_PERIOD"])
                    min_date, max_date = data_df["TIME_PERIOD"].min(), data_df["TIME_PERIOD"].max()

                    start_date = st.sidebar.date_input("Start Date", min_date, key="start_date")
                    end_date = st.sidebar.date_input("End Date", max_date, key="end_date")

                    filtered_data = data_df[(data_df["TIME_PERIOD"] >= pd.to_datetime(start_date)) &
                                            (data_df["TIME_PERIOD"] <= pd.to_datetime(end_date))]

                    if filtered_data.empty:
                        st.warning("No data found for the selected date range.")
                        return

                else:
                    st.error("The dataset does not contain the 'TIME_PERIOD' column.")
                    return

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

                if compare_quarters:
                    selected_quarters = st.sidebar.multiselect("Select Quarters:", ["Q1", "Q2", "Q3", "Q4"], key="quarter_selection")
                    if selected_quarters:
                        quarter_chart = self.visualization.quarterly_comparison_chart(filtered_data, selected_quarters)
                        st.plotly_chart(quarter_chart)

if __name__ == "__main__":
    st.write("🚀 App started!")
    # Provide the local file path to the embedded Excel file
    excel_file_path = "data/DATA_FOR_ECB.xlsx"  # Update this to the actual path of the file in your repository
    dashboard = Dashboard(excel_file_path)
    dashboard.run()

