"""
kpi_analysis.py
----------------
Step 2-6 of the methodology: KPI computation & diagnostics.

Implements the five KPIs from the project brief plus supporting diagnostics
used by the Streamlit dashboard and the research paper:

  1. On-Time Delivery Rate (%)
  2. Average Delivery Delay (Days)
  3. Late Delivery Risk Ratio
  4. Shipping Mode Efficiency Index
  5. Regional Delay Index

Run standalone to print a full console report:
    python src/kpi_analysis.py
"""

import pandas as pd
from data_cleaning import load_and_clean


def on_time_delivery_rate(df: pd.DataFrame) -> float:
    return round((df["Delivery Classification"] == "On-time").mean() * 100, 2)


def average_delivery_delay(df: pd.DataFrame) -> float:
    return round(df["Delivery Delay Gap"].mean(), 2)


def late_delivery_risk_ratio(df: pd.DataFrame) -> float:
    return round(df["Late_delivery_risk"].mean(), 4)


def shipping_mode_efficiency_index(df: pd.DataFrame) -> pd.DataFrame:
    """Lower index = more efficient (less average delay, lower risk ratio)."""
    g = df.groupby("Shipping Mode").agg(
        avg_delay_gap=("Delivery Delay Gap", "mean"),
        late_risk_ratio=("Late_delivery_risk", "mean"),
        on_time_rate_pct=("Delivery Classification", lambda x: (x == "On-time").mean() * 100),
        order_count=("Delivery Delay Gap", "count"),
    ).round(3)
    g["Efficiency Index"] = (g["avg_delay_gap"].clip(lower=0) + g["late_risk_ratio"] * 3).round(3)
    return g.sort_values("Efficiency Index")


def regional_delay_index(df: pd.DataFrame, group_col: str = "Order Region") -> pd.DataFrame:
    g = df.groupby(group_col).agg(
        avg_delay_gap=("Delivery Delay Gap", "mean"),
        late_risk_ratio=("Late_delivery_risk", "mean"),
        on_time_rate_pct=("Delivery Classification", lambda x: (x == "On-time").mean() * 100),
        order_count=("Delivery Delay Gap", "count"),
    ).round(3)
    g["Regional Delay Index"] = (g["avg_delay_gap"].clip(lower=0) + g["late_risk_ratio"] * 3).round(3)
    return g.sort_values("Regional Delay Index", ascending=False)


def segment_impact(df: pd.DataFrame) -> pd.DataFrame:
    return df.groupby("Customer Segment").agg(
        avg_delay_gap=("Delivery Delay Gap", "mean"),
        late_risk_ratio=("Late_delivery_risk", "mean"),
        on_time_rate_pct=("Delivery Classification", lambda x: (x == "On-time").mean() * 100),
        avg_benefit=("Benefit per order", "mean"),
        order_count=("Delivery Delay Gap", "count"),
    ).round(3)


def full_report(df: pd.DataFrame) -> dict:
    return {
        "on_time_delivery_rate_pct": on_time_delivery_rate(df),
        "average_delivery_delay_days": average_delivery_delay(df),
        "late_delivery_risk_ratio": late_delivery_risk_ratio(df),
        "shipping_mode_efficiency": shipping_mode_efficiency_index(df),
        "regional_delay_index": regional_delay_index(df),
        "market_delay_index": regional_delay_index(df, "Market"),
        "segment_impact": segment_impact(df),
    }


if __name__ == "__main__":
    df = load_and_clean(verbose=True)
    report = full_report(df)

    print("\n=== OVERALL KPIs ===")
    print(f"On-Time Delivery Rate:   {report['on_time_delivery_rate_pct']}%")
    print(f"Average Delivery Delay:  {report['average_delivery_delay_days']} days")
    print(f"Late Delivery Risk Ratio:{report['late_delivery_risk_ratio']}")

    print("\n=== SHIPPING MODE EFFICIENCY INDEX (lower = better) ===")
    print(report["shipping_mode_efficiency"])

    print("\n=== REGIONAL DELAY INDEX (top 10 highest risk) ===")
    print(report["regional_delay_index"].head(10))

    print("\n=== MARKET DELAY INDEX ===")
    print(report["market_delay_index"])

    print("\n=== CUSTOMER SEGMENT IMPACT ===")
    print(report["segment_impact"])
