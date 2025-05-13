import plotly.graph_objects as go
import pandas as pd
from pandas.tseries.frequencies import to_offset

class DataVisualization:
    def __init__(self, df_dict):
        self.df_dict = df_dict

    @staticmethod
    def infer_frequency(df):
        if "TIME_PERIOD" not in df.columns or len(df) < 3:
            return "unknown"
        try:
            df_sorted = df.sort_values("TIME_PERIOD")
            df_sorted["TIME_PERIOD"] = pd.to_datetime(df_sorted["TIME_PERIOD"])
            diffs = pd.Series(df_sorted["TIME_PERIOD"].diff().dropna().values).unique()
            if len(diffs) == 1:
                return to_offset(diffs[0]).name
        except Exception:
            return "unknown"
        return "unknown"

    @staticmethod
    def describe_metadata_markdown(df):
        lines = []
        if df is not None and isinstance(df, pd.DataFrame):
            df = df.copy()
            df.dropna(axis=1, how="all", inplace=True)

            def get_unique(colname):
                if colname in df.columns:
                    vals = df[colname].dropna().unique()
                    if len(vals) > 0:
                        return vals[0]
                return None

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

    @staticmethod
    def generate_summary_stats(df):
        if df.empty or "OBS_VALUE" not in df.columns:
            return pd.DataFrame(columns=["Metric", "Value"])

        stats = {
            "Min": df["OBS_VALUE"].min(),
            "Max": df["OBS_VALUE"].max(),
            "Mean": df["OBS_VALUE"].mean(),
            "Std Dev": df["OBS_VALUE"].std(),
            "Latest": df["OBS_VALUE"].iloc[-1],
            "Count": df["OBS_VALUE"].count(),
            "Start Date": df.index.min().strftime("%Y-%m-%d"),
            "End Date": df.index.max().strftime("%Y-%m-%d"),
        }

        return pd.DataFrame(
            [(k, str(v)) for k, v in stats.items()],
            columns=["Metric", "Value"]
        )

    def assign_colors_and_axes(self, dataset_names, units):
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2']
        axis_assignments = {}
        color_map = {}

        for idx, name in enumerate(dataset_names):
            color_map[name] = colors[idx % len(colors)]
            axis_assignments[name] = "left" if idx == 0 else "right"

        return color_map, axis_assignments

    def compare_datasets_chart(
        self, combined_data, view_option, chart_title,
        sub_option=None, y_axis_label=None, x_axis_label="Date",
        chart_height=500, chart_type="line", log_scale=False
    ):
        fig = go.Figure()
        table_data = []
        units = {}
        datasets = [name for name, _ in combined_data]

        for name, df in combined_data:
            unit = df["UNIT"].dropna().unique()[0] if "UNIT" in df.columns and not df["UNIT"].dropna().empty else ""
            units[name] = unit

        color_map, axis_map = self.assign_colors_and_axes(datasets, units)

        for idx, (original_name, data_df) in enumerate(combined_data):
            dataset_name = original_name  # for label formatting only

            data_df = pd.DataFrame(data_df).sort_values(by="TIME_PERIOD")
            data_df["TIME_PERIOD"] = pd.to_datetime(data_df["TIME_PERIOD"])
            data_df.set_index("TIME_PERIOD", inplace=True)
            data_df = data_df.copy()

            if "OBS_VALUE" not in data_df.columns:
                continue

            y_values = data_df["OBS_VALUE"]

            if view_option == "Period-on-Period":
                if sub_option == "Rate of Change":
                    y_values = y_values.pct_change() * 100
                    dataset_name += " (% Change)"
                elif sub_option == "Difference":
                    y_values = y_values.diff()
                    dataset_name += " (Diff)"
            elif view_option == "Interannual":
                freq = self.infer_frequency(data_df.reset_index())
                periods = 12 if freq == "M" else 4 if freq == "Q" else 1
                if sub_option == "Rate of Change":
                    y_values = y_values.pct_change(periods=periods) * 100
                    dataset_name += " (YoY %)"
                elif sub_option == "Difference":
                    y_values = y_values.diff(periods=periods)
                    dataset_name += " (YoY Diff)"

            data_df["OBS_VALUE"] = y_values

            # Format label
            if "(" in dataset_name and ")" in dataset_name:
                main_title = dataset_name.split("(", 1)[0].strip()
                detail = dataset_name[len(main_title):].strip(" ()")
                trace_label = f"<b>{main_title}</b><br><span style='font-size:11px; font-weight:normal;'>({detail})</span>"
            else:
                trace_label = f"<b>{dataset_name}</b>"

            # ✅ use original_name for lookups
            y_axis_side = "y2" if axis_map[original_name] == "right" else "y"
            color = color_map[original_name]

            trace_args = dict(
                x=data_df.index,
                y=data_df["OBS_VALUE"],
                name=trace_label,
                marker=dict(color=color),
                yaxis=y_axis_side
            )

            if chart_type == "line":
                fig.add_trace(go.Scatter(mode='lines+markers', **trace_args))
            elif chart_type == "area":
                fig.add_trace(go.Scatter(mode='lines', fill='tozeroy', **trace_args))
            elif chart_type == "bar":
                fig.add_trace(go.Bar(**trace_args))
            elif chart_type == "scatter":
                fig.add_trace(go.Scatter(mode='markers', **trace_args))

            stats_df = self.generate_summary_stats(data_df)
            table_data.append((dataset_name, data_df.reset_index(), original_name, data_df.reset_index(), stats_df))

        if y_axis_label is None:
            first_df = combined_data[0][1]
            if "UNIT" in first_df.columns:
                unit_col = first_df["UNIT"].dropna().astype(str).str.strip().unique()
                if len(unit_col) > 0 and unit_col[0]:
                    y_axis_label = unit_col[0]
                elif "UNIT_DESCR" in first_df.columns:
                    unit_col = first_df["UNIT_DESCR"].dropna().astype(str).str.strip().unique()
                    y_axis_label = unit_col[0] if len(unit_col) > 0 and unit_col[0] else "Value"
                else:
                    y_axis_label = "Value"
            else:
                y_axis_label = "Value"

        secondary_label = (
            units[datasets[1]] if len(datasets) > 1 and datasets[1] in units and units[datasets[1]] else "Secondary Axis"
        )

        fig.update_layout(
            title=dict(
                text=chart_title,
                x=0.5,
                xanchor='center',
                font=dict(size=16)
            ),
            height=chart_height,
            xaxis=dict(title=x_axis_label),
            yaxis=dict(title=y_axis_label, side="left", showgrid=True),
            yaxis2=dict(
                title=secondary_label,
                overlaying='y',
                side='right',
                showgrid=False,
                showticklabels=True,
                visible=True
            ),
            legend=dict(
                orientation="h",
                x=0.5,
                xanchor="center",
                y=-0.2,
                title_text="",
                font=dict(size=11)
            ),
            margin=dict(l=30, r=30, t=50, b=60),
            hovermode="x unified",
            plot_bgcolor='#f0f7ff',
            paper_bgcolor='#f0f7ff'
        )

        return fig, table_data, color_map, axis_map
