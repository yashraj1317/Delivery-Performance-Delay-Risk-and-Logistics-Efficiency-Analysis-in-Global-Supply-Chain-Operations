"""
generate_sample_data.py
------------------------
Generates a realistic SYNTHETIC sample dataset that matches the exact column
schema described in the project brief (this mirrors the structure of the
well-known "DataCo Smart Supply Chain" dataset).

WHY THIS EXISTS:
No raw CSV was uploaded with the project brief. This script lets the entire
pipeline (cleaning -> KPIs -> dashboard) run end-to-end immediately for
testing/demo purposes. The moment you have the REAL dataset, drop it in as:

    data/raw/supply_chain_data.csv

...and the cleaning script / dashboard will use it automatically instead
(see data_cleaning.py — it prefers a real file if present).

Run:
    python src/generate_sample_data.py
"""

import numpy as np
import pandas as pd
from pathlib import Path

RNG = np.random.default_rng(42)
N_ROWS = 6000

OUT_PATH = Path(__file__).resolve().parents[1] / "data" / "raw" / "sample_supply_chain_data.csv"

SHIPPING_MODES = ["Standard Class", "First Class", "Second Class", "Same Day"]
SHIPPING_MODE_WEIGHTS = [0.55, 0.15, 0.22, 0.08]

PAYMENT_TYPES = ["Debit", "Credit", "Cash", "Transfer"]
PAYMENT_WEIGHTS = [0.35, 0.40, 0.15, 0.10]

CUSTOMER_SEGMENTS = ["Consumer", "Corporate", "Home Office"]
SEGMENT_WEIGHTS = [0.52, 0.30, 0.18]

MARKETS = ["LATAM", "Europe", "Pacific Asia", "USCA", "Africa"]
MARKET_WEIGHTS = [0.28, 0.26, 0.20, 0.18, 0.08]

REGION_BY_MARKET = {
    "LATAM": ["South America", "Central America", "Caribbean"],
    "Europe": ["Western Europe", "Northern Europe", "Southern Europe", "Eastern Europe"],
    "Pacific Asia": ["Southeast Asia", "Eastern Asia", "Oceania", "South Asia"],
    "USCA": ["US Center", "West of USA", "East of USA", "South of USA", "Canada"],
    "Africa": ["West Africa", "East Africa", "North Africa"],
}

COUNTRIES_BY_MARKET = {
    "LATAM": ["Brazil", "Mexico", "Argentina", "Colombia", "Peru"],
    "Europe": ["Germany", "France", "United Kingdom", "Italy", "Spain", "Poland"],
    "Pacific Asia": ["China", "Japan", "Indonesia", "Australia", "India", "Vietnam"],
    "USCA": ["United States", "Canada"],
    "Africa": ["Nigeria", "Kenya", "Egypt", "South Africa"],
}

CATEGORIES = [
    (1, "Fitness"), (2, "Cleats"), (3, "Electronics"), (4, "Cardio Equipment"),
    (5, "Camping & Hiking"), (6, "Women's Apparel"), (7, "Men's Footwear"),
    (8, "Indoor/Outdoor Games"), (9, "Kitchen"), (10, "Office Supplies"),
]

DEPARTMENTS = [
    (2, "Fitness"), (3, "Footwear"), (4, "Apparel"), (5, "Golf"),
    (6, "Outdoors"), (7, "Fan Shop"), (8, "Technology"),
]

PRODUCT_NAMES = [
    "Nike Men's Running Shoe", "Under Armour Fleece Hoodie", "Perfect Fitness Perfect Rip Deck",
    "O'Brien Men's Neoprene Life Vest", "Diamondback Bike", "Field & Stream Sleeping Bag",
    "Team Golf Cart Umbrella", "Nike Women's Tempo Shorts", "Coleman Cooler",
    "Yoga Mat Premium", "Adidas Kids' Soccer Cleat", "Wilson Evolution Basketball",
]

# Base delay-risk factors per shipping mode (Same Day/First Class -> lower scheduled days,
# higher relative delay risk under load; Standard -> baseline)
MODE_DELAY_BIAS = {
    "Standard Class": 0.0,
    "First Class": 0.35,
    "Second Class": 0.10,
    "Same Day": 0.55,
}

MODE_SCHEDULED_DAYS = {
    "Standard Class": 4,
    "First Class": 2,
    "Second Class": 3,
    "Same Day": 1,
}


def gen_customer_locations(market):
    country = RNG.choice(COUNTRIES_BY_MARKET[market])
    lat = RNG.uniform(-55, 65)
    lon = RNG.uniform(-120, 140)
    return country, round(lat, 4), round(lon, 4)


