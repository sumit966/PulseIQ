import streamlit as st
from core.database import init_db

st.set_page_config(
    page_title="PulseIQ — Real-Time AI Analytics",
    page_icon="⚡",
    layout="wide",
)

init_db()

st.title("PulseIQ")
st.subheader("Real-Time AI Analytics Platform")

st.markdown("""
**PulseIQ** is an enterprise-grade prototype demonstrating:

- **Streaming pipeline** — simulated Kafka producer/consumer
- **Data quality monitoring** — completeness, invalids, drift
- **ML inference** — live churn prediction (Random Forest)
- **AI insights** — LLM-generated narrative summaries via Groq
- **Live dashboards** — auto-refreshing KPIs and charts
- **Pipeline telemetry** — broker lag, throughput, message counts

### Use the sidebar to navigate pages
""")

c1, c2, c3 = st.columns(3)
c1.metric("Modules", "5")
c2.metric("Pipeline Layers", "4")
c3.metric("Refresh Rate", "2 sec")

st.info("All data is synthetic. LLM insights powered by Groq (free tier).")

