"""Terminal report for scheduled analytics checks."""
from pathlib import Path
from analytics import load_transactions, kpis, revenue_by, detect_hourly_anomalies
df = load_transactions(Path(__file__).parent / "data" / "transactions.csv")
m = kpis(df)
print("RETAIL PULSE — CURRENT SNAPSHOT")
print(f"Revenue: ₹{m['revenue']:,.2f} | Orders: {m['orders']:,} | AOV: ₹{m['average_order_value']:,.2f}")
print(f"Customers: {m['customers']:,} | Refund rate: {m['refund_rate']:.2f}%")
print("\nTop categories:\n" + revenue_by(df, "category").head(3).to_string(index=False))
print(f"\nAnomalous hours: {int(detect_hourly_anomalies(df).is_anomaly.sum())}")
