import streamlit as st
from data_retrieval import DataRetrieval
from data_visualization import DataVisualization

# Load data
data_retriever = DataRetrieval("ecb_dashboard_data.pkl")
df_dict = data_retriever.DICT_data

# Set up page layout
st.set_page_config(page_title="Uncompromised Research Dashboard", layout="wide")
st.markdown("""
    <div style='margin-top: -60px;'>
        <h1 style='text-align: center;'>📊 Uncompromised Research Dashboard</h1>
    </div>
""", unsafe_allow_html=True)

if not df_dict:
    st.error("❌ No data loaded from the pickle file.")
else:
    # Map cleaned label (without key) to full key
    label_to_key = {}
    for full_key in df_dict:
        clean_label = full_key.split('[')[0].strip()
        counter = 2
        original_label = clean_label
        while clean_label in label_to_key:
            clean_label = f"{original_label} ({counter})"
            counter += 1
        label_to_key[clean_label] = full_key

    display_labels = list(label_to_key.keys())

    if not display_labels:
        st.warning("⚠️ No valid datasets available.")
    else:
        selected_label = st.selectbox("Select Dataset:", display_labels)
        compare_label = st.selectbox("Compare with Additional Datasets:", ["None"] + display_labels)

        selected_key = label_to_key.get(selected_label)
        compare_key = label_to_key.get(compare_label) if compare_label != "None" else None

        view_option = st.radio("View Option:", ["Original Data", "Period-on-Period", "Interannual"])
        sub_option = None
        if view_option in ["Period-on-Period", "Interannual"]:
            sub_option = st.selectbox("Sub Option:", ["Difference", "Rate of Change"])

        st.date_input("Select Time Range:", [])

        # Prepare data for visualization
        combined_data = []
        if selected_key in df_dict:
            combined_data.append((selected_key, df_dict[selected_key]))
        if compare_key and compare_key in df_dict:
            combined_data.append((compare_key, df_dict[compare_key]))

        if combined_data:
            visualizer = DataVisualization(df_dict)
            fig, table_data, _, _ = visualizer.compare_datasets_chart(
                combined_data=combined_data,
                view_option=view_option,
                chart_title=selected_label,
                sub_option=sub_option
            )

            # Tabs for Chart / Table / Description / Summary Stats
            tab1, tab2, tab3, tab4 = st.tabs(["📈 Chart", "📊 Table", "📄 Description", "📊 Summary Stats"])

            with tab1:
                st.plotly_chart(fig, use_container_width=True)

            with tab2:
                for label, df, orig_key, full_df, stats_df in table_data:
                    calc_col = "OBS_VALUE"
                    table_title = f"{label}"

                    if view_option in ["Period-on-Period", "Interannual"]:
                        df = df[["TIME_PERIOD", calc_col]].dropna()
                        df.columns = ["Date", table_title]
                    else:
                        df = df.dropna(subset=["OBS_VALUE"])

                    st.subheader(f"Data Table - {table_title}")
                    st.dataframe(df)

                    csv = df.to_csv(index=False).encode("utf-8")
                    st.download_button(f"Download {label}", data=csv, file_name=f"{label}.csv", mime="text/csv")

            with tab3:
                st.markdown("📝 Metadata and dataset description coming soon...")

            with tab4:
                for label, df, orig_key, full_df, stats_df in table_data:
                    st.subheader(f"Summary Statistics - {label}")
                    st.dataframe(stats_df)
        else:
            st.info("ℹ️ Please select datasets that contain valid data.")
