import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score


MODEL_VERSION = "v1.0.0"


def clean_and_enrich(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    df = df.copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df["revenue"] = pd.to_numeric(df["revenue"], errors="coerce").fillna(0.0)
    df["unit_price"] = pd.to_numeric(df["unit_price"], errors="coerce").fillna(0.0)
    df["churn_probability"] = pd.to_numeric(
        df["churn_probability"], errors="coerce"
    ).fillna(0.0)
    df["prediction"] = df["prediction"].fillna("Pending").astype(str)
    df["model_version"] = df["model_version"].fillna("").astype(str)
    df["engagement_score"] = (
        df["session_duration"] / 60 + df["pages_viewed"]
    ).round(2)
    df["dq_missing"] = df[["country", "product", "unit_price"]].isna().any(axis=1)
    df["dq_negative"] = (df["revenue"] < 0) | (df["quantity"] < 0)
    for col in ["country", "product", "channel"]:
        if col in df.columns:
            df[col] = df[col].fillna("Unknown").astype(str)
    return df


def train_churn_model():
    np.random.seed(42)
    n = 3000
    X = pd.DataFrame({
        "session_duration": np.random.randint(10, 600, n),
        "pages_viewed": np.random.randint(1, 30, n),
        "is_returning": np.random.randint(0, 2, n),
        "quantity": np.random.randint(1, 5, n),
    })
    y = ((X["session_duration"] < 120) & (X["pages_viewed"] < 6)).astype(int)
    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, random_state=1)
    model = RandomForestClassifier(n_estimators=80, random_state=42)
    model.fit(X_tr, y_tr)
    preds = model.predict(X_te)
    metrics = {
        "accuracy": round(accuracy_score(y_te, preds), 3),
        "precision": round(precision_score(y_te, preds, zero_division=0), 3),
        "recall": round(recall_score(y_te, preds, zero_division=0), 3),
        "f1": round(f1_score(y_te, preds, zero_division=0), 3),
    }
    return model, metrics


CHURN_MODEL, MODEL_METRICS = train_churn_model()
FEATURE_IMPORTANCE = pd.Series(
    CHURN_MODEL.feature_importances_,
    index=["session_duration", "pages_viewed", "is_returning", "quantity"]
).sort_values(ascending=False)


def predict_churn(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    df = df.copy()
    feats = df[["session_duration", "pages_viewed", "is_returning", "quantity"]]
    probs = CHURN_MODEL.predict_proba(feats)[:, 1]
    df["churn_probability"] = probs.round(3)
    df["prediction"] = np.where(probs > 0.5, "High Risk", "Safe")
    df["model_version"] = MODEL_VERSION
    return df
