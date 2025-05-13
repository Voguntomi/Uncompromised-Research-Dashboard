import streamlit as st
import pandas as pd
from data_retrieval import DataRetrieval
from data_visualization import DataVisualization

class Dashboard:
    def __init__(self, pickle_file_path):
        self.data_retrieval = DataRetrieval(pickle_file_path)
        self.raw_df = self.data_retrieval.raw_data
        self.visualization = DataVisualization(self.data_retrieval.DICT_data)
        self.table_data = []

        self.series_name_map = {}
        self.series_key_map = {}
        self.title_compl_map = {}

        self.build_series_name_map()

    def build_series_name_map(self):
        total_keys = list(self.raw_df["KEY"].dropna().unique())
        title_to_details = {}

        for key in total_keys:
            try:
                self.data_retrieval.fetch_data(key)
                df = self.data_retrieval.DICT_data.get(key)
                if isinstance(df, pd.DataFrame) and not df.empty:
                    title = self.get_title_from_data(df).strip()
                    title_compl = self.get_title_compl(df).strip() if self.get_title_compl(df) else ""

                    if title not in title_to_details:
                        title_to_details[title] = []
                    title_to_details[title].append((key, title_compl))
            except Exception:
                continue

        for title, entries in title_to_details.items():
            if len(entries) == 1:
                key, _ = entries[0]
                self.series_name_map[title] = key
                self.series_key_map[key] = title
                self.title_compl_map[key] = self.get_title_compl(self.data_retrieval.DICT_data[key])
            else:
                for key, compl in entries:
                    difference = compl.replace(title, "").strip(" -–:()")
                    label = f"{title} ({difference})" if difference else f"{title}"
                    self.series_name_map[label] = key
                    self.series_key_map[key] = label
                    self.title_compl_map[key] = compl

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

    def run(self):
        st.set_page_config(page_title="Uncompromised Research Dashboard", layout="wide")
        st.markdown("<div style='text-align: center; font-size: 18px;'>📊 <strong>Uncompromised Research Dashboard</strong></div>", unsafe_allow_html=True)

        dataset_names = list(self.series_name_map.keys())
        selected_name = st.sidebar.selectbox("Select Dataset", dataset_names)
        selected_key = self.series_name_map[selected_name]

        full_title = self.title_compl_map.get(selected_key)
        if full_title:
            if "(" in full_title:
                main_title, bracketed = full_title.split("(", 1)
                bracketed = bracketed.rstrip(")")
                formatted = f"<b>{main_title.strip()}</b><br><span style='font-size:11px; font-weight:normal;'>({bracketed.strip()})</span>"
            else:
                formatted = f"<b>{full_title}</b>"
            st.sidebar.markdown(formatted, unsafe_allow_html=True)

        selected_comparisons = st.sidebar.multiselect("Compare with:", dataset_names)

        # ✅ Get date range from dataset
        base_df = self.data_retrieval.DICT_data[selected_key]
        base_df["TIME_PERIOD"] = pd.to_datetime(base_df["TIME_PERIOD"])
        min_date = base_df["TIME_PERIOD"].min()
        max_date = base_df["TIME_PERIOD"].max()

        time_range = st.sidebar.date_input(
            "Select Time Range",
            value=[min_date, max_date],
            min_value=min_date,
            max_value=max_date
        )

        view_option = st.sidebar.radio("View Option", ["Original Data", "Period-on-Period", "Interannual"])
        sub_option = None
        if view_option != "Original Data":
            sub_option = st.sidebar.selectbox("Sub Option", ["Difference", "Rate of Change"])

        freq = self.visualization.infer_frequency(base_df)
        chart_types = ["Line", "Bar", "Scatter", "Area"]
        chart_type = st.sidebar.selectbox("Chart Type", chart_types)

        def filter_df(df):
            df = df.copy()
            df["TIME_PERIOD"] = pd.to_datetime(df["TIME_PERIOD"])
            if time_range and isinstance(time_range, list) and len(time_range) == 2:
                df = df[(df["TIME_PERIOD"] >= pd.to_datetime(time_range[0])) & (df["TIME_PERIOD"] <= pd.to_datetime(time_range[1]))]
            return df

        combined_data = []
        selected_df = self.data_retrieval.DICT_data[selected_key]
        combined_data.append((selected_name, filter_df(selected_df)))

        for name in selected_comparisons:
            key = self.series_name_map[name]
            df = self.data_retrieval.DICT_data[key]
            combined_data.append((name, filter_df(df)))

        main_title = selected_name.split(" (")[0].strip()
        full_title = self.title_compl_map.get(selected_key, "")
        if full_title and full_title.startswith(main_title):
            extra_info = full_title.replace(main_title, "").strip(" -–:()")
        else:
            extra_info = full_title.strip()
        chart_title = f"<b>{main_title}</b><br><span style='font-size:11px; font-weight:normal;'>{extra_info}</span>" if extra_info else f"<b>{main_title}</b>"

        if combined_data:
            chart, table_data, color_map, axis_map = self.visualization.compare_datasets_chart(
                combined_data=combined_data,
                view_option=view_option,
                chart_title=chart_title,
                sub_option=sub_option,
                y_axis_label=None,
                x_axis_label="Date",
                chart_height=500,
                chart_type=chart_type.lower()
            )
            self.table_data = table_data

            tab1, tab2, tab3, tab4 = st.tabs(["📈 Chart", "📋 Table", "ⓘ Description", "📊 Summary Stats"])
            with tab1:
                st.plotly_chart(chart, use_container_width=True)
            with tab2:
                for label, df, _, _, _ in self.table_data:
                    st.markdown(f"**{label}**")
                    st.dataframe(df, use_container_width=True)
                    st.markdown("---")
            with tab3:
                for _, _, dataset_name, raw_df, _ in self.table_data:
                    st.markdown(f"**{dataset_name}**")
                    st.markdown(self.visualization.describe_metadata_markdown(raw_df))
                    st.markdown("---")
            with tab4:
                for label, _, _, _, stats_df in self.table_data:
                    st.markdown(f"**{label}**")
                    st.dataframe(stats_df, use_container_width=True)
                    st.markdown("---")
        else:
            st.warning("No valid data selected.")

if __name__ == "__main__":
    dashboard = Dashboard("ecb_dashboard_data.pkl")
    dashboard.run()
