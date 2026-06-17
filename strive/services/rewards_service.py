from datetime import datetime, timezone
from sqlalchemy.orm import Session
from models import UserReward, UserPoints, CheckIn, StreakMember

# ── All possible rewards ──
REWARDS = {
    # Streak milestones
    "streak_3":   {"emoji": "<i class='fas fa-seedling'></i>", "title": "Getting Started",    "desc": "3 day streak",         "points": 50,   "type": "badge"},
    "streak_7":   {"emoji": "<i class='fas fa-fire'></i>",    "title": "Week Warrior",       "desc": "7 day streak",         "points": 100,  "type": "badge"},
    "streak_14":  {"emoji": "<i class='fas fa-bolt'></i>",    "title": "Two Week Titan",     "desc": "14 day streak",        "points": 200,  "type": "badge"},
    "streak_21":  {"emoji": "<i class='fas fa-dumbbell'></i>","title": "Habit Locked In",    "desc": "21 day streak",        "points": 300,  "type": "trophy"},
    "streak_30":  {"emoji": "<i class='fas fa-trophy'></i>",  "title": "Monthly Master",     "desc": "30 day streak",        "points": 500,  "type": "trophy"},
    "streak_60":  {"emoji": "<i class='fas fa-gem'></i>",     "title": "Diamond Grinder",    "desc": "60 day streak",        "points": 1000, "type": "trophy"},
    "streak_100": {"emoji": "<i class='fas fa-crown'></i>",   "title": "Century Champion",   "desc": "100 day streak",       "points": 2000, "type": "trophy"},

    # Check-in milestones
    "checkins_1":   {"emoji": "<i class='fas fa-check-circle'></i>", "title": "First Step",        "desc": "First check-in",       "points": 20,  "type": "badge"},
    "checkins_10":  {"emoji": "<i class='fas fa-calendar'></i>",    "title": "Ten Down",          "desc": "10 total check-ins",   "points": 80,  "type": "badge"},
    "checkins_25":  {"emoji": "<i class='fas fa-bullseye'></i>",    "title": "Quarter Century",   "desc": "25 total check-ins",   "points": 150, "type": "badge"},
    "checkins_50":  {"emoji": "<i class='fas fa-star'></i>",        "title": "Fifty Strong",      "desc": "50 total check-ins",   "points": 300, "type": "trophy"},
    "checkins_100": {"emoji": "<i class='fas fa-rocket'></i>",      "title": "Century Striver",   "desc": "100 total check-ins",  "points": 600, "type": "trophy"},

    # Social rewards
    "first_nudge":    {"emoji": "<i class='fas fa-hand-wave'></i>", "title": "Good Teammate",   "desc": "Sent your first nudge",      "points": 30,  "type": "badge"},
    "nudge_5":        {"emoji": "<i class='fas fa-bullhorn'></i>",  "title": "Hype Person",     "desc": "Sent 5 nudges",              "points": 75,  "type": "badge"},
    "joined_3_groups":{"emoji": "<i class='fas fa-users'></i>",     "title": "Social Striver",  "desc": "Joined 3 streak groups",     "points": 100, "type": "badge"},
    "joined_5_groups":{"emoji": "<i class='fas fa-globe'></i>",     "title": "Community Builder","desc": "Joined 5 streak groups",    "points": 200, "type": "badge"},

    # Mood rewards
    "motivated_10":  {"emoji": "<i class='fas fa-smile'></i>",     "title": "Positivity King",  "desc": "10 motivated check-ins",    "points": 120, "type": "badge"},
    "motivated_25":  {"emoji": "<i class='fas fa-sun'></i>",       "title": "Sunshine Striver", "desc": "25 motivated check-ins",   "points": 250, "type": "badge"},

    # Verified proof
    "verified_5":   {"emoji": "<i class='fas fa-camera'></i>",    "title": "Proof Provider",   "desc": "5 verified check-ins",       "points": 100, "type": "badge"},
    "verified_20":  {"emoji": "<i class='fas fa-video'></i>",     "title": "Evidence Expert",  "desc": "20 verified check-ins",      "points": 300, "type": "trophy"},

    # Consistency
    "consistency_7_days": {"emoji": "<i class='fas fa-calendar-check'></i>", "title": "Full Week",   "desc": "Checked in 7 days in a row", "points": 150, "type": "badge"},
    "early_bird":         {"emoji": "<i class='fas fa-sun'></i>",             "title": "Early Bird",  "desc": "Checked in before 7am",      "points": 50,  "type": "badge"},
}

# ── Level thresholds ──
LEVELS = [
    (0,    1, "Beginner",      "<span style='color:#ADB5BD'>&#9679;</span>"),
    (100,  2, "Striver",       "<span style='color:#2ED573'>&#9679;</span>"),
    (300,  3, "Hustler",       "<span style='color:#7C5CFC'>&#9679;</span>"),
    (600,  4, "Warrior",       "<span style='color:#FF4757'>&#9679;</span>"),
    (1000, 5, "Champion",      "<span style='color:#FFA502'>&#9679;</span>"),
    (2000, 6, "Legend",        "<span style='color:#FFA502'>&#9679;</span>"),
    (4000, 7, "Elite",         "<span style='color:#FF4757'>&#9679;</span>"),
    (8000, 8, "Unstoppable",   "<span style='color:#7C5CFC; font-weight:700'>&#9830;</span>"),
]

