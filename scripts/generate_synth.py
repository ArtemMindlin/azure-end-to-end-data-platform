import os
import pandas as pd
import numpy as np
from datetime import timezone

# -----------------------------
# CONFIG
# -----------------------------
INPUT_PATH = "../data/raw/products_macro.csv"
OUTPUT_PATH = "../data/synth/products_macro_synth.csv"

SEED = 42
rng = np.random.default_rng(SEED)

# Time range (monthly snapshots)
START_YEAR = 2005
START_MONTH = 1
N_YEARS = 20
FREQ = "MS"  # Month Start

# Price dynamics
ANNUAL_INFLATION_MEAN = 0.02  # 2% avg yearly drift
ANNUAL_INFLATION_STD = 0.01  # macro drift variability
PRODUCT_MONTHLY_VOL = 0.015  # monthly product-specific random walk volatility (1.5%)
CATEGORY_SEASONALITY_AMP = 0.03  # +/-3% seasonal amplitude (category-level)

# Discount dynamics
DISCOUNT_RATE_MIN = 0.08  # min proportion discounted each month
DISCOUNT_RATE_MAX = 0.25  # max proportion discounted each month
DISC_MIN = 0.05  # 5% min discount
DISC_MAX = 0.35  # 35% max discount

# Seasonal multiplier for discount probability by month
DISCOUNT_MONTH_MULT = {
    1: 0.95,
    2: 0.95,
    3: 1.00,
    4: 1.00,
    5: 1.00,
    6: 0.90,
    7: 0.85,
    8: 0.85,
    9: 1.00,
    10: 1.05,
    11: 1.35,
    12: 1.25,
}

# Formatting
CURRENCY_SYMBOL = "€"
DECIMALS = 2

COL_ID = "id"
COL_CATEGORY = "Category"
COL_NAME = "name"
COL_SUBTITLE = "subtitle"
COL_PRICE = "price"
COL_DISCOUNT = "discount_price"
COL_MAIN_IMAGE = "main_image_url"
COL_SECONNDARY_IMAGE = "secondary_image_url"
COL_NUTRITIONAL_INFO = "nutritional_info"

SNAPSHOT_COL = "snapshot_utc"


# -----------------------------
# HELPERS
# -----------------------------
def parse_eur_text(x):
    """Convert '€ 3,45' / '3,45' / '3.45' to float. Returns np.nan if empty."""
    if pd.isna(x):
        return np.nan
    s = str(x).strip()
    s = s.replace(CURRENCY_SYMBOL, "").replace("\u20ac", "").strip()
    s = s.replace(",", ".")
    s = "".join(ch for ch in s if ch.isdigit() or ch == ".")
    return float(s) if s else np.nan


def format_eur(x):
    """Format float as euro text, e.g. '€ 3,45'. Returns None if nan."""
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return None
    val = round(float(x), DECIMALS)
    s = f"{val:.{DECIMALS}f}".replace(".", ",")
    return f"{CURRENCY_SYMBOL} {s}"


# -----------------------------
# MAIN
# -----------------------------
def main():
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

    df0 = pd.read_csv(INPUT_PATH)
    original_cols = list(df0.columns)

    # Base price from the original 'price' column
    base_price = df0[COL_PRICE].apply(parse_eur_text).astype(float)

    base_price = base_price.clip(lower=0.10)
    base_price_vec = base_price.to_numpy()
    n_products = len(df0)

    # Snapshot dates (monthly)
    start = pd.Timestamp(year=START_YEAR, month=START_MONTH, day=1)
    periods = N_YEARS * 12
    dates = pd.date_range(start=start, periods=periods, freq=FREQ)

    # Macro inflation path (monthly)
    annual_draw = rng.normal(ANNUAL_INFLATION_MEAN, ANNUAL_INFLATION_STD, size=periods)
    monthly_drift = (1.0 + annual_draw) ** (1.0 / 12.0) - 1.0
    macro_multiplier = np.cumprod(1.0 + monthly_drift)

    # Product-specific random walk
    product_shocks = rng.normal(0.0, PRODUCT_MONTHLY_VOL, size=(periods, n_products))
    product_multiplier = np.cumprod(1.0 + product_shocks, axis=0)

    # Category seasonality: each category gets random phase
    categories = df0[COL_CATEGORY].astype(str)
    unique_cats = categories.unique()
    cat_phase = {cat: rng.uniform(0, 2 * np.pi) for cat in unique_cats}
    phases = np.array([cat_phase[c] for c in categories])

    seasonal = np.zeros((periods, n_products), dtype=float)
    for t, d in enumerate(dates):
        angle_base = 2 * np.pi * (d.month - 1) / 12.0
        seasonal[t, :] = 1.0 + CATEGORY_SEASONALITY_AMP * np.sin(angle_base + phases)

    # Synthetic numeric price per month/product
    price_num = (
        base_price_vec[None, :]
        * macro_multiplier[:, None]
        * product_multiplier
        * seasonal
    ).clip(min=0.10)

    # Discount rate per month (random each run)
    discount_rate_base = rng.uniform(DISCOUNT_RATE_MIN, DISCOUNT_RATE_MAX, size=periods)
    discount_rate = np.clip(
        np.array(
            [
                discount_rate_base[t] * DISCOUNT_MONTH_MULT.get(dates[t].month, 1.0)
                for t in range(periods)
            ]
        ),
        0.0,
        0.95,
    )

    # Decide discounts per month/product
    has_discount = rng.random((periods, n_products)) < discount_rate[:, None]
    disc_pct = rng.uniform(DISC_MIN, DISC_MAX, size=(periods, n_products))

    discount_price_num = np.where(
        has_discount, price_num * (1.0 - disc_pct), np.nan
    ).clip(min=0.10)

    # Round
    price_num = np.round(price_num, DECIMALS)
    discount_price_num = np.round(discount_price_num, DECIMALS)

    # Build long dataset (append snapshots)
    chunks = []
    for t in range(periods):
        snap_dt = dates[t].to_pydatetime().replace(tzinfo=timezone.utc)
        snap_str = snap_dt.strftime("%Y-%m-%d %H:%M:%S")

        chunk = df0.copy()
        chunk[COL_PRICE] = [format_eur(x) for x in price_num[t, :]]
        chunk[COL_DISCOUNT] = [format_eur(x) for x in discount_price_num[t, :]]
        chunk[SNAPSHOT_COL] = snap_str

        chunks.append(chunk)

    out = pd.concat(chunks, ignore_index=True)

    # Keep original columns first, then snapshot_utc
    final_cols = original_cols + (
        [SNAPSHOT_COL] if SNAPSHOT_COL not in original_cols else []
    )
    out = out[final_cols]

    out.to_csv(OUTPUT_PATH, index=False)

    # Quick stats
    total_rows = len(out)
    discounted_rows = out[COL_DISCOUNT].notna().sum()
    print(f"✅ Saved: {OUTPUT_PATH}")
    print(f"Rows: {total_rows} (products={n_products}, months={periods})")
    print(f"Discounted rows: {discounted_rows} ({discounted_rows/total_rows:.1%})")
    print(f"Snapshots: {dates[0].strftime('%Y-%m')} .. {dates[-1].strftime('%Y-%m')}")


if __name__ == "__main__":
    main()
