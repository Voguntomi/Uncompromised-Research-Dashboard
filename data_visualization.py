import plotly.graph_objects as go
import pandas as pd
from pandas.tseries.frequencies import to_offset
import streamlit as st
import io


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

    def compare_datasets_chart(self, combined_data, view_option, chart_title, sub_option=None, y_axis_label="Value", x_axis_label="Date"):
        fig = go.Figure()
        table_data = []

        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2']
        dash_styles = ['solid', 'dash', 'dot', 'dashdot']

        for idx, (dataset_name, data_df) in enumerate(combined_data):
            data_df = pd.DataFrame(data_df).sort_values(by="TIME_PERIOD")
            data_df.set_index("TIME_PERIOD", inplace=True)
            data_df = data_df.copy()

            if "OBS_VALUE" not in data_df.columns:
                continue

            axis = 'y' if idx == 0 else 'y2'
            frequency = self.infer_frequency(data_df.reset_index())

            if view_option == "Original Data":
                y_values = data_df["OBS_VALUE"]
                trace_name = f"{dataset_name} (Original)"
                table_df = data_df.reset_index()
                table_label = f"{dataset_name} – Full Dataset"
            elif view_option == "Period-on-Period":
                if sub_option == "Rate of Change":
                    y_values = data_df["OBS_VALUE"].pct_change() * 100
                    trace_name = f"{dataset_name} (Period-on-Period % Change)"
                    transformation_label = "Period-on-Period % Change"
                elif sub_option == "Difference":
                    y_values = data_df["OBS_VALUE"].diff()
                    trace_name = f"{dataset_name} (Period-on-Period Difference)"
                    transformation_label = "Period-on-Period Difference"
                else:
                    continue
            elif view_option == "Interannual":
                if frequency not in ["M", "Q"]:
                    continue
                periods = 12 if frequency == "M" else 4
                if sub_option == "Rate of Change":
                    y_values = data_df["OBS_VALUE"].pct_change(periods=periods) * 100
                    trace_name = f"{dataset_name} (12-Month % Change)"
                    transformation_label = "12-Month % Change"
                elif sub_option == "Difference":
                    y_values = data_df["OBS_VALUE"].diff(periods=periods)
                    trace_name = f"{dataset_name} (12-Month Difference)"
                    transformation_label = "12-Month Difference"
                else:
                    continue
            else:
                continue

            if view_option != "Original Data":
                processed_df = pd.DataFrame({
                    "Date": data_df.index.strftime('%Y-%m-%d'),
                    "Index Value": data_df["OBS_VALUE"].values,
                    "Transformed Value": y_values
                })
                table_df = processed_df.reset_index(drop=True)
                table_label = f"{dataset_name} – {transformation_label}"

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
                yaxis=axis,
                hovertemplate='Time: %{x}<br>Value: %{y:.2f}<extra></extra>'
            ))

            with st.expander(f"Export Table: {dataset_name}"):
                csv = table_df.to_csv(index=False).encode('utf-8')
                st.download_button("Download CSV", csv, f"{dataset_name}.csv", "text/csv")

                excel_buffer = io.BytesIO()
                with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                    table_df.to_excel(writer, index=False)
                st.download_button("Download Excel", data=excel_buffer.getvalue(), file_name=f"{dataset_name}.xlsx")

            table_data.append((table_label, table_df))

        fig.update_layout(
            height=500,
            title=dict(text=chart_title, x=0.5, xanchor='center', font=dict(size=20, family="Arial", color="#333")),
            xaxis=dict(title=x_axis_label, showgrid=True, gridcolor='lightgray', zeroline=False),
            yaxis=dict(title=y_axis_label, side='left', showgrid=True, gridcolor='lightgray'),
            yaxis2=dict(title=y_axis_label + " (2)", overlaying='y', side='right', showgrid=False, visible=True),
            legend=dict(x=0.5, y=-0.2, orientation='h', xanchor='center', font=dict(size=13)),
            margin=dict(l=60, r=60, t=80, b=80),
            plot_bgcolor='#f0f7ff',
            paper_bgcolor='#f0f7ff',
            font=dict(size=14, family="Helvetica", color="#333"),
            hovermode="x unified"
        )

        return fig, table_data
