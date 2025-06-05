import streamlit as st
import pandas as pd
from pathlib import Path
from eurostat_analysis import (
    fetch_data, prepare_data, compute_month_over_month,
    compute_percentiles, calculate_monthly_medians, plot_data
)

def run_eurostat_dashboard():
    # ------------------ Compact Title ------------------
    st.markdown(
        "<h6 style='text-align: center; font-size: 16px;'>📈 Eurostat Inflation Percentiles Dashboard</h6>",
        unsafe_allow_html=True
    )

    # ------------------ Configuration ------------------
    dataset_code = "prc_hicp_midx"
    available_geos = ['EA', 'DE', 'FR', 'IT', 'ES', 'NL']
    coicop_options = [
        'CP00', 'CP01', 'CP02', 'CP03', 'CP04', 'CP05', 'CP06',
        'CP07', 'CP08', 'CP09', 'CP10', 'CP11', 'CP12',
        'NRG', 'TOT_X_NRG', 'TOT_X_NRG_FOOD'
    ]

    # ------------------ Sidebar ------------------
    start_year = st.sidebar.slider("Start Year for Plotting", 2000, 2024, 2021)
    moving_avg_period = st.sidebar.slider("Moving Avg. Period (months)", 1, 24, 6)
    selected_geos = st.sidebar.multiselect("Select Countries", available_geos, default=available_geos)

    select_all = st.sidebar.checkbox("Select all COICOP categories", value=True)
    if select_all:
        selected_coicop = coicop_options
    else:
        selected_coicop = st.sidebar.multiselect(
            "Select COICOP Categories",
            options=coicop_options,
            default=['CP00', 'CP01', 'CP07', 'CP04']
        )

    filters = {
        'unit': 'I15',
        'coicop': selected_coicop,
        'geo': selected_geos
    }

    # ------------------ Data Loading ------------------
    @st.cache_data(show_spinner=True)
    def load_processed_data(dataset_code, filters):
        raw = fetch_data(dataset_code, filters)
        prepared = prepare_data(raw)
        mom = compute_month_over_month(prepared)
        percentiles = compute_percentiles(mom)
        medians = calculate_monthly_medians(mom)
        return percentiles, medians

    percentiles, medians = load_processed_data(dataset_code, filters)

    # ------------------ Tabs ------------------
    tab1, tab2, tab3 = st.tabs([
        "📊 Percentile Charts",
        "📈 Moving Averages",
        "🧾 Medians Table"
    ])

    with tab1:
        st.markdown(
            "<h6 style='text-align: center; font-size: 15px;'>Monthly Inflation Percentile Charts</h6>",
            unsafe_allow_html=True
        )
        for key in percentiles:
            coicop_code = key.replace("d_", "")
            if coicop_code not in selected_coicop:
                continue
            df = percentiles[key]
            plot_data({key: df}, start_year, selected_geos, moving_avg_period=0)

    with tab2:
        st.markdown(
            f"<h6 style='text-align: center; font-size: 15px;'>{moving_avg_period}-Month Moving Averages</h6>",
            unsafe_allow_html=True
        )
        for key in percentiles:
            coicop_code = key.replace("d_", "")
            if coicop_code not in selected_coicop:
                continue
            df = percentiles[key]
            plot_data({key: df}, start_year, selected_geos, moving_avg_period)

    with tab3:
        st.subheader("Median Month-over-Month Inflation by Country and Category")

        filtered_medians = medians.loc[
            medians.index.get_level_values("coicop").isin([f'd_{c}' for c in selected_coicop])
        ]
        st.dataframe(filtered_medians)

        excel_path = Path.home() / "Documents" / "ECB_inflation_percentiles" / "monthly_medians.xlsx"
        filtered_medians.to_excel(excel_path)
        with open(excel_path, "rb") as f:
            st.download_button(
                label="📥 Download as Excel",
                data=f.read(),
                file_name="monthly_medians.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
