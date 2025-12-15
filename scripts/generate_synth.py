import pandas as pd
import numpy as np
from datetime import datetime, timezone

# ---------- CONFIG ----------
INPUT_PATH = "../data/raw/products_macro.csv"
OUTPUT_PATH = "../data/synth/products_macro_synth.csv"

SEED = 42
rng = np.random.default_rng(SEED)

# Random percentage of products that will have a discount (per execution)
DISCOUNT_RATE = rng.uniform(0.10, 0.30)

# Discount percentage range (5%–35%)
DISC_MIN = 0.05
DISC_MAX = 0.35

# Small price jitter to avoid identical prices (±1%)
PRICE_JITTER = 0.01
# ---------------------------

print(f"Using discount rate: {DISCOUNT_RATE:.1%}")

df = pd.read_csv(INPUT_PATH)

# ---------- Helper functions ----------

def parse_eur_text(x):
    """
    Convert price text like:
    '€ 3,45', '3,45', '3.45' -> float
    """
    if pd.isna(x):
        return np.nan
    s = str(x).strip()
    s = s.replace("€", "").replace("\u20ac", "").strip()
    s = s.replace(",", ".")
    s = "".join(ch for ch in s if ch.isdigit() or ch == ".")
    return float(s) if s else np.nan


def format_eur(x):
    """
    Convert float -> European price format text (e.g. '€ 3,45')
    """
    if pd.isna(x):
        return np.nan
    return f"€ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# ---------- Synthetic logic ----------

# Parse original price text to numeric
price_num = df["price"].apply(parse_eur_text)

# Apply small random jitter to prices
jitter = rng.uniform(-PRICE_JITTER, PRICE_JITTER, size=len(df))
price_synth = (price_num * (1 + jitter)).clip(lower=0.01)

# Decide randomly which rows will have a discount
has_discount = rng.random(len(df)) < DISCOUNT_RATE

# Random discount percentage per row
discount_pct = rng.uniform(DISC_MIN, DISC_MAX, size=len(df))

# Compute discounted price
discount_price_num = np.where(
    has_discount,
    price_synth * (1 - discount_pct),
    np.nan
)

# Round to 2 decimals
price_synth = np.round(price_synth, 2)
discount_price_num = np.round(discount_price_num, 2)

# ---------- Overwrite ONLY existing columns ----------

# Keep same column names and formats as original dataset
df["price"] = price_synth.apply(format_eur)
df["discount_price"] = pd.Series(discount_price_num).apply(format_eur)

# Optional: snapshot timestamp (ONLY if it already exists in original schema)
if "snapshot_utc" in df.columns:
    df["snapshot_utc"] = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

# ---------- Save ----------
df.to_csv(OUTPUT_PATH, index=False)

print(f"✅ Saved synthetic dataset: {OUTPUT_PATH}")
print(f"Rows: {len(df)}")
print(f"Discounted rows: {has_discount.sum()} ({has_discount.mean():.1%})")
print(
    "Average discount (discounted only): "
    f"{np.nanmean((price_synth - discount_price_num) / price_synth):.1%}"
)
