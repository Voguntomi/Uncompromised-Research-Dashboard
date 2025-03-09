import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd


class DataVisualization:
    def __init__(self, data_dict):
        """
        Initialize with the data dictionary, which contains the processed data.
        """
        self.data_dict = data_dict

    def line_chart(self, data_df, y_column="OBS_VALUE", title="Line Chart"):
        """
        Create a line chart for the given DataFrame and y_column.
        """
        if "TIME_PERIOD" not in data_df.columns or y_column not in data_df.columns:
            raise ValueError("Data must include 'TIME_PERIOD' and the specified y_column for line chart.")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=data_df["TIME_PERIOD"], y=data_df[y_column], mode="lines", name=y_column))
        fig.update_layout(
            template="plotly_white",
            title=title,
            xaxis_title="Time Period",
            yaxis_title=y_column
        )
        return fig

    def period_on_period_chart(self, data_df, title="Period-on-Period Change"):
        """
        Create a period-on-period comparison chart.
        """
        if "Variance" not in data_df.columns:
            data_df["Variance"] = data_df["OBS_VALUE"].pct_change(periods=1) * 100

        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(
            go.Bar(x=data_df["TIME_PERIOD"], y=data_df["OBS_VALUE"], name="Previous Year", marker_color="blue"),
            secondary_y=False
        )
        fig.add_trace(
            go.Scatter(x=data_df["TIME_PERIOD"], y=data_df["Variance"], mode="lines+markers", name="Variance",
                       marker_color="magenta"),
            secondary_y=True
        )
        fig.update_layout(
            title=title,
            xaxis_title="Time Period",
            yaxis_title="OBS_VALUE",
        )
        return fig

    def interannual_chart(self, data_df, title="Interannual Change"):
        """
        Create an interannual change chart, comparing different years for the same time periods.
        """
        if "Year" not in data_df.columns:
            data_df["Year"] = data_df["TIME_PERIOD"].dt.year  # Add Year column if not present

        pivot_df = data_df.pivot(index="TIME_PERIOD", columns="Year", values="OBS_VALUE")
        fig = go.Figure()
        for col in pivot_df.columns:
            fig.add_trace(go.Bar(x=pivot_df.index, y=pivot_df[col], name=f"Year {col}"))
        fig.update_layout(
            barmode="group",
            title=title,
            xaxis_title="Time Period",
            yaxis_title="OBS_VALUE"
        )
        return fig

    def quarterly_comparison_chart(self, data_df, selected_quarters):
        """
        Create a chart comparing data for specific quarters.
        """
        data_df["Quarter"] = data_df["TIME_PERIOD"].dt.to_period("Q").astype(str)

        # Only filter for selected quarters
        pivot_df = data_df.pivot(index="Quarter", columns="Year", values="OBS_VALUE")
        pivot_df = pivot_df.loc[
            pivot_df.index.str.endswith(tuple(selected_quarters))]  # Filter based on selected quarters

        if pivot_df.empty:
            raise ValueError("No data available for the selected quarters.")

        fig = go.Figure()
        for col in pivot_df.columns:
            fig.add_trace(go.Bar(x=pivot_df.index, y=pivot_df[col], name=f"Year {col}"))
        fig.update_layout(
            barmode="group",
            title="Quarterly Comparison",
            xaxis_title="Quarter",
            yaxis_title="OBS_VALUE"
        )
        return fig

