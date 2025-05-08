import streamlit as st
import pandas as pd
from data_retrieval import DataRetrieval
from data_visualization import DataVisualization


class Dashboard:
    def __init__(self, pickle_file_path):
        self.data_retrieval = DataRetrieval(pickle_file_path)
        self.raw_df = self.data_retrieval.raw_data
        self.visualization = DataVisualization(self.data_retrieval.DICT_data)

        self.series_name_map = {}  # short title → key
        self.series_key_map = {}   # key → short title
        self.title_compl_map = {}  # key → full TITLE_COMPL
        self.failed_keys = []

        self.build_series_name_map()

    def build_series_name_map(self):
        self.failed_keys = []
        total_keys = list(self.raw_df["KEY"].dropna().unique())

        for key in total_keys:
            try:
                self.data_retrieval.fetch_data(key)
                df = self.data_retrieval.DICT_data.get(key)

                if isinstance(df, pd.DataFrame) and not df.empty:
                    title = self.get_title_from_data(df)
                    title_compl = self.get_title_compl(df)

                    clean_label = title
                    counter = 2
                    while clean_label in self.series_name_map:
                        clean_label = f"{title} ({counter})"
                        counter += 1

                    self.series_name_map[clean_label] = key
                    self.series_key_map[key] = clean_label
                    self.title_compl_map[key] = title_compl
                else:
                    self.failed_keys.append(key)
            except Exception:
                self.failed_keys.append(key)

    def get_title_from_data(self, df):
        for col in ["TITLE", "TITLE_EN", "Series_title"]:
            if col in df.columns:
                val = df[col].dropna().unique()
                if len(val) > 0:
                    return val[0]
        return "Unnamed Series"

    def get_title_compl(self, df):
        if "TITLE_COMPL" in df.columns:
            val = df["TITLE_COMPL"].dropna().unique()
            if len(val) > 0:
                return val[0]
        return None

    def get_unit_from_data(self, df):
        for col in ["UNIT", "UNIT_MEASURE", "UNIT_MULT", "UNIT_DESCR"]:
            if col in df.columns:
                val = df[col].dropna().unique()
                if len(val) > 0:
                    return val[0]
        return None

    def run(self):
        st.set_page_config(page_title="Uncompromised Research Dashboard", layout="wide")
        st.markdown("<h1 style='text-align: center;'>📊 Uncompromised Research Dashboard</h1>", unsafe_allow_html=True)

        dataset_names = list(self.series_name_map.keys())

        selected_name = st.sidebar.selectbox("Select Dataset:", options=dataset_names)
        selected_key = self.series_name_map.get(selected_name)

        # ✅ Show full TITLE_COMPL below the selectbox
        full_title = self.title_compl_map.get(selected_key)
        if full_title:
            st.sidebar.caption(f"ℹ️ **Description**: {full_title}")

        selected_comparisons = st.sidebar.multiselect("Compare with Additional Datasets:", options=dataset_names)
        time_range = st.sidebar.date_input("Select Time Range:", [])
        view_option = st.sidebar.radio("View Option:", ["Original Data", "Period-on-Period", "Interannual"])

        sub_option = None
        if view_option != "Original Data":
            sub_option = st.sidebar.selectbox("Select Sub Option:", ["Difference", "Rate of Change"])

        def filter_data(data_df):
            if "TIME_PERIOD" not in data_df.columns:
                return pd.DataFrame()
            data_df["TIME_PERIOD"] = pd.to_datetime(data_df["TIME_PERIOD"], errors='coerce')
            data_df.dropna(subset=["TIME_PERIOD"], inplace=True)
            if time_range:
                data_df = data_df[
                    (data_df["TIME_PERIOD"] >= pd.to_datetime(time_range[0])) &
                    (data_df["TIME_PERIOD"] <= pd.to_datetime(time_range[1]))
                ]
            return data_df

        combined_data = []
        unit = None
        y_axis_label = "Value"
        x_axis_label = "Date"

        if selected_key:
            df = self.data_retrieval.DICT_data.get(selected_key)
            if isinstance(df, pd.DataFrame) and not df.empty:
                label = selected_name
                unit = self.get_unit_from_data(df)
                combined_data.append((label, filter_data(df)))

        for name in selected_comparisons:
            key = self.series_name_map.get(name)
            if key:
                df = self.data_retrieval.DICT_data.get(key)
                if isinstance(df, pd.DataFrame) and not df.empty:
                    label = name
                    combined_data.append((label, filter_data(df)))

        # ✅ Adjust y-axis label for transformation types
        if view_option in ["Period-on-Period", "Interannual"] and sub_option == "Rate of Change":
            y_axis_label = "Percentage (%)"
        elif view_option == "Original Data" and unit:
            y_axis_label = unit
        elif sub_option == "Difference" and unit:
            y_axis_label = f"Δ {unit}"

        if combined_data:
            chart_title = selected_name
            combined_chart, table_data = self.visualization.compare_datasets_chart(
                combined_data, view_option, chart_title, sub_option,
                y_axis_label=y_axis_label, x_axis_label=x_axis_label
            )
        else:
            st.info("ℹ️ Please select a dataset that contains valid data.")


if __name__ == "__main__":
    data_file_path = "ecb_dashboard_data.pkl"
    dashboard = Dashboard(data_file_path)
    dashboard.run()
