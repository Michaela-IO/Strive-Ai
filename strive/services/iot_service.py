import random
import time
import json
from datetime import datetime
from sqlalchemy.orm import Session
from models import CheckIn, StreakMember, StreakGroup

_random_gen = random.Random(42)

def simulate_smartwatch_data(user_id: int) -> dict:
    steps = _random_gen.randint(3000, 14000)
    heart_rate = _random_gen.randint(62, 85)
    active_minutes = _random_gen.randint(15, 75)

    # Add some hour-of-day realism
    hour = datetime.utcnow().hour
    if 5 <= hour <= 9:
        steps = _random_gen.randint(5000, 14000)
        active_minutes = _random_gen.randint(25, 75)
    elif 10 <= hour <= 17:
        steps = _random_gen.randint(4000, 12000)
        active_minutes = _random_gen.randint(20, 60)
    else:
        steps = _random_gen.randint(2000, 8000)
        active_minutes = _random_gen.randint(10, 40)

    return {
        "user_id": user_id,
        "steps_today": steps,
        "heart_rate_bpm": heart_rate,
        "active_minutes": active_minutes,
        "timestamp": datetime.utcnow().isoformat(),
    }

def auto_verify_checkin(data: dict) -> bool:
    steps = data.get("steps_today", 0)
    active = data.get("active_minutes", 0)
    return steps >= 6000 and active >= 30

def process_smartwatch_checkin(db: Session, user_id: int, group_id: int) -> dict:
    data = simulate_smartwatch_data(user_id)
    verified = auto_verify_checkin(data)

    existing = db.query(CheckIn).filter(
        CheckIn.user_id == user_id,
        CheckIn.streak_group_id == group_id,
        CheckIn.created_at >= datetime(datetime.utcnow().year, datetime.utcnow().month, datetime.utcnow().day)
    ).first()
    if existing:
        return {"status": "already_checked_in", "verified": existing.verified}

    checkin = CheckIn(
        user_id=user_id,
        streak_group_id=group_id,
        caption="Auto-verified by Strive Watch \U0000231a",
        sentiment="motivated" if verified else "neutral",
        sentiment_score=0.85 if verified else 0.5,
        verified=verified,
    )
    db.add(checkin)

    member = db.query(StreakMember).filter(
        StreakMember.user_id == user_id,
        StreakMember.streak_group_id == group_id
    ).first()
    if member:
        member.current_streak += 1
        if member.current_streak > member.longest_streak:
            member.longest_streak = member.current_streak

    db.commit()
    return {
        "status": "checked_in",
        "verified": verified,
        "steps": data["steps_today"],
        "active_minutes": data["active_minutes"],
        "heart_rate": data["heart_rate_bpm"],
    }
