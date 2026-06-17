from database import SessionLocal, init_db
from models import User, Goal, StreakGroup, StreakMember, CheckIn, Reaction, Comment, Nudge
from services.auth_service import create_user
from datetime import datetime, timedelta, timezone
import random

DEMO_USERS = [
    ("strive_demo", "demo@strive.app", "demo1234", "The original striver"),
    ("alice_fit", "alice@strive.app", "alice1234", "Fitness enthusiast"),
    ("bob_codes", "bob@strive.app", "bob1234", "Building the next big thing"),
    ("charlie_reads", "charlie@strive.app", "charlie1234", "Bookworm on a mission"),
    ("diana_mindful", "diana@strive.app", "diana1234", "Finding peace one breath at a time"),
]

SEED_GOALS = [
    ("Morning Workout", "Hit the gym or home workout every morning", "Fitness", 30),
    ("Daily Coding", "Code at least 30 minutes every day", "Coding", 60),
    ("Read 10 Pages", "Read 10 pages of any book daily", "Reading", 30),
    ("Meditation", "10 minutes of mindfulness meditation", "Meditation", 21),
]

SENTIMENTS = ["motivated", "neutral", "struggling"]
CAPTIONS = [
    "Great session today! Feeling strong and energized",
    "Barely made it but showed up - that's what counts",
    "Solid progress, staying consistent",
    "Tough day but didn't skip",
    "Crushed my goals today! Personal best!",
    "Rough morning but pushed through",
    "Another day, another step forward",
    "Feeling great about this streak!",
]

def seed_database():
    init_db()
    db = SessionLocal()

    if db.query(User).first():
        db.close()
        return

    users = []
    for username, email, password, bio in DEMO_USERS:
        ok, msg, user = create_user(db, username, email, password)
        if ok and user:
            user.bio = bio
            users.append(user)
    db.commit()

    goals_with_groups = []
    for title, desc, category, duration in SEED_GOALS:
        goal = Goal(
            creator_id=users[0].id, title=title, description=desc,
            category=category, target_duration=duration, visibility="public"
        )
        db.add(goal)
        db.flush()
        group = StreakGroup(goal_id=goal.id, current_streak=random.randint(3, 14), longest_streak=random.randint(7, 30))
        db.add(group)
        db.flush()
        goals_with_groups.append((goal, group))
    db.commit()

    today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    for i, user in enumerate(users):
        user_goals = goals_with_groups[i % len(goals_with_groups): i % len(goals_with_groups) + min(2, len(goals_with_groups) - (i % len(goals_with_groups)))]
        for goal, group in user_goals:
            member = StreakMember(
                user_id=user.id, streak_group_id=group.id,
                current_streak=random.randint(1, 10), longest_streak=random.randint(5, 20),
                consistency_score=random.uniform(60, 100)
            )
            db.add(member)
            db.flush()

            for days_ago in range(random.randint(5, 14)):
                checkin_time = today - timedelta(days=days_ago, hours=random.randint(6, 20))
                sentiment = random.choice(SENTIMENTS)
                caption = random.choice(CAPTIONS)
                checkin = CheckIn(
                    user_id=user.id, streak_group_id=group.id,
                    caption=caption, sentiment=sentiment,
                    sentiment_score=random.uniform(0.3, 1.0),
                    verified=random.random() > 0.3,
                    created_at=checkin_time
                )
                db.add(checkin)
                db.flush()

                if random.random() > 0.5:
                    reactor = random.choice(users)
                    if reactor.id != user.id:
                        db.add(Reaction(user_id=reactor.id, checkin_id=checkin.id, type="flame"))

                if random.random() > 0.7:
                    commenter = random.choice(users)
                    if commenter.id != user.id:
                        db.add(Comment(
                            user_id=commenter.id, checkin_id=checkin.id,
                            content=random.choice(["Keep it up!", "Nice work!", "You got this!", "Inspiring!"]),
                            created_at=checkin_time + timedelta(hours=1)
                        ))

    for user in users[1:]:
        receiver = users[0]
        db.add(Nudge(sender_id=user.id, receiver_id=receiver.id,
                     streak_group_id=goals_with_groups[0][1].id,
                     created_at=today - timedelta(hours=random.randint(1, 8))))

    db.commit()
    print("Database seeded successfully!")
    for username, email, password, _ in DEMO_USERS:
        print(f"  @{username:<18}  {email:<22}  {password}")
    db.close()

if __name__ == "__main__":
    seed_database()
