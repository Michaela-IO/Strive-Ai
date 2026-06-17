import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

APP_NAME = "Strive"
APP_VERSION = "2.0.0"
APP_ICON = "fire"

BASE_DIR = Path(__file__).resolve().parent
SECRET_KEY = os.getenv("STRIVE_SECRET_KEY", "change-this-in-production")
DATABASE_URL = os.getenv("STRIVE_DATABASE_URL", f"sqlite:///{BASE_DIR / 'strive.db'}")
ALGORITHM = os.getenv("STRIVE_ALGORITHM", "HS256")
TOKEN_EXPIRE_DAYS = int(os.getenv("STRIVE_TOKEN_EXPIRE_DAYS", "7"))
DEBUG = os.getenv("STRIVE_DEBUG", "false").lower() == "true"

GOAL_CATEGORIES = [
    "Fitness",
    "Coding",
    "Reading",
    "Meditation",
    "Study",
    "Sleep",
    "Productivity",
    "Other",
]

GRACE_PERIOD_HOURS = 2
MAX_GROUP_SIZE = 10

SENTIMENT_LABELS = ["struggling", "neutral", "motivated"]
MIN_CHECKINS_FOR_ML = 5

COLORS = {
    "primary": "#FF4757",
    "secondary": "#2ED573",
    "tertiary": "#7C5CFC",
    "accent": "#FFA502",
    "dark": "#2D3436",
    "muted": "#636E72",
    "bg": "#F8F9FA",
    "card": "#FFFFFF",
    "border": "#E9ECEF",
    "danger": "#FF6B6B",
    "info": "#48DBFB",
    "success": "#2ED573",
    "warning": "#FFA502",
}
