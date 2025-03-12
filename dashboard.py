import streamlit as st
import pandas as pd
from data_retrieval import DataRetrieval
from data_manipulation import DataManipulation
from data_visualization import DataVisualization
import plotly.graph_objects as go
import plotly.express as px


class Dashboard:
    def __init__(self, pickle_file_path):
        self.pickle_file_path = pickle_file_path
        self.data_retrieval = DataRetrieval(pickle_file_path)
        self.df_dict = self.data_retrieval.raw_data
        self.visualization = DataVisualization(self.df_dict)

    def auto_detect_frequency(self, df):
        """Detect the dataset's frequency based on time gaps."""
        if "TIME_PERIOD" in df.columns:
            df["TIME_PERIOD"] = pd.to_datetime(df["TIME_PERIOD"], errors='coerce')
            df.dropna(subset=["TIME_PERIOD"], inplace=True)
            time_diff = df["TIME_PERIOD"].diff().mode()[0]
            if time_diff.days in [90, 91, 92]:
                return "quarterly"
            elif time_diff.days in [30, 31]:
                return "monthly"
        return None

    def run(self):
        st.set_page_config(page_title="Uncompromised Research Dashboard", layout="wide")
        st.markdown("<h1 style='text-align: center;'>📊 Uncompromised Research Dashboard</h1>", unsafe_allow_html=True)

        dataset_names = [name for name in self.data_retrieval.key_name_mapping.values() if name]

        selected_dataset = st.sidebar.selectbox("Select Dataset:", options=dataset_names, key="single_selection")
        selected_datasets = st.sidebar.multiselect("Compare with Additional Datasets:", options=dataset_names,
                                                   key="multi_selection")

        time_range = st.sidebar.date_input("Select Time Range:", [])
        view_option = st.sidebar.radio("View Option:", ["Original Data", "Period-on-Period", "Interannual"],
                                       key="view_option")

        compare_quarters = st.sidebar.checkbox("Compare Specific Quarters Across Years")
        selected_quarters = []
        if compare_quarters:
            selected_quarters = st.sidebar.multiselect("Select Quarters:", options=["Q1", "Q2", "Q3", "Q4"],
                                                       key="quarter_selection")

        combined_data = []

        def filter_data(selected_key, data_df):
            """Filter data based on date range."""
            data_df["TIME_PERIOD"] = pd.to_datetime(data_df["TIME_PERIOD"], errors='coerce')
            data_df.dropna(subset=["TIME_PERIOD"], inplace=True)
            if time_range:
                data_df = data_df[(data_df["TIME_PERIOD"] >= pd.to_datetime(time_range[0])) &
                                  (data_df["TIME_PERIOD"] <= pd.to_datetime(time_range[1]))]
            return data_df

        if selected_dataset:
            selected_key = self.data_retrieval.get_key_from_name(selected_dataset)
            self.data_retrieval.fetch_data(selected_key)
            data_df = self.data_retrieval.DICT_data.get(selected_key, pd.DataFrame())
            if not data_df.empty:
                combined_data.append((selected_dataset, filter_data(selected_key, data_df)))

        for dataset_name in selected_datasets:
            selected_key = self.data_retrieval.get_key_from_name(dataset_name)
            if selected_key not in self.data_retrieval.DICT_data:
                self.data_retrieval.fetch_data(selected_key)
            data_df = self.data_retrieval.DICT_data.get(selected_key, pd.DataFrame())
            if not data_df.empty:
                combined_data.append((dataset_name, filter_data(selected_key, data_df)))

        if combined_data:
            chart_title = selected_dataset if len(combined_data) == 1 else "Comparison of Selected Datasets"
            combined_chart = self.visualization.compare_datasets_chart(combined_data, view_option, chart_title)
            if isinstance(combined_chart, go.Figure):
                st.plotly_chart(combined_chart)
            else:
                st.warning("No valid data available for chart generation.")

            for dataset_name, data_df in combined_data:
                st.markdown(f"### {dataset_name} Data Table")
                st.dataframe(data_df)

            if compare_quarters:
                for dataset_name, data_df in combined_data:
                    quarter_data = data_df.copy()
                    quarter_data['Quarter_Year'] = quarter_data['TIME_PERIOD'].dt.to_period('Q').astype(str)
                    filtered_quarter_data = quarter_data[quarter_data['Quarter_Year'].str[-2:].isin(selected_quarters)]
                    fig = px.bar(filtered_quarter_data, x='Quarter_Year', y='OBS_VALUE', color='Quarter_Year',
                                 title=f"Quarterly Comparison for {dataset_name}")
                    st.plotly_chart(fig)


if __name__ == "__main__":
    data_file_path = "data_for_ecb.pkl"
    dashboard = Dashboard(pickle_file_path=data_file_path)
    dashboard.run()
