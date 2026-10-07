import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from streamlit_autorefresh import st_autorefresh

from core.kafka_sim import broker_stats, start_producer
from core.config import KAFKA_TOPIC
from core.database import init_db, fetch_recent

st.set_page_config(page_title="Pipeline Health", page_icon="🔄", layout="wide")
st_autorefresh(interval=2000, key="pipe_refresh")
init_db()
start_producer(KAFKA_TOPIC, interval=0.4)

stats = broker_stats()
df = fetch_recent(2000)

st.title("Pipeline Health & Streaming")
st.caption("Kafka-style producer/consumer telemetry")
st.markdown("---")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Messages Sent", stats["messages_sent"])
c2.metric("Messages Consumed", stats["messages_consumed"])
c3.metric("Consumer Lag", stats["lag"])
c4.metric("DB Records", len(df))

st.markdown("---")
st.subheader("Architecture")
fig = go.Figure()
nodes = [
    ("Producer", 0, 0),
    ("Broker/Queue", 1, 0),
    ("Consumer", 2, 0),
    ("DB (SQLite)", 3, 0),
    ("ML Pipeline", 3, -1),
    ("Dashboard", 3, 1),
]
for name, x, y in nodes:
    fig.add_trace(go.Scatter(
        x=[x], y=[y], mode="markers+text",
        text=[name], textposition="middle center",
        marker=dict(size=80, color="#00d4ff", opacity=0.3,
                    line=dict(width=2, color="#00d4ff")),
        showlegend=False, hoverinfo="text",
    ))
for a, b in [(0, 1), (1, 2), (2, 3), (3, 4), (3, 5)]:
    fig.add_trace(go.Scatter(
        x=[nodes[a][1], nodes[b][1]], y=[nodes[a][2], nodes[b][2]],
        mode="lines", line=dict(color="#00d4ff", width=2),
        showlegend=False, hoverinfo="skip",
    ))
fig.update_xaxes(visible=False)
fig.update_yaxes(visible=False)
fig.update_layout(height=280, margin=dict(l=0, r=0, t=10, b=10),
                  plot_bgcolor="rgba(0,0,0,0)")
st.plotly_chart(fig, width='stretch')

st.markdown("---")
st.subheader("Stream Rate (last 60 events)")
if not df.empty:
    ts = df.sort_values("timestamp").tail(60).copy()
    ts["timestamp"] = pd.to_datetime(ts["timestamp"])
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=ts["timestamp"], y=ts["revenue"],
                              mode="markers+lines", name="Revenue"))
    fig2.update_layout(height=300, margin=dict(l=0, r=0, t=10, b=0))
    st.plotly_chart(fig2, width='stretch')

