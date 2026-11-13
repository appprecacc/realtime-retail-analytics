# Retail Pulse: real-time retail analytics

This end-to-end portfolio project simulates an incoming e-commerce transaction feed, computes business KPIs with **pandas** and **NumPy**, detects unusual hourly revenue, and presents it in a **Streamlit + Plotly** dashboard.

## Run it

```bash
cd realtime_retail_analytics
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
python data_generator.py --rows 1500
streamlit run dashboard.py
```

To mimic fresh events arriving, run this in a second terminal and refresh the dashboard:

```bash
python data_generator.py --rows 100
```

For a scheduler-friendly terminal report, run `python report.py`.

## Production direction

Replace the CSV event feed with Kafka, an API, object storage, or a database. Schedule `report.py`, send anomalies to your alerting channel, and store credentials in environment variables.
