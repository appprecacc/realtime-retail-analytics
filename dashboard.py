"""Streamlit dashboard for near-real-time retail analytics."""
from pathlib import Path
import streamlit as st
import plotly.express as px
from analytics import load_transactions, kpis, daily_summary, revenue_by, detect_hourly_anomalies

st.set_page_config(page_title="Retail Pulse", page_icon="📈", layout="wide")
ROOT = Path(__file__).parent; DATA = ROOT / "data" / "transactions.csv"
st.title("Retail Pulse — Real-time Sales Analytics")
st.caption("Demo data is generated locally. Append events, then refresh the dashboard.")
if not DATA.exists():
    st.warning("Run `python data_generator.py --rows 1500` first."); st.stop()
df = load_transactions(DATA)
with st.sidebar:
    st.header("Filters")
    cities = st.multiselect("City", sorted(df.city.unique()), default=sorted(df.city.unique()))
    channels = st.multiselect("Channel", sorted(df.channel.unique()), default=sorted(df.channel.unique()))
    start, end = st.date_input("Date range", value=(df.timestamp.min().date(), df.timestamp.max().date()))
filtered = df[(df.city.isin(cities)) & (df.channel.isin(channels)) & (df.timestamp.dt.date >= start) & (df.timestamp.dt.date <= end)]
m = kpis(filtered); cols = st.columns(5)
for col, label, value in zip(cols, ["Revenue", "Completed orders", "Average order value", "Customers", "Refund rate"], [f"₹{m['revenue']:,.0f}", f"{m['orders']:,}", f"₹{m['average_order_value']:,.0f}", f"{m['customers']:,}", f"{m['refund_rate']:.1f}%"]): col.metric(label, value)
left, right = st.columns(2)
with left: st.plotly_chart(px.line(daily_summary(filtered), x="date", y="revenue", markers=True, title="Daily revenue"), use_container_width=True)
with right: st.plotly_chart(px.bar(revenue_by(filtered, "category"), x="category", y="revenue", title="Revenue by category"), use_container_width=True)
st.plotly_chart(px.bar(revenue_by(filtered, "city"), x="city", y="revenue", color="revenue", title="Revenue by city"), use_container_width=True)
anomalies = detect_hourly_anomalies(filtered); flagged = anomalies[anomalies.is_anomaly]
st.subheader("Revenue anomaly monitor")
st.plotly_chart(px.line(anomalies, x="timestamp", y="revenue", title="Hourly completed revenue"), use_container_width=True)
if len(flagged): st.warning(f"{len(flagged)} unusual hour(s) detected (|z-score| ≥ 2.5)."); st.dataframe(flagged[["timestamp", "revenue", "z_score"]], hide_index=True)
else: st.success("No unusual revenue hours in the selected data.")
st.subheader("Latest transactions"); st.dataframe(filtered.sort_values("timestamp", ascending=False).head(25), use_container_width=True, hide_index=True)
