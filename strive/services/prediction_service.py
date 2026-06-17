import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, accuracy_score, precision_score, recall_score, f1_score
from models import User, CheckIn, StreakMember, StreakGroup, Goal
from services.nlp_service import analyze_sentiment

_models = {}
_model_metrics = {}
_trained = False

def _extract_features(db: Session, user_id: int, checkin_date=None) -> dict:
    if checkin_date is None:
        checkin_date = datetime.utcnow()
    month_ago = checkin_date - timedelta(days=30)
    week_ago = checkin_date - timedelta(days=7)

    memberships = db.query(StreakMember).filter(StreakMember.user_id == user_id).all()
    group_ids = [m.streak_group_id for m in memberships]

    checkins = db.query(CheckIn).filter(
        CheckIn.user_id == user_id,
        CheckIn.created_at >= month_ago
    ).all()

    recent = [c for c in checkins if c.created_at >= week_ago]

    current_streak = max([m.current_streak for m in memberships], default=0)
    total_days_30 = 30
    days_checked_30 = len(set(c.created_at.date() for c in checkins if c.created_at >= month_ago))
    consistency_30 = round(days_checked_30 / total_days_30, 2)

    mood_scores = []
    struggling_count = 0
    for c in recent:
        s = c.sentiment
        if s == "motivated":
            mood_scores.append(1.0)
        elif s == "struggling":
            mood_scores.append(0.0)
            struggling_count += 1
        else:
            mood_scores.append(0.5)
    avg_mood = round(np.mean(mood_scores), 2) if mood_scores else 0.5
    struggling_rate = round(struggling_count / len(recent), 2) if recent else 0.0

    last_checkin = db.query(CheckIn).filter(
        CheckIn.user_id == user_id
    ).order_by(CheckIn.created_at.desc()).first()
    days_since = (checkin_date - last_checkin.created_at).days if last_checkin else 99

    group_size = len(memberships)

    checkins_this_week = len(recent)

    verified_count = sum(1 for c in checkins if c.verified)
    verified_rate = round(verified_count / len(checkins), 2) if checkins else 0.0

    return {
        "current_streak": current_streak,
        "consistency_30": consistency_30,
        "avg_mood_score": avg_mood,
        "struggling_rate": struggling_rate,
        "days_since_checkin": days_since,
        "group_size": group_size,
        "checkins_this_week": checkins_this_week,
        "verified_rate": verified_rate,
    }

def _generate_training_data(db: Session, n_samples: int = 2400) -> tuple:
    np.random.seed(42)
    users = db.query(User).all()
    if not users:
        return None, None

    rng = np.random.default_rng(42)
    rows = []
    labels = []
    for _ in range(n_samples):
        streak = rng.integers(0, 101)
        consistency = rng.uniform(0.0, 1.0)
        avg_mood = rng.uniform(0.0, 1.0)
        struggling_rate = rng.uniform(0.0, 1.0)
        days_since = rng.integers(0, 8)
        group_size = rng.integers(1, 12)
        checkins_wk = rng.integers(0, 8)
        verified_rate = rng.uniform(0.0, 1.0)

        low_streak = streak < 30
        low_consistency = consistency < 0.5
        low_mood = avg_mood < 0.4
        high_struggle = struggling_rate > 0.4
        long_gap = days_since > 3
        low_verified = verified_rate < 0.4
        risk_factors = sum([low_streak, low_consistency, low_mood, high_struggle, long_gap, low_verified])
        will_break = 1 if risk_factors >= 3 else 0

        rows.append([streak, consistency, avg_mood, struggling_rate,
                     days_since, group_size, checkins_wk, verified_rate])
        labels.append(will_break)

    X = pd.DataFrame(rows, columns=[
        "current_streak", "consistency_30", "avg_mood_score", "struggling_rate",
        "days_since_checkin", "group_size", "checkins_this_week", "verified_rate"
    ])
    y = pd.Series(labels)
    return X, y

FEATURE_NAMES = [
    "current_streak", "consistency_30", "avg_mood_score", "struggling_rate",
    "days_since_checkin", "group_size", "checkins_this_week", "verified_rate"
]

def train_models(db: Session):
    global _models, _model_metrics, _trained
    result = _generate_training_data(db)
    if result is None:
        return False
    X, y = result

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    models = {
        "Logistic Regression": LogisticRegression(max_iter=1000, random_state=42),
        "Random Forest": RandomForestClassifier(n_estimators=100, random_state=42),
        "Gradient Boosting": GradientBoostingClassifier(n_estimators=100, learning_rate=0.1, random_state=42),
    }

    _models = {}
    _model_metrics = {}

    for name, model in models.items():
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        y_prob = model.predict_proba(X_test)[:, 1]

        _models[name] = model
        _model_metrics[name] = {
            "auc": round(roc_auc_score(y_test, y_prob), 4),
            "accuracy": round(accuracy_score(y_test, y_pred), 4),
            "precision": round(precision_score(y_test, y_pred), 4),
            "recall": round(recall_score(y_test, y_pred), 4),
            "f1": round(f1_score(y_test, y_pred), 4),
        }

    _trained = True
    return True

def predict_streak_break(db: Session, user_id: int, checkin_date=None) -> dict:
    global _models, _trained
    if not _trained:
        train_models(db)

    features = _extract_features(db, user_id, checkin_date)
    X = pd.DataFrame([features])[FEATURE_NAMES]

    results = {}
    for name, model in _models.items():
        prob = float(model.predict_proba(X)[0, 1])
        pred = int(model.predict(X)[0])
        results[name] = {
            "probability": round(prob, 3),
            "prediction": pred,
            "at_risk": pred == 1,
        }

    # Use Gradient Boosting as the authoritative prediction
    gb = results.get("Gradient Boosting", {})
    return {
        "at_risk": gb.get("at_risk", False),
        "probability": gb.get("probability", 0.0),
        "details": results,
        "features": features,
    }

def get_model_metrics() -> dict:
    global _model_metrics
    return _model_metrics

def get_top_at_risk(db: Session, group_id: int, limit: int = 5) -> list:
    members = db.query(StreakMember).filter(
        StreakMember.streak_group_id == group_id
    ).all()

    at_risk = []
    for m in members:
        if m.user_id == -1:
            continue
        result = predict_streak_break(db, m.user_id)
        if result["at_risk"]:
            user = db.query(User).filter(User.id == m.user_id).first()
            at_risk.append({
                "user_id": m.user_id,
                "username": user.username if user else "unknown",
                "probability": result["probability"],
                "features": result["features"],
            })
    at_risk.sort(key=lambda x: x["probability"], reverse=True)
    return at_risk[:limit]

def is_trained() -> bool:
    return _trained
