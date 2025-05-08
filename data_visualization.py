import plotly.graph_objects as go
import pandas as pd
from pandas.tseries.frequencies import to_offset
import streamlit as st


class DataVisualization:
    def __init__(self, df_dict):
        self.df_dict = df_dict

    @staticmethod
    def infer_frequency(df):
        if len(df) < 3:
            return None
        df_sorted = df.sort_values("TIME_PERIOD")
        diffs = pd.Series(df_sorted["TIME_PERIOD"].diff().dropna().values).unique()
        if len(diffs) == 1:
            try:
                return to_offset(diffs[0]).name
            except Exception:
                return None
        return None

    @staticmethod
    def describe_metadata(df, dataset_name):
        lines = [f"**{dataset_name}**"]

        if df is not None and isinstance(df, pd.DataFrame):
            df = df.copy()
            df.dropna(axis=1, how="all", inplace=True)

            def get_unique(colname):
                if colname in df.columns:
                    vals = df[colname].dropna().unique()
                    if len(vals) > 0:
                        return vals[0]
                return "Not available"

            metadata_fields = {
                "Complete Title": get_unique("TITLE_COMPL"),
                "Title (EN)": get_unique("TITLE_EN"),
                "Title (Original)": get_unique("TITLE"),
                "Frequency": get_unique("FREQ"),
                "Reference Area": get_unique("REF_AREA"),
                "Adjustment": get_unique("SEASONAL_ADJUST_DESC") or get_unique("SEASONAL_ADJUST"),
                "Unit of Measure": get_unique("UNIT") or get_unique("UNIT_DESCR"),
                "Source": get_unique("SOURCE") if "SOURCE" in df.columns else None,
                "Observation Status": get_unique("OBS_STATUS_DESC") or get_unique("OBS_STATUS"),
            }

            for label, value in metadata_fields.items():
                if value and value != "Not available":
                    lines.append(f"- **{label}:** {value}")

        else:
            lines.append("_No metadata available._")

        return "\n".join(lines)

    def compare_datasets_chart(
        self, combined_data, view_option, chart_title,
        sub_option=None, y_axis_label="Value", x_axis_label="Date"
    ):
        fig = go.Figure()
        table_data = []

        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2']
        dash_styles = ['solid', 'dash', 'dot', 'dashdot']

        for idx, (dataset_name, data_df) in enumerate(combined_data):
            display_name = dataset_name.split('[')[0].strip()
            data_df = pd.DataFrame(data_df).sort_values(by="TIME_PERIOD")
            data_df.set_index("TIME_PERIOD", inplace=True)
            data_df = data_df.copy()

            if "OBS_VALUE" not in data_df.columns:
                continue

            frequency = self.infer_frequency(data_df.reset_index())

            if view_option == "Original Data":
                y_values = data_df["OBS_VALUE"]
                trace_name = f"{display_name} (Original)"
                table_df = data_df.reset_index()
                table_label = f"{display_name} – Full Dataset"

            elif view_option == "Period-on-Period":
                if sub_option == "Rate of Change":
                    y_values = data_df["OBS_VALUE"].pct_change() * 100
                    trace_name = f"{display_name} (Period-on-Period % Change)"
                    transformation_label = "Period-on-Period % Change"
                elif sub_option == "Difference":
                    y_values = data_df["OBS_VALUE"].diff()
                    trace_name = f"{display_name} (Period-on-Period Difference)"
                    transformation_label = "Period-on-Period Difference"
                else:
                    continue
                processed_df = pd.DataFrame({
                    "Date": data_df.index.strftime('%Y-%m-%d'),
                    "Index Value": data_df["OBS_VALUE"].values,
                    "Transformed Value": y_values
                })
                table_df = processed_df.reset_index(drop=True)
                table_label = f"{display_name} – {transformation_label}"

            elif view_option == "Interannual":
                if frequency not in ["M", "Q"]:
                    frequency = "M"  # Default fallback

                periods = 12 if frequency == "M" else 4
                if sub_option == "Rate of Change":
                    y_values = data_df["OBS_VALUE"].pct_change(periods=periods) * 100
                    trace_name = f"{display_name} (12-Month % Change)"
                    transformation_label = "12-Month % Change"
                elif sub_option == "Difference":
                    y_values = data_df["OBS_VALUE"].diff(periods=periods)
                    trace_name = f"{display_name} (12-Month Difference)"
                    transformation_label = "12-Month Difference"
                else:
                    continue
                processed_df = pd.DataFrame({
                    "Date": data_df.index.strftime('%Y-%m-%d'),
                    "Index Value": data_df["OBS_VALUE"].values,
                    "Transformed Value": y_values
                })
                table_df = processed_df.reset_index(drop=True)
                table_label = f"{display_name} – {transformation_label}"

            else:
                continue

            fig.add_trace(go.Scatter(
                x=data_df.index,
                y=y_values,
                mode='lines+markers',
                name=trace_name,
                line=dict(
                    color=colors[idx % len(colors)],
                    width=3,
                    dash=dash_styles[idx % len(dash_styles)],
                    shape='spline',
                    smoothing=1.3
                ),
                marker=dict(size=7, symbol='circle', line=dict(width=1, color='white')),
                opacity=0.9,
                yaxis='y',
                hovertemplate='Time: %{x}<br>Value: %{y:.2f}<extra></extra>'
            ))

            table_data.append((table_label, table_df, dataset_name, data_df.reset_index()))

        fig.update_layout(
            height=600,
            title=dict(
                text=chart_title,
                x=0.5,
                xanchor='center',
                font=dict(size=20, family="Arial", color="#333")
            ),
            xaxis=dict(
                title=x_axis_label,
                showgrid=True,
                gridcolor='lightgray',
                zeroline=False
            ),
            yaxis=dict(
                title=y_axis_label,
                side='left',
                showgrid=True,
                gridcolor='lightgray'
            ),
            legend=dict(
                x=0.5,
                y=-0.2,
                orientation='h',
                xanchor='center',
                font=dict(size=13)
            ),
            margin=dict(l=30, r=30, t=50, b=50),
            plot_bgcolor='#f0f7ff',
            paper_bgcolor='#f0f7ff',
            font=dict(size=14, family="Helvetica", color="#333"),
            hovermode="x unified"
        )

        st.plotly_chart(fig, use_container_width=True, key=f"main_chart_{hash(chart_title)}")

        # ✅ Show dataset metadata
        for table_label, table_df, dataset_name, raw_df in table_data:
            with st.expander("ℹ️ View Dataset Description", expanded=False):
                st.markdown(self.describe_metadata(raw_df, dataset_name))

        # ✅ Show data tables if user requests
        if st.checkbox("Show Data Tables"):
            for table_label, table_df, _, _ in table_data:
                st.markdown(f"#### {table_label}")
                st.dataframe(table_df, use_container_width=True)

        return fig, table_data

