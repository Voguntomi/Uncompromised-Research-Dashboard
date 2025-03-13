import plotly.graph_objects as go
import pandas as pd
import plotly.express as px


class DataVisualization:
    def __init__(self, df_dict):
        self.df_dict = df_dict

    def compare_datasets_chart(self, combined_data, view_option, chart_title):
        fig = go.Figure()

        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#8064a2']

        for idx, (dataset_name, data_df) in enumerate(combined_data):
            data_df = pd.DataFrame(data_df).sort_values(by="TIME_PERIOD")
            data_df.set_index("TIME_PERIOD", inplace=True)

            axis = 'y1' if idx == 0 else 'y2'

            if view_option == "Original Data":
                fig.add_trace(go.Scatter(
                    x=data_df.index,
                    y=data_df["OBS_VALUE"],
                    mode='lines+markers',
                    name=dataset_name,
                    line=dict(color=colors[idx % len(colors)], width=2),
                    opacity=0.8,
                    yaxis=axis
                ))

            elif view_option == "Period-on-Period":
                data_df["OBS_VALUE"] = data_df["OBS_VALUE"].diff()
                fig.add_trace(go.Scatter(
                    x=data_df.index,
                    y=data_df["OBS_VALUE"],
                    mode='lines',
                    name=dataset_name,
                    line=dict(color=colors[idx % len(colors)], width=2),
                    opacity=0.8,
                    yaxis=axis
                ))

            elif view_option == "Interannual":
                data_df["OBS_VALUE"] = data_df["OBS_VALUE"].pct_change(periods=4) * 100
                fig.add_trace(go.Scatter(
                    x=data_df.index,
                    y=data_df["OBS_VALUE"],
                    mode='lines+markers',
                    name=dataset_name,
                    line=dict(color=colors[idx % len(colors)], width=2),
                    opacity=0.8,
                    yaxis=axis
                ))

        fig.update_layout(
            title=chart_title,
            xaxis_title="Time Period",
            yaxis=dict(title="OBS VALUE", side='left', showgrid=True, gridcolor='lightgray'),
            yaxis2=dict(title="OBS VALUE", overlaying='y', side='right', showgrid=False, visible=True),
            legend=dict(x=0.5, y=-0.2, orientation='h', xanchor='center'),
            margin=dict(l=40, r=40, t=60, b=40),
            plot_bgcolor='#F3F3F3',
            font=dict(size=14),
            barmode='group'
        )

        return fig

    def quarterly_comparison_chart(self, data_df, selected_quarters):
        # Ensure data_df is a DataFrame
        if not isinstance(data_df, pd.DataFrame):
            raise TypeError("Expected data_df to be a DataFrame, but got {}".format(type(data_df)))

        # Correct datetime conversion
        data_df["TIME_PERIOD"] = pd.to_datetime(data_df["TIME_PERIOD"], errors='coerce')
        data_df.set_index("TIME_PERIOD", inplace=True)

        # Filter data for selected quarters
        quarter_data = data_df[data_df.index.quarter.isin([int(q[1]) for q in selected_quarters])]

        # Visualization
        fig = px.bar(quarter_data, x=quarter_data.index, y='OBS_VALUE', title='Quarterly Data')
        return fig




