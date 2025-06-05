import streamlit as st

# ✅ Page setup
st.set_page_config(page_title="Uncompromised Research Dashboard", layout="wide")

from eurostat_page import run_eurostat_dashboard
from ecb_dashboard import Dashboard

# ------------------ Sidebar Title ------------------
st.sidebar.markdown(
    """
    <div style="
        padding: 6px 0 14px 0;
        font-size: 20px;
        font-weight: 700;
        color: #333333;
        border-bottom: 2px solid #4F8BF9;
        letter-spacing: 0.5px;
    ">
        📋 Menu
    </div>
    """,
    unsafe_allow_html=True
)

# ------------------ Page Options ------------------
menu = ["ECB Dashboard", "Eurostat Dashboard"]
choice = st.sidebar.radio("Select a page", menu)

# ------------------ Routing ------------------
if choice == "ECB Dashboard":
    dashboard = Dashboard("ecb_dashboard_data.pkl")
    dashboard.run()

elif choice == "Eurostat Dashboard":
    run_eurostat_dashboard()
