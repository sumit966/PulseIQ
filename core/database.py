import os
import sqlite3
import pandas as pd
from core.config import DB_PATH

os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)


def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            customer_id INTEGER,
            country TEXT,
            product TEXT,
            channel TEXT,
            quantity INTEGER,
            unit_price REAL,
            session_duration INTEGER,
            pages_viewed INTEGER,
            is_returning INTEGER,
            revenue REAL,
            injected_anomaly INTEGER,
            churn_probability REAL,
            prediction TEXT,
            model_version TEXT
        )
    """)
    conn.commit()
    conn.close()


def insert_events(events):
    """Insert events, safely handling missing churn fields."""
    if not events:
        return

    rows = []
    for e in events:
        rows.append({
            "timestamp": e.get("timestamp"),
            "customer_id": e.get("customer_id"),
            "country": e.get("country"),
            "product": e.get("product"),
            "channel": e.get("channel"),
            "quantity": e.get("quantity"),
            "unit_price": e.get("unit_price"),
            "session_duration": e.get("session_duration"),
            "pages_viewed": e.get("pages_viewed"),
            "is_returning": e.get("is_returning"),
            "revenue": e.get("revenue"),
            "injected_anomaly": e.get("injected_anomaly", 0),
            "churn_probability": e.get("churn_probability"),
            "prediction": e.get("prediction"),
            "model_version": e.get("model_version"),
        })

    conn = sqlite3.connect(DB_PATH)
    conn.executemany("""
        INSERT INTO events (timestamp, customer_id, country, product, channel,
            quantity, unit_price, session_duration, pages_viewed, is_returning,
            revenue, injected_anomaly, churn_probability, prediction, model_version)
        VALUES (:timestamp, :customer_id, :country, :product, :channel,
                :quantity, :unit_price, :session_duration, :pages_viewed,
                :is_returning, :revenue, :injected_anomaly, :churn_probability,
                :prediction, :model_version)
    """, rows)
    conn.commit()
    conn.close()


def fetch_recent(limit=2000):
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql(f"SELECT * FROM events ORDER BY id DESC LIMIT {limit}", conn)
    conn.close()
    return df
