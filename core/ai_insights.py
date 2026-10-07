from typing import List
import pandas as pd
from core.config import (
    USE_LLM, LLM_PROVIDER,
    GROQ_API_KEY, OPENAI_API_KEY, OPENAI_MODEL,
)


def _rule_based_insights(df: pd.DataFrame) -> List[str]:
    if df.empty:
        return ["Waiting for data stream..."]
    insights = []
    avg_rev = df["revenue"].mean()
    high_churn = (df["prediction"] == "High Risk").mean() * 100
    top_country = df.groupby("country")["revenue"].sum().idxmax()
    top_product = df.groupby("product")["revenue"].sum().idxmax()

    insights.append(f"Average revenue per order: **${avg_rev:.2f}**")
    insights.append(f"High-risk churn customers: **{high_churn:.1f}%**")
    insights.append(f"Top market: **{top_country}**")
    insights.append(f"Best-selling product: **{top_product}**")

    recent = df.sort_values("timestamp").tail(30)["revenue"]
    if len(recent) > 5 and recent.std() > 0:
        z = (recent.iloc[-1] - recent.mean()) / recent.std()
        if abs(z) > 2:
            insights.append(f"Anomaly detected in latest revenue (z={z:.2f})")
    return insights


def _build_prompt(df: pd.DataFrame) -> str:
    summary = df.describe(include="all").to_string()[:3000]
    head = df.sort_values("timestamp", ascending=False).head(15).to_string()[:2000]
    return f"""You are a senior data analyst. Analyze this real-time e-commerce data
and return exactly 5 bullet insights for a business dashboard.

STATS:
{summary}

RECENT EVENTS:
{head}

Return 5 lines. Each line format: emoji + short title + one-sentence explanation.
Max 25 words per line. Focus on: trends, anomalies, churn risk, top revenue drivers."""


def _extract_content(msg) -> str:
    """Groq reasoning models put output in .content, fallback to .reasoning."""
    content = getattr(msg, "content", None)
    if content:
        return content
    reasoning = getattr(msg, "reasoning", None)
    return reasoning or ""


def _groq_insights(df: pd.DataFrame) -> List[str]:
    from groq import Groq
    client = Groq(api_key=GROQ_API_KEY)
    resp = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[{"role": "user", "content": _build_prompt(df)}],
        temperature=0.4,
        max_tokens=500,
    )
    text = _extract_content(resp.choices[0].message).strip()
    lines = [l.strip("-*• ").strip() for l in text.split("\n") if l.strip()]
    # keep only meaningful insight lines
    return [l for l in lines if len(l) > 15][:6] or _rule_based_insights(df)


def _openai_insights(df: pd.DataFrame) -> List[str]:
    from openai import OpenAI
    client = OpenAI(api_key=OPENAI_API_KEY)
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": _build_prompt(df)}],
        temperature=0.4, max_tokens=500,
    )
    text = resp.choices[0].message.content.strip()
    lines = [l.strip("-*• ").strip() for l in text.split("\n") if l.strip()]
    return [l for l in lines if len(l) > 15][:6]


def generate_insights(df: pd.DataFrame) -> List[str]:
    if not USE_LLM:
        return _rule_based_insights(df)
    try:
        if LLM_PROVIDER == "groq" and GROQ_API_KEY:
            return _groq_insights(df)
        if LLM_PROVIDER == "openai" and OPENAI_API_KEY:
            return _openai_insights(df)
    except Exception as e:
        return [f"LLM error: {e}"] + _rule_based_insights(df)
    return _rule_based_insights(df)

