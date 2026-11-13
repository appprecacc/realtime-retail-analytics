"""Reusable analytics layer for the dashboard and command-line report."""
from __future__ import annotations
from pathlib import Path
from typing import Union
import pandas as pd

def load_transactions(path: Union[str, Path]) -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=["timestamp"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    df["revenue"] = pd.to_numeric(df["revenue"], errors="coerce").fillna(0)
    return df.dropna(subset=["transaction_id", "timestamp"])

def completed(df: pd.DataFrame) -> pd.DataFrame:
    return df.loc[df["status"].eq("Completed")].copy()

def kpis(df: pd.DataFrame) -> dict[str, float | int]:
    data = completed(df); revenue = data["revenue"].sum(); orders = len(data)
    return {"revenue": float(revenue), "orders": orders,
            "average_order_value": float(revenue / orders) if orders else 0.0,
            "customers": int(data["customer_id"].nunique()),
            "refund_rate": float((df["status"] == "Refunded").mean() * 100)}

def daily_summary(df: pd.DataFrame) -> pd.DataFrame:
    data = completed(df).copy(); data["date"] = data["timestamp"].dt.date
    return data.groupby("date", as_index=False).agg(revenue=("revenue", "sum"), orders=("transaction_id", "count"))

def revenue_by(df: pd.DataFrame, column: str) -> pd.DataFrame:
    return completed(df).groupby(column, as_index=False)["revenue"].sum().sort_values("revenue", ascending=False)

def detect_hourly_anomalies(df: pd.DataFrame, z_threshold: float = 2.5) -> pd.DataFrame:
    data = completed(df).set_index("timestamp").sort_index()
    hourly = data["revenue"].resample("h").sum().rename("revenue").reset_index()
    std = hourly["revenue"].std(ddof=0)
    hourly["z_score"] = 0.0 if std == 0 else (hourly["revenue"] - hourly["revenue"].mean()) / std
    hourly["is_anomaly"] = hourly["z_score"].abs() >= z_threshold
    return hourly