def build_row(i):
    market = RNG.choice(MARKETS, p=MARKET_WEIGHTS)
    order_region = RNG.choice(REGION_BY_MARKET[market])
    order_country, lat, lon = gen_customer_locations(market)
    customer_country = order_country

    shipping_mode = RNG.choice(SHIPPING_MODES, p=SHIPPING_MODE_WEIGHTS)
    scheduled_days = MODE_SCHEDULED_DAYS[shipping_mode] + RNG.integers(0, 2)

    # Real shipping days: baseline = scheduled + noise, biased by mode & a random regional friction factor
    regional_friction = RNG.normal(0, 1.0)
    mode_bias = MODE_DELAY_BIAS[shipping_mode]
    delay_noise = RNG.normal(loc=mode_bias, scale=1.3) + regional_friction * 0.4
    real_days = max(0, round(scheduled_days + delay_noise))

    late_risk = 1 if real_days > scheduled_days else 0

    delivery_status = (
        "Late delivery" if late_risk == 1 and real_days > scheduled_days
        else ("Advance shipping" if real_days < scheduled_days else "Shipping on time")
    )
    if RNG.random() < 0.02:
        delivery_status = "Shipping canceled"

    cat_id, cat_name = CATEGORIES[RNG.integers(0, len(CATEGORIES))]
    dept_id, dept_name = DEPARTMENTS[RNG.integers(0, len(DEPARTMENTS))]
    product_name = RNG.choice(PRODUCT_NAMES)
    product_price = round(RNG.uniform(15, 400), 2)

    discount_rate = round(RNG.uniform(0, 0.25), 2)
    discount = round(product_price * discount_rate, 2)
    qty = int(RNG.integers(1, 5))
    order_item_total = round((product_price - discount) * qty, 2)
    sales = round(product_price * qty, 2)
    profit_ratio = round(RNG.uniform(-0.15, 0.35), 3)
    profit_per_order = round(order_item_total * profit_ratio, 2)
    benefit_per_order = round(profit_per_order + RNG.normal(0, 5), 2)
    sales_per_customer = round(sales * RNG.uniform(0.9, 1.3), 2)

    segment = RNG.choice(CUSTOMER_SEGMENTS, p=SEGMENT_WEIGHTS)
    payment = RNG.choice(PAYMENT_TYPES, p=PAYMENT_WEIGHTS)

    order_status = RNG.choice(
        ["COMPLETE", "PENDING", "CLOSED", "ON_HOLD", "PROCESSING", "CANCELED"],
        p=[0.45, 0.15, 0.15, 0.10, 0.10, 0.05],
    )

    return {
        "Type": payment,
        "Days for shipping (real)": real_days,
        "Days for shipment (scheduled)": scheduled_days,
        "Benefit per order": benefit_per_order,
        "Sales per customer": sales_per_customer,
        "Delivery Status": delivery_status,
        "Late_delivery_risk": late_risk,
        "Category Id": cat_id,
        "Category Name": cat_name,
        "Customer City": f"City_{RNG.integers(1, 400)}",
        "Customer Country": customer_country,
        "Customer Fname": f"FName{RNG.integers(1, 5000)}",
        "Customer Id": int(RNG.integers(10000, 99999)),
        "Customer Lname": f"LName{RNG.integers(1, 5000)}",
        "Customer Segment": segment,
        "Customer State": f"State_{RNG.integers(1, 60)}",
        "Customer Street": f"{RNG.integers(100,9999)} Main St",
        "Customer Zipcode": int(RNG.integers(10000, 99999)),
        "Department Id": dept_id,
        "Department Name": dept_name,
        "Latitude": lat,
        "Longitude": lon,
        "Market": market,
        "Order City": f"City_{RNG.integers(1, 400)}",
        "Order Country": order_country,
        "Order Customer Id": int(RNG.integers(10000, 99999)),
        "Order Item Discount": discount,
        "Order Item Discount Rate": discount_rate,
        "Order Item Product Price": product_price,
        "Order Item Profit Ratio": profit_ratio,
        "Order Item Quantity": qty,
        "Sales": sales,
        "Order Item Total": order_item_total,
        "Order Profit Per Order": profit_per_order,
        "Order Region": order_region,
        "Order State": f"State_{RNG.integers(1, 60)}",
        "Order Status": order_status,
        "Product Name": product_name,
        "Product Price": product_price,
        "Shipping Mode": shipping_mode,
    }


def main():
    rows = [build_row(i) for i in range(N_ROWS)]
    df = pd.DataFrame(rows)

    # Inject a small amount of realistic messiness for the cleaning step to handle
    dirty_idx = RNG.choice(df.index, size=int(N_ROWS * 0.015), replace=False)
    df.loc[dirty_idx, "Days for shipping (real)"] = np.nan
    dirty_idx2 = RNG.choice(df.index, size=int(N_ROWS * 0.01), replace=False)
    df.loc[dirty_idx2, "Customer Zipcode"] = np.nan
    dup_rows = df.sample(n=25, random_state=1)
    df = pd.concat([df, dup_rows], ignore_index=True)

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT_PATH, index=False)
    print(f"Sample dataset written: {OUT_PATH}  ({len(df)} rows, {df.shape[1]} columns)")


if __name__ == "__main__":
    main()
