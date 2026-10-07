import streamlit as st
from streamlit_autorefresh import st_autorefresh

from core.database import init_db, fetch_recent
from core.ml_pipeline import clean_and_enrich, predict_churn
from core.ai_insights import generate_insights
from core.config import USE_LLM, LLM_PROVIDER, OPENAI_MODEL

st.set_page_config(page_title="AI Insights", page_icon="🧠", layout="wide")
st_autorefresh(interval=15000, key="ai_refresh")
init_db()

df = clean_and_enrich(fetch_recent(1000))
df = predict_churn(df)

st.title("AI-Generated Insights")

if USE_LLM and LLM_PROVIDER == "groq":
    mode = f"Groq — {OPENAI_MODEL}"
elif USE_LLM and LLM_PROVIDER == "openai":
    mode = f"OpenAI — {OPENAI_MODEL}"
else:
    mode = "Rule-based (offline)"

st.caption(f"Engine: **{mode}** | Refresh every 15s")
st.markdown("---")

if df.empty:
    st.warning("Waiting for data...")
    st.stop()

with st.spinner("AI is analyzing the latest data..."):
    insights = generate_insights(df)

for i, insight in enumerate(insights, 1):
    st.markdown(f"**{i}.** {insight}")

st.markdown("---")
st.subheader("Snapshot Summary")
c1, c2, c3 = st.columns(3)
c1.metric("Revenue", f"${df['revenue'].sum():,.0f}")
c2.metric("Top Country", df.groupby('country')['revenue'].sum().idxmax())
c3.metric("Top Product", df.groupby('product')['revenue'].sum().idxmax())

with st.expander("Raw stats used for AI reasoning"):
    st.dataframe(df.describe().round(2), width='stretch')

