import eurostat
import pandas as pd
import numpy as np
import scipy.stats as stats
import plotly.graph_objects as go
import streamlit as st

# ------------------ 1. Fetch Data ------------------
def fetch_data(dataset_code, filter_pars):
    return eurostat.get_data_df(dataset_code, filter_pars=filter_pars)

# ------------------ 2. Prepare Data ------------------
def prepare_data(df_data):
    dataframes = {}
    for coicop in df_data['coicop'].unique():
        df_filtered = df_data[df_data['coicop'] == coicop].drop(columns=['freq', 'unit', 'coicop'])
        dataframes[f'd_{coicop}'] = df_filtered.set_index('geo\\TIME_PERIOD')
    return dataframes

# ------------------ 3. Compute Month-over-Month ------------------
def compute_month_over_month(dataframes):
    return {
        key: df.pct_change(axis=1, fill_method=None) * 100
        for key, df in dataframes.items()
    }

# ------------------ 4. Compute Percentiles ------------------
def compute_percentiles(mom_dataframes):
    percentile_dict = {}
    for key, df in mom_dataframes.items():
        df_percentiles = df.copy()
        months = df.columns.str[-2:].unique()
        for geo in df.index:
            for month in months:
                month_cols = [col for col in df.columns if col.endswith(month)]
                month_values = df.loc[geo, month_cols].dropna().values
                if month_values.size == 0:
                    continue
                percentiles = [
                    stats.percentileofscore(month_values, val, kind='rank') if not np.isnan(val) else np.nan
                    for val in df.loc[geo, month_cols]
                ]
                df_percentiles.loc[geo, month_cols] = percentiles
        percentile_dict[key] = df_percentiles
    return percentile_dict

# ------------------ 5. Calculate Monthly Medians ------------------
def calculate_monthly_medians(mom_dataframes):
    records = []
    for key, df in mom_dataframes.items():
        months = sorted(df.columns.str[-2:].unique())
        for geo in df.index:
            medians = {'coicop': key, 'geo': geo}
            for month in months:
                month_cols = [col for col in df.columns if col.endswith(month)]
                month_values = df.loc[geo, month_cols].values
                month_values = month_values[~np.isnan(month_values)]
                medians[month] = np.median(month_values) if month_values.size > 0 else np.nan
            records.append(medians)
    median_df = pd.DataFrame(records)
    median_df = median_df.set_index(['coicop', 'geo']).sort_index(axis=1)
    return median_df

# ------------------ 6. Plot Dynamic Charts ------------------
def plot_data(df_dict, start_year, selected_geos=None, moving_avg_period=12):
    for key, df in df_dict.items():
        filtered_cols = [col for col in df.columns if int(col[:4]) >= start_year]
        if not filtered_cols:
            continue

        df_filtered = df[filtered_cols]
        if selected_geos:
            df_filtered = df_filtered.loc[selected_geos]

        df_transposed = df_filtered.T
        df_transposed.index.name = "Date"

        # --- Percentile Chart ---
        if moving_avg_period == 0:
            fig = go.Figure()

            for geo in df_transposed.columns:
                fig.add_trace(go.Scatter(
                    x=df_transposed.index,
                    y=df_transposed[geo],
                    mode="lines",
                    name=geo,
                    line=dict(width=2)
                ))

            fig.update_layout(
                title={
                    "text": f"<b>Percentiles for {key} (From {start_year})</b><br><span style='font-size:13px; font-weight:normal'>Monthly inflation percentiles by country</span>",
                    "x": 0.5,
                    "xanchor": "center"
                },
                xaxis=dict(
                    title=dict(text="Date", font=dict(size=13)),
                    tickfont=dict(size=12)
                ),
                yaxis=dict(
                    title=dict(text="Percentile", font=dict(size=13)),
                    tickfont=dict(size=12)
                ),
                height=500,
                template="simple_white",
                plot_bgcolor="#f8fafd",
                paper_bgcolor="#f8fafd",
                font=dict(family="Arial", size=13),
                legend=dict(title="", font=dict(size=12))
            )
            st.plotly_chart(fig, use_container_width=True)

        # --- Moving Average Chart ---
        else:
            df_moving_avg = df_transposed.rolling(window=moving_avg_period, min_periods=1).mean()

            fig_avg = go.Figure()

            for geo in df_moving_avg.columns:
                fig_avg.add_trace(go.Scatter(
                    x=df_moving_avg.index,
                    y=df_moving_avg[geo],
                    mode="lines",
                    name=geo,
                    line=dict(width=2)
                ))

            fig_avg.update_layout(
                title={
                    "text": f"<b>{moving_avg_period}-Month Moving Average for {key} (From {start_year})</b><br><span style='font-size:13px; font-weight:normal'>Smoothed trends by country</span>",
                    "x": 0.5,
                    "xanchor": "center"
                },
                xaxis=dict(
                    title=dict(text="Date", font=dict(size=13)),
                    tickfont=dict(size=12)
                ),
                yaxis=dict(
                    title=dict(text="Moving Avg. Percentile", font=dict(size=13)),
                    tickfont=dict(size=12)
                ),
                height=500,
                template="simple_white",
                plot_bgcolor="#f8fafd",
                paper_bgcolor="#f8fafd",
                font=dict(family="Arial", size=13),
                legend=dict(title="", font=dict(size=12))
            )
            st.plotly_chart(fig_avg, use_container_width=True)
