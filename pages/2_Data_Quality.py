import streamlit as st
import plotly.express as px
from streamlit_autorefresh import st_autorefresh

from core.database import init_db, fetch_recent
from core.ml_pipeline import clean_and_enrich

st.set_page_config(page_title="Data Quality", page_icon="", layout="wide")
st_autorefresh(interval=3000, key="dq_refresh")
init_db()

df = clean_and_enrich(fetch_recent(1000))

st.title("Data Quality Monitor")
st.caption("Real-time integrity, completeness and anomaly checks")
st.markdown("---")

if df.empty:
    st.warning("No data yet.")
    st.stop()

total = len(df)
missing = int(df["dq_missing"].sum())
negatives = int(df["dq_negative"].sum())
dupes = int(df.duplicated(subset=["timestamp", "customer_id", "product"]).sum())
quality_score = round((1 - (missing + negatives + dupes) / total) * 100, 2)

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Records", total)
c2.metric("Missing", missing)
c3.metric("Invalid", negatives)
c4.metric("Duplicates", dupes)
c5.metric("Quality Score", f"{quality_score}%")

st.markdown("---")
left, right = st.columns(2)

with left:
    st.subheader("Completeness by Column")
    comp = (df.notna().mean() * 100).round(2).reset_index()
    comp.columns = ["column", "complete_pct"]
    fig = px.bar(comp, x="column", y="complete_pct",
                 color="complete_pct", color_continuous_scale="Teal")
    fig.update_layout(height=350, margin=dict(l=0, r=0, t=10, b=0))
    st.plotly_chart(fig, use_container_width=True)

with right:
    st.subheader("Revenue Distribution")
    fig = px.histogram(df, x="revenue", nbins=40, color="country")
    fig.update_layout(height=350, margin=dict(l=0, r=0, t=10, b=0))
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.subheader("Anomaly Injection (Ground Truth)")
anom_rate = df["injected_anomaly"].mean() * 100
st.metric("Injected anomalies", f"{anom_rate:.2f}%")

recent = df.sort_values("timestamp").tail(60).copy()
recent["rolling_mean"] = recent["revenue"].rolling(5, min_periods=1).mean()
fig = px.line(recent, x="timestamp", y=["revenue", "rolling_mean"],
              title="Revenue vs Rolling Mean")
fig.update_layout(height=340, margin=dict(l=0, r=0, t=30, b=0))
st.plotly_chart(fig, use_container_width=True)
