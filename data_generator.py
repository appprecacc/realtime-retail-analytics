"""Generate a realistic, streaming-style retail transaction feed."""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import argparse
import numpy as np
import pandas as pd

RNG = np.random.default_rng(42)
CITIES = ["Bengaluru", "Mumbai", "Delhi", "Hyderabad", "Chennai", "Pune"]
CHANNELS = ["Web", "Mobile App", "Store"]
CATEGORIES = ["Electronics", "Home", "Fashion", "Grocery", "Beauty"]
BASE_PRICE = {"Electronics": 1850, "Home": 920, "Fashion": 720, "Grocery": 380, "Beauty": 560}

def make_transactions(count: int, end: datetime | None = None) -> pd.DataFrame:
    """Create transactions distributed across the preceding seven days."""
    end = end or datetime.now(timezone.utc)
    timestamps = end - pd.to_timedelta(RNG.uniform(0, 7 * 24 * 60, count), unit="m")
    category = RNG.choice(CATEGORIES, count, p=[.16, .18, .25, .25, .16])
    channel = RNG.choice(CHANNELS, count, p=[.36, .42, .22])
    units = RNG.integers(1, 5, count)
    price = np.array([BASE_PRICE[x] for x in category]) * RNG.lognormal(0, .24, count)
    discount = RNG.choice([0, .05, .10, .15, .20], count, p=[.32, .22, .25, .14, .07])
    status = RNG.choice(["Completed", "Refunded", "Cancelled"], count, p=[.955, .028, .017])
    return pd.DataFrame({
        "transaction_id": [f"TXN-{RNG.integers(10**10, 10**11 - 1)}" for _ in range(count)],
        "timestamp": pd.to_datetime(timestamps, utc=True),
        "customer_id": [f"CUST-{RNG.integers(10000, 99999)}" for _ in range(count)],
        "city": RNG.choice(CITIES, count), "channel": channel, "category": category,
        "units": units, "unit_price": np.round(price, 2), "discount_pct": discount,
        "revenue": np.round(units * price * (1 - discount), 2), "status": status,
    }).sort_values("timestamp")

def append_feed(path: Path, count: int) -> int:
    rows = make_transactions(count)
    path.parent.mkdir(parents=True, exist_ok=True)
    rows.to_csv(path, mode="a", header=not path.exists(), index=False)
    return len(rows)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Append simulated retail transactions to a CSV feed.")
    parser.add_argument("--rows", type=int, default=120)
    parser.add_argument("--output", default="data/transactions.csv")
    args = parser.parse_args()
    print(f"Appended {append_feed(Path(args.output), args.rows)} transactions to {args.output}")
