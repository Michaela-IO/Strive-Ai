from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from database import Base


def _now():
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    avatar_url = Column(String(500), nullable=True)
    bio = Column(Text, nullable=True)
    created_at = Column(DateTime, default=_now)

    goals = relationship("Goal", back_populates="creator")
    memberships = relationship("StreakMember", back_populates="user")
    checkins = relationship("CheckIn", back_populates="user")


class Goal(Base):
    __tablename__ = "goals"

    id = Column(Integer, primary_key=True, index=True)
    creator_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(50), nullable=False)
    frequency = Column(String(50), default="daily")
    visibility = Column(String(20), default="public")
    target_duration = Column(Integer, default=30)
    created_at = Column(DateTime, default=_now)

    creator = relationship("User", back_populates="goals")
    streak_group = relationship("StreakGroup", back_populates="goal", uselist=False)


class StreakGroup(Base):
    __tablename__ = "streak_groups"

    id = Column(Integer, primary_key=True, index=True)
    goal_id = Column(Integer, ForeignKey("goals.id"))
    current_streak = Column(Integer, default=0)
    longest_streak = Column(Integer, default=0)
    member_count = Column(Integer, default=1)
    created_at = Column(DateTime, default=_now)

    goal = relationship("Goal", back_populates="streak_group")
    members = relationship("StreakMember", back_populates="group")
    checkins = relationship("CheckIn", back_populates="group")


class StreakMember(Base):
    __tablename__ = "streak_members"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    streak_group_id = Column(Integer, ForeignKey("streak_groups.id"))
    joined_at = Column(DateTime, default=_now)
    consistency_score = Column(Float, default=100.0)
    current_streak = Column(Integer, default=0)
    longest_streak = Column(Integer, default=0)

    user = relationship("User", back_populates="memberships")
    group = relationship("StreakGroup", back_populates="members")


class CheckIn(Base):
    __tablename__ = "checkins"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    streak_group_id = Column(Integer, ForeignKey("streak_groups.id"))
    image_url = Column(String(500), nullable=True)
    caption = Column(Text, nullable=True)
    created_at = Column(DateTime, default=_now)
    verified = Column(Boolean, default=False)
    sentiment = Column(String(20), nullable=True)
    sentiment_score = Column(Float, nullable=True)

    user = relationship("User", back_populates="checkins")
    group = relationship("StreakGroup", back_populates="checkins")
    comments = relationship("Comment", back_populates="checkin")
    reactions = relationship("Reaction", back_populates="checkin")


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    checkin_id = Column(Integer, ForeignKey("checkins.id"))
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=_now)

    checkin = relationship("CheckIn", back_populates="comments")


class Reaction(Base):
    __tablename__ = "reactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    checkin_id = Column(Integer, ForeignKey("checkins.id"))
    type = Column(String(20), nullable=False)

    checkin = relationship("CheckIn", back_populates="reactions")


class Nudge(Base):
    __tablename__ = "nudges"

    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey("users.id"))
    receiver_id = Column(Integer, ForeignKey("users.id"))
    streak_group_id = Column(Integer, ForeignKey("streak_groups.id"))
    created_at = Column(DateTime, default=_now)


class MLPrediction(Base):
    __tablename__ = "ml_predictions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    streak_group_id = Column(Integer, ForeignKey("streak_groups.id"))
    prediction_type = Column(String(50))
    prediction_value = Column(Float)
    created_at = Column(DateTime, default=_now)


class IoTDevice(Base):
    __tablename__ = "iot_devices"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    device_name = Column(String(100))
    device_type = Column(String(50))
    last_sync = Column(DateTime, nullable=True)
    steps_today = Column(Integer, default=0)
    heart_rate = Column(Integer, nullable=True)
    active_minutes = Column(Integer, default=0)


class UserReward(Base):
    __tablename__ = "user_rewards"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    reward_type = Column(String(50))
    reward_key = Column(String(100))
    reward_title = Column(String(100))
    reward_emoji = Column(String(10))
    points_earned = Column(Integer, default=0)
    earned_at = Column(DateTime, default=_now)


class UserPoints(Base):
    __tablename__ = "user_points"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    total_points = Column(Integer, default=0)
    level = Column(Integer, default=1)
    updated_at = Column(DateTime, default=_now)