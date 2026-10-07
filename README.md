# PulseIQ — Real-Time AI Analytics Platform

Real-time AI analytics prototype: streaming pipeline to live dashboard.

## Features

* Fake Kafka producer/consumer with broker lag telemetry
* Live dashboard with auto-refreshing KPIs (2s)
* Data quality monitoring (completeness, invalids, anomalies)
* ML model monitoring with live churn predictions
* AI insight engine powered by Groq (openai/gpt-oss-20b)
* Pipeline health with architecture diagram

## Tech Stack

Streamlit, Plotly, SQLite, Scikit-learn, Groq API, Docker, GitHub Actions

## Quick Start

pip install -r requirements.txt
streamlit run app.py

Open http://localhost:8501

## Configuration (.env)

USE\_LLM=true
LLM\_PROVIDER=groq
GROQ\_API\_KEY=your\_key
OPENAI\_MODEL=openai/gpt-oss-20b

Free key: https://console.groq.com/keys

## Docker

docker compose up --build

## License

MIT



