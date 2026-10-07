from core.database import init_db, insert_events, fetch_recent
from core.data_generator import generate_event
from core.ml_pipeline import clean_and_enrich, predict_churn
from core.ai_insights import generate_insights

init_db()
insert_events([generate_event() for _ in range(30)])
df = predict_churn(clean_and_enrich(fetch_recent(50)))

print(f"Rows: {len(df)}")
high_risk = (df["prediction"] == "High Risk").sum()
print(f"High-risk: {high_risk}")
print("Insights:")
for i in generate_insights(df)[:5]:
    print(f"  - {i}")
