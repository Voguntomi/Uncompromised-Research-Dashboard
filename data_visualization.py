import plotly.graph_objects as go
import pandas as pd


class DataVisualization:
    def __init__(self, df_dict):
        self.df_dict = df_dict

    def compare_datasets_chart(self, combined_data, view_option, chart_title, sub_option=None, y_axis_label="Value", x_axis_label="Date"):
        fig = go.Figure()
        table_data = []

        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2']
        dash_styles = ['solid', 'dash', 'dot', 'dashdot']

        for idx, (dataset_name, data_df) in enumerate(combined_data):
            data_df = pd.DataFrame(data_df).sort_values(by="TIME_PERIOD")
            data_df.set_index("TIME_PERIOD", inplace=True)
            data_df = data_df.copy()

            axis = 'y' if idx == 0 else 'y2'

            if view_option == "Original Data":
                y_values = data_df["OBS_VALUE"]
                trace_name = f"{dataset_name} (Original)"
            elif view_option == "Period-on-Period":
                if sub_option == "Rate of Change":
                    y_values = data_df["OBS_VALUE"].pct_change() * 100
                    trace_name = f"{dataset_name} (Period-on-Period % Change)"
                elif sub_option == "Difference":
                    y_values = data_df["OBS_VALUE"].diff()
                    trace_name = f"{dataset_name} (Period-on-Period Difference)"
                else:
                    continue
            elif view_option == "Interannual":
                if sub_option == "Rate of Change":
                    y_values = data_df["OBS_VALUE"].pct_change(periods=4) * 100
                    trace_name = f"{dataset_name} (Interannual % Change)"
                elif sub_option == "Difference":
                    y_values = data_df["OBS_VALUE"].diff(periods=4)
                    trace_name = f"{dataset_name} (Interannual Difference)"
                else:
                    continue
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
                yaxis=axis,
                hovertemplate='Time: %{x}<br>Value: %{y:.2f}<extra></extra>'
            ))

            table_df = pd.DataFrame({
                "Time Period": data_df.index.strftime('%Y-%m-%d'),
                "Value": y_values.round(2)
            })
            table_data.append((trace_name, table_df))

        fig.update_layout(
            height=500,  # Adjusted chart height
            title=dict(text=chart_title, x=0.5, xanchor='center', font=dict(size=20, family="Arial", color="#333")),
            xaxis=dict(title=x_axis_label, showgrid=True, gridcolor='lightgray', zeroline=False),
            yaxis=dict(title=y_axis_label, side='left', showgrid=True, gridcolor='lightgray'),
            yaxis2=dict(title=y_axis_label + " (2)", overlaying='y', side='right', showgrid=False, visible=True),
            legend=dict(x=0.5, y=-0.2, orientation='h', xanchor='center', font=dict(size=13)),
            margin=dict(l=60, r=60, t=80, b=80),
            plot_bgcolor='#ffffff',
            paper_bgcolor='#ffffff',
            font=dict(size=14, family="Helvetica", color="#333"),
            hovermode="x unified"
        )

        return fig, table_data

