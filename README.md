# 🚚 Delivery Performance, Delay Risk & Logistics Efficiency Analysis

> Diagnostic analytics of on-time delivery, delay risk, and shipping-mode efficiency for **APL Logistics (KWE Group)**, with an interactive Streamlit dashboard.

🔗 **Live Dashboard:** `<paste your Streamlit app link here>`

---

## 📌 Overview

Logistics teams record thousands of orders but often cannot say clearly how many arrive on time, how many are late, and where the risk sits. This project builds a **diagnostic layer** that answers four questions:

1. How often are deliveries on-time, delayed, or early?
2. What does the dataset's `Late_delivery_risk` flag actually measure?
3. Which shipping modes, regions, and markets carry the most delay risk?
4. Are some customer segments more exposed than others?

Prepared for: **APL Logistics (KWE Group)** | Programme: **Unified Mentor**

## 🎯 Objectives

- Quantify on-time, delayed, and early deliveries
- Explain the late-delivery risk indicator
- Identify high-risk shipping modes, regions, and markets
- Compare delay exposure across customer segments
- Deliver all KPIs in a live, filterable dashboard

## 📊 Dataset

An order-line-level dataset with **40 columns** (following the DataCo Smart Supply Chain schema) covering shipping durations, delivery status, the late-risk flag, customer segment, geography, and financial fields.

> ⚠️ **Data note:** No raw file came with the project brief, so the results and the live dashboard use a **synthetic demonstration dataset** (6,025 generated orders, 5,910 after cleaning). The app generates it automatically when no data file is present. To use real data, place it at `data/raw/supply_chain_data.csv` (or `supply_chain_data.csv.gz`) and the whole pipeline will use it instead. Values will differ on real data.

## 🧪 Methodology

1. **Cleaning & validation:** removed duplicates, rows with missing critical fields, and invalid shipping durations (kept 0–60 days); standardized text fields.
2. **Delivery Delay Gap:**

```
   Delay Gap = Days for shipping (real) − Days for shipment (scheduled)
```

   | Gap | Class |
   | --- | --- |
   | = 0 | On-time |
   | > 0 | Delayed |
   | < 0 | Early |

3. **KPI layer:** five KPIs computed overall and by shipping mode, region, market, and customer segment.
4. **Dashboard:** a Streamlit app with four modules and sidebar filters.

## 📈 Key Performance Indicators

| KPI | Result |
| --- | --- |
| On-Time Delivery Rate | 28.2% |
| Delayed orders | 38.9% |
| Early orders | 32.9% |
| Average Delivery Delay | 0.13 days |
| Late Delivery Risk Ratio | 38.9% |
| Shipping Mode Efficiency Index | 1.05 (Standard) to 2.13 (Same Day) |
| Regional Delay Index | 0.96 (North Africa) to 1.64 (Canada) |

Efficiency and regional indices = average delay (floored at 0) + 3 × late-risk ratio. Lower is better for modes; higher means higher risk for regions.

## 🔍 Key Findings

- **Delays are systemic:** only 28.2% of orders arrive exactly on time and 38.9% arrive late.
- **Averages hide risk:** the mean delay is just 0.13 days, but 16.7% of orders are 2 or more days late.
- **The risk flag is an outcome, not a warning:** `Late_delivery_risk` equals 1 for exactly the delayed orders.
- **Expedited modes are weakest:** Same Day (index 2.13) and First Class (1.81) are far less efficient than Standard Class (1.05).
- **Risk is uneven by region:** Canada, West Africa, and Eastern Asia rank highest; market-level averages hide these local differences.
- **No segment is protected:** late-risk is 38.6%–39.3% across Consumer, Corporate, and Home Office.
- **Delays cost money:** delayed orders earn about 5% less benefit per order.

## 💡 Recommendations

1. Recalibrate delivery windows for Same Day and First Class.
2. Review carriers and routes in the highest-risk regions.
3. Quote delivery dates at booking from mode and region history.
4. Apply mitigation across all customer segments.
5. Track the KPIs weekly or monthly in the dashboard.
6. Build a predictive model to flag late risk at order intake.

## 📊 Dashboard Modules

- **Delivery Performance Overview**
- **Delay Risk Analysis**
- **Shipping Mode Comparison**
- **Regional & Market Heatmaps**

Sidebar filters: **Shipping Mode · Market · Order Region · Customer Segment**

## 🚀 How to Run

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. (Optional) Clean the data and print the KPI report
py src\data_cleaning.py
py src\kpi_analysis.py

# 3. Launch the dashboard
py -m streamlit run app.py
```

The dashboard opens at `http://localhost:8501`. On Mac/Linux, use `python3` and forward slashes (`src/data_cleaning.py`).

## 📁 Project Structure

```
├── src/
│   ├── data_cleaning.py          # cleaning, validation, delay gap & classification
│   ├── kpi_analysis.py           # the five KPIs and diagnostics
│   └── generate_sample_data.py   # synthetic demo dataset generator
├── app.py                        # Streamlit dashboard
├── requirements.txt
├── Research_Paper_Delivery_Performance_Analysis.docx
├── Executive_Summary.docx
└── README.md
```

## 🛠️ Tech Stack

Python · pandas · NumPy · Plotly · Streamlit

## 📄 Documents

- **Research paper:** `Research_Paper_Delivery_Performance_Analysis.docx`
- **Executive summary:** `Executive_Summary.docx`

## 👤 Author

**Yashraj Sagar Shedage**
