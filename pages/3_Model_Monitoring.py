import streamlit as st
import plotly.express as px
import pandas as pd
from streamlit_autorefresh import st_autorefresh

from core.database import init_db, fetch_recent
from core.ml_pipeline import (
    clean_and_enrich, predict_churn,
    MODEL_METRICS, FEATURE_IMPORTANCE, MODEL_VERSION,
)

st.set_page_config(page_title="Model Monitoring", page_icon="🤖", layout="wide")
st_autorefresh(interval=4000, key="model_refresh")
init_db()

df = clean_and_enrich(fetch_recent(1000))
df = predict_churn(df)

st.title("Model Monitoring")
st.caption(f"Live inference telemetry — Model {MODEL_VERSION}")
st.markdown("---")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Accuracy", f"{MODEL_METRICS['accuracy']*100:.1f}%")
c2.metric("Precision", f"{MODEL_METRICS['precision']*100:.1f}%")
c3.metric("Recall", f"{MODEL_METRICS['recall']*100:.1f}%")
c4.metric("F1", f"{MODEL_METRICS['f1']*100:.1f}%")

st.markdown("---")
left, right = st.columns(2)

with left:
    st.subheader("Feature Importance")
    fi = FEATURE_IMPORTANCE.reset_index()
    fi.columns = ["feature", "importance"]
    fig = px.bar(fi, x="importance", y="feature", orientation="h",
                 color="importance", color_continuous_scale="Viridis")
    fig.update_layout(height=340, margin=dict(l=0, r=0, t=10, b=0))
    st.plotly_chart(fig, width='stretch')

with right:
    st.subheader("Churn Probability Distribution")
    if not df.empty:
        fig = px.histogram(df, x="churn_probability", nbins=30,
                           color="prediction",
                           color_discrete_map={"High Risk": "#ef553b", "Safe": "#00cc96"})
        fig.update_layout(height=340, margin=dict(l=0, r=0, t=10, b=0))
        st.plotly_chart(fig, width='stretch')
    else:
        st.info("No predictions yet.")

st.markdown("---")
st.subheader("High-Risk Customers (Top 15)")
if not df.empty:
    high = df[df["prediction"] == "High Risk"].sort_values(
        "churn_probability", ascending=False
    ).head(15)
    st.dataframe(
        high[["timestamp", "customer_id", "country", "product",
              "session_duration", "pages_viewed", "churn_probability"]],
        width='stretch', hide_index=True,
    )
else:
    st.info("Waiting for predictions...")

st.markdown("---")
st.subheader("Prediction Rate Over Time")
if not df.empty:
    ts = df.sort_values("timestamp").copy()
    ts["minute"] = pd.to_datetime(ts["timestamp"]).dt.floor("min")
    rate = ts.groupby(["minute", "prediction"]).size().reset_index(name="count")
    fig = px.area(rate, x="minute", y="count", color="prediction",
                  color_discrete_map={"High Risk": "#ef553b", "Safe": "#00cc96"})
    fig.update_layout(height=320, margin=dict(l=0, r=0, t=10, b=0))
    st.plotly_chart(fig, width='stretch')

