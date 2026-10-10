
"""
app.py
------
Streamlit Web Application for the Delivery Performance, Delay Risk, and
Logistics Efficiency Analysis project (APL Logistics / KWE Group).
 
Run:
    streamlit run app.py
 
Modules (per project brief):
  1. Delivery Performance Overview
  2. Delay Risk Analysis Dashboard
  3. Shipping Mode Comparison
  4. Regional & Market Heatmaps
 
Filters (sidebar):
  - Shipping mode
  - Region & market
  - Customer segment
  - Date range (only enabled automatically if a date column is present)
"""
 
import streamlit as st
import pandas as pd
import plotly.express as px
import sys
from pathlib import Path
 
sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))
from data_cleaning import load_and_clean  # noqa: E402
from kpi_analysis import (  # noqa: E402
    on_time_delivery_rate,
    average_delivery_delay,
    late_delivery_risk_ratio,
    shipping_mode_efficiency_index,
    regional_delay_index,
    segment_impact,
)
 
st.set_page_config(
    page_title="APL Logistics | Delivery Performance & Delay Risk Analytics",
    page_icon="📦",
    layout="wide",
)
 
# ---------------------------------------------------------------- DATA LOAD
@st.cache_data
def get_data():
    return load_and_clean(verbose=False, save=False)
 
df_raw = get_data()
 
# ---------------------------------------------------------------- SIDEBAR FILTERS
st.sidebar.title("📦 Filters")
st.sidebar.caption("Unified Mentor × APL Logistics (KWE Group)")
 
modes = st.sidebar.multiselect(
    "Shipping Mode", sorted(df_raw["Shipping Mode"].dropna().unique()),
    default=sorted(df_raw["Shipping Mode"].dropna().unique())
)
markets = st.sidebar.multiselect(
    "Market", sorted(df_raw["Market"].dropna().unique()),
    default=sorted(df_raw["Market"].dropna().unique())
)
regions = st.sidebar.multiselect(
    "Order Region", sorted(df_raw["Order Region"].dropna().unique()),
    default=sorted(df_raw["Order Region"].dropna().unique())
)
segments = st.sidebar.multiselect(
    "Customer Segment", sorted(df_raw["Customer Segment"].dropna().unique()),
    default=sorted(df_raw["Customer Segment"].dropna().unique())
)
 
df = df_raw[
    df_raw["Shipping Mode"].isin(modes)
    & df_raw["Market"].isin(markets)
    & df_raw["Order Region"].isin(regions)
    & df_raw["Customer Segment"].isin(segments)
]
 
st.sidebar.markdown("---")
st.sidebar.metric("Orders in current filter", f"{len(df):,}")
st.sidebar.caption(
    "Data source: `data/raw/` — drop your dataset in as "
    "`supply_chain_data.csv` or `supply_chain_data.csv.gz`."
)
 
# ---------------------------------------------------------------- HEADER
st.title("🚚 Delivery Performance, Delay Risk & Logistics Efficiency Analysis")
st.caption("Global Supply Chain Operations — APL Logistics (KWE Group) · Diagnostic Intelligence Layer")
 
if df.empty:
    st.warning("No records match the current filter selection.")
    st.stop()
 
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Delivery Performance Overview",
    "⚠️ Delay Risk Analysis",
    "🚢 Shipping Mode Comparison",
    "🗺️ Regional & Market Heatmaps",
])
 
# ================================================================== TAB 1
with tab1:
    st.subheader("On-time vs Late Delivery — Baseline KPIs")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("On-Time Delivery Rate", f"{on_time_delivery_rate(df)}%")
    c2.metric("Average Delivery Delay", f"{average_delivery_delay(df)} days")
    c3.metric("Late Delivery Risk Ratio", f"{late_delivery_risk_ratio(df):.2%}")
    c4.metric("Total Orders", f"{len(df):,}")
 
    col1, col2 = st.columns(2)
    with col1:
        class_counts = df["Delivery Classification"].value_counts().reset_index()
        class_counts.columns = ["Classification", "Orders"]
        fig = px.pie(class_counts, names="Classification", values="Orders",
                     title="Delivery Classification Split", hole=0.45,
                     color="Classification",
                     color_discrete_map={"On-time": "#2E7D32", "Delayed": "#C62828", "Early": "#1565C0"})
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        risk_counts = df["Late_delivery_risk"].map({0: "Low / No Risk", 1: "Late Risk Flagged"}).value_counts().reset_index()
        risk_counts.columns = ["Risk", "Orders"]
        fig = px.bar(risk_counts, x="Risk", y="Orders", title="Late Delivery Risk Distribution",
                     color="Risk", color_discrete_sequence=["#2E7D32", "#C62828"])
        st.plotly_chart(fig, use_container_width=True)
 
    st.subheader("Delay Gap Trend by Order Volume Segment")
    trend = df.groupby("Delivery Classification")["Delivery Delay Gap"].agg(["mean", "count"]).reset_index()
    st.dataframe(trend.rename(columns={"mean": "Avg Delay Gap (days)", "count": "Order Count"}), use_container_width=True)
 
