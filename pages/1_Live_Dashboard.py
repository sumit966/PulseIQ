import streamlit as st
import plotly.express as px
import pandas as pd
from streamlit_autorefresh import st_autorefresh

from core.kafka_sim import FakeKafkaConsumer, start_producer
from core.config import KAFKA_TOPIC
from core.database import init_db, insert_events, fetch_recent
from core.ml_pipeline import clean_and_enrich, predict_churn
from core.ai_insights import generate_insights

st.set_page_config(page_title="Live Dashboard", page_icon="📊", layout="wide")
st_autorefresh(interval=2000, key="dash_refresh")

init_db()
start_producer(KAFKA_TOPIC, interval=0.4)

consumer = FakeKafkaConsumer(KAFKA_TOPIC, group_id="dashboard")
events = consumer.poll(max_records=8)
insert_events(events)

df = fetch_recent(1000)
df = clean_and_enrich(df)
df = predict_churn(df)

st.title("Live Business Dashboard")
st.caption(f"Consumed this refresh: {len(events)} | Records in window: {len(df)}")
st.markdown("---")

if df.empty:
    st.warning("Waiting for first events...")
    st.stop()

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Revenue", f"${df['revenue'].sum():,.0f}")
c2.metric("Orders", len(df))
c3.metric("AOV", f"${df['revenue'].mean():.2f}")
c4.metric("Churn %", f"{(df['prediction']=='High Risk').mean()*100:.1f}%")
c5.metric("Customers", df["customer_id"].nunique())

st.markdown("---")
left, right = st.columns(2)

with left:
    st.subheader("Revenue Trend")
    trend = df.sort_values("timestamp").tail(120)
    fig = px.line(trend, x="timestamp", y="revenue", markers=True)
    fig.update_layout(height=340, margin=dict(l=0, r=0, t=10, b=0))
    st.plotly_chart(fig, width='stretch')

with right:
    st.subheader("Revenue by Country")
    by_country = df.groupby("country")["revenue"].sum().reset_index()
    fig = px.bar(by_country, x="country", y="revenue", color="country")
    fig.update_layout(height=340, margin=dict(l=0, r=0, t=10, b=0))
    st.plotly_chart(fig, width='stretch')

left, right = st.columns(2)
with left:
    st.subheader("Product Performance")
    prod = df.groupby("product").agg(
        revenue=("revenue", "sum"), orders=("revenue", "count")
    ).reset_index()
    fig = px.scatter(prod, x="orders", y="revenue", size="revenue",
                     color="product", hover_name="product")
    fig.update_layout(height=340, margin=dict(l=0, r=0, t=10, b=0))
    st.plotly_chart(fig, width='stretch')

with right:
    st.subheader("Churn Risk")
    churn = df["prediction"].value_counts().reset_index()
    churn.columns = ["status", "count"]
    fig = px.pie(churn, names="status", values="count", color="status",
                 color_discrete_map={"High Risk": "#ef553b", "Safe": "#00cc96"})
    fig.update_layout(height=340, margin=dict(l=0, r=0, t=10, b=0))
    st.plotly_chart(fig, width='stretch')

st.markdown("---")
st.subheader("AI-Generated Insights")
for insight in generate_insights(df):
    st.markdown(f"- {insight}")

st.markdown("---")
st.subheader("Live Event Stream")
st.dataframe(
    df.sort_values("id", ascending=False).head(10)[
        ["timestamp", "customer_id", "country", "product",
         "revenue", "churn_probability", "prediction"]
    ],
    width='stretch', hide_index=True,
)