def get_level(points: int) -> tuple:
    level_info = LEVELS[0]
    for threshold, level, name, color in LEVELS:
        if points >= threshold:
            level_info = (threshold, level, name, color)
    return level_info

def get_next_level(points: int) -> tuple:
    for i, (threshold, level, name, color) in enumerate(LEVELS):
        if points < threshold:
            return threshold, name, color
    return None, "Max Level", "<span style='color:#7C5CFC;font-weight:700'>&#9830;</span>"

def get_or_create_points(db: Session, user_id: int) -> "UserPoints":
    points_obj = db.query(UserPoints).filter(UserPoints.user_id == user_id).first()
    if not points_obj:
        points_obj = UserPoints(user_id=user_id, total_points=0, level=1)
        db.add(points_obj)
        db.commit()
        db.refresh(points_obj)
    return points_obj

def has_reward(db: Session, user_id: int, reward_key: str) -> bool:
    return db.query(UserReward).filter(
        UserReward.user_id == user_id,
        UserReward.reward_key == reward_key
    ).first() is not None

def award_reward(db: Session, user_id: int, reward_key: str) -> dict | None:
    if has_reward(db, user_id, reward_key):
        return None
    if reward_key not in REWARDS:
        return None

    reward = REWARDS[reward_key]
    user_reward = UserReward(
        user_id=user_id,
        reward_type=reward["type"],
        reward_key=reward_key,
        reward_title=reward["title"],
        reward_emoji=reward["emoji"],
        points_earned=reward["points"]
    )
    db.add(user_reward)

    points_obj = get_or_create_points(db, user_id)
    points_obj.total_points += reward["points"]
    _, level, _, _ = get_level(points_obj.total_points)
    points_obj.level = level
    points_obj.updated_at = datetime.now(timezone.utc)

    db.commit()
    return reward

def check_and_award_all(db: Session, user_id: int) -> list[dict]:
    """
    Check all reward conditions for a user and award any newly earned rewards.
    Call this after every check-in.
    Returns list of newly earned rewards.
    """
    newly_earned = []

    checkins = db.query(CheckIn).filter(CheckIn.user_id == user_id).all()
    memberships = db.query(StreakMember).filter(StreakMember.user_id == user_id).all()
    total_checkins = len(checkins)
    motivated_checkins = sum(1 for c in checkins if c.sentiment == "motivated")
    verified_checkins = sum(1 for c in checkins if c.verified)
    best_streak = max([m.longest_streak for m in memberships], default=0)
    current_streak = max([m.current_streak for m in memberships], default=0)

    from models import Nudge
    nudges_sent = db.query(Nudge).filter(Nudge.sender_id == user_id).count()

    # Check-in milestones
    for count, key in [(1, "checkins_1"), (10, "checkins_10"), (25, "checkins_25"),
                       (50, "checkins_50"), (100, "checkins_100")]:
        if total_checkins >= count:
            r = award_reward(db, user_id, key)
            if r:
                newly_earned.append(r)

    # Streak milestones
    streak_to_check = max(best_streak, current_streak)
    for days, key in [(3, "streak_3"), (7, "streak_7"), (14, "streak_14"),
                      (21, "streak_21"), (30, "streak_30"), (60, "streak_60"), (100, "streak_100")]:
        if streak_to_check >= days:
            r = award_reward(db, user_id, key)
            if r:
                newly_earned.append(r)

    # Social milestones
    if nudges_sent >= 1:
        r = award_reward(db, user_id, "first_nudge")
        if r: newly_earned.append(r)
    if nudges_sent >= 5:
        r = award_reward(db, user_id, "nudge_5")
        if r: newly_earned.append(r)
    if len(memberships) >= 3:
        r = award_reward(db, user_id, "joined_3_groups")
        if r: newly_earned.append(r)
    if len(memberships) >= 5:
        r = award_reward(db, user_id, "joined_5_groups")
        if r: newly_earned.append(r)

    # Mood milestones
    if motivated_checkins >= 10:
        r = award_reward(db, user_id, "motivated_10")
        if r: newly_earned.append(r)
    if motivated_checkins >= 25:
        r = award_reward(db, user_id, "motivated_25")
        if r: newly_earned.append(r)

    # Verified proof milestones
    if verified_checkins >= 5:
        r = award_reward(db, user_id, "verified_5")
        if r: newly_earned.append(r)
    if verified_checkins >= 20:
        r = award_reward(db, user_id, "verified_20")
        if r: newly_earned.append(r)

    # Early bird
    for c in checkins:
        if c.created_at.hour < 7:
            r = award_reward(db, user_id, "early_bird")
            if r: newly_earned.append(r)
            break

    return newly_earned

def get_user_rewards(db: Session, user_id: int) -> list:
    return db.query(UserReward).filter(
        UserReward.user_id == user_id
    ).order_by(UserReward.earned_at.desc()).all()

def get_leaderboard(db: Session, limit: int = 10) -> list:
    from models import User
    results = db.query(UserPoints, User).join(
        User, UserPoints.user_id == User.id
    ).order_by(UserPoints.total_points.desc()).limit(limit).all()
    return results