# ================================================================== TAB 2
with tab2:
    st.subheader("Late Delivery Risk & Delay Gap Distribution")
    col1, col2 = st.columns(2)
    with col1:
        fig = px.histogram(df, x="Delivery Delay Gap", nbins=40,
                            title="Delivery Delay Gap Histogram (Real − Scheduled Days)",
                            color_discrete_sequence=["#1565C0"])
        fig.add_vline(x=0, line_dash="dash", line_color="red")
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        risk_by_seg = df.groupby("Customer Segment")["Late_delivery_risk"].mean().reset_index()
        risk_by_seg["Late_delivery_risk"] = (risk_by_seg["Late_delivery_risk"] * 100).round(2)
        fig = px.bar(risk_by_seg, x="Customer Segment", y="Late_delivery_risk",
                     title="Late Delivery Risk % by Customer Segment",
                     color="Late_delivery_risk", color_continuous_scale="Reds")
        st.plotly_chart(fig, use_container_width=True)
 
    st.subheader("Customer Segment Impact Analysis")
    st.dataframe(segment_impact(df), use_container_width=True)
 
    st.subheader("Delay Gap by Order Status")
    status_gap = df.groupby("Order Status")["Delivery Delay Gap"].mean().sort_values(ascending=False).reset_index()
    fig = px.bar(status_gap, x="Order Status", y="Delivery Delay Gap", title="Average Delay Gap by Order Status")
    st.plotly_chart(fig, use_container_width=True)
 
# ================================================================== TAB 3
with tab3:
    st.subheader("Shipping Mode Efficiency")
    mode_eff = shipping_mode_efficiency_index(df).reset_index()
    st.dataframe(mode_eff, use_container_width=True)
 
    col1, col2 = st.columns(2)
    with col1:
        fig = px.bar(mode_eff.sort_values("Efficiency Index"), x="Shipping Mode", y="Efficiency Index",
                     title="Shipping Mode Efficiency Index (lower = better)",
                     color="Efficiency Index", color_continuous_scale="RdYlGn_r")
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        fig = px.bar(mode_eff.sort_values("on_time_rate_pct", ascending=False),
                     x="Shipping Mode", y="on_time_rate_pct",
                     title="SLA / On-Time Compliance by Shipping Mode (%)",
                     color="on_time_rate_pct", color_continuous_scale="Greens")
        st.plotly_chart(fig, use_container_width=True)
 
    st.subheader("Delay Gap Distribution by Shipping Mode")
    fig = px.box(df, x="Shipping Mode", y="Delivery Delay Gap", color="Shipping Mode",
                 title="Delay Gap Spread by Shipping Mode")
    st.plotly_chart(fig, use_container_width=True)
 
# ================================================================== TAB 4
with tab4:
    st.subheader("Regional & Market Delay Diagnostics")
 
    view = st.radio("Group by", ["Order Region", "Market"], horizontal=True)
    idx_df = regional_delay_index(df, view).reset_index()
 
    fig = px.bar(idx_df.sort_values("Regional Delay Index", ascending=True),
                 x="Regional Delay Index", y=view, orientation="h",
                 title=f"Regional Delay Index by {view} (higher = higher risk)",
                 color="Regional Delay Index", color_continuous_scale="RdYlGn_r",
                 height=max(400, 28 * len(idx_df)))
    st.plotly_chart(fig, use_container_width=True)
 
    st.subheader("Geographic Delay Map (Customer Coordinates)")
    if {"Latitude", "Longitude"}.issubset(df.columns):
        map_df = df.dropna(subset=["Latitude", "Longitude"]).sample(min(2000, len(df)), random_state=1)
        fig = px.scatter_geo(
            map_df, lat="Latitude", lon="Longitude", color="Delivery Classification",
            color_discrete_map={"On-time": "#2E7D32", "Delayed": "#C62828", "Early": "#1565C0"},
            hover_data=["Order Region", "Market", "Shipping Mode"],
            title="Order Delivery Outcomes by Location", opacity=0.6,
        )
        st.plotly_chart(fig, use_container_width=True)
 
    st.subheader(f"Full {view} Diagnostic Table")
    st.dataframe(idx_df, use_container_width=True)
 
st.markdown("---")
st.caption(
    "Diagnostic intelligence layer for APL Logistics supply chain operations · "
    "Unified Mentor Project · This dashboard is the foundation step before predictive / "
    "optimization-based supply chain modeling."
)
 