import re
from config import SENTIMENT_LABELS

# Keyword-based sentiment analysis
# We'll upgrade this to a proper ML model in the next phase

MOTIVATED_WORDS = [
    "great", "amazing", "awesome", "crushed", "killed", "nailed",
    "strong", "powerful", "best", "love", "excited", "proud",
    "achieved", "completed", "finished", "won", "personal record",
    "pr", "pb", "pumped", "motivated", "unstoppable", "fired up",
    "consistency", "discipline", "grind", "progress", "growth"
]

STRUGGLING_WORDS = [
    "tired", "exhausted", "hard", "difficult", "struggle", "struggled",
    "barely", "almost", "missed", "failed", "fail", "bad", "rough",
    "tough", "pain", "sore", "burned out", "burnout", "unmotivated",
    "lazy", "skip", "skipped", "late", "almost gave up", "demotivated"
]

def clean_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-zA-Z0-9\s]", "", text)
    return text.strip()

def analyze_sentiment(text: str) -> tuple[str, float]:
    """
    Analyze sentiment of a check-in caption.
    Returns (sentiment_label, confidence_score)
    
    This uses keyword matching for now.
    Phase 2 will replace this with a trained ML classifier.
    """
    if not text or len(text.strip()) == 0:
        return "neutral", 0.5

    cleaned = clean_text(text)
    words = cleaned.split()

    motivated_count = sum(1 for word in words if word in MOTIVATED_WORDS)
    struggling_count = sum(1 for word in words if word in STRUGGLING_WORDS)

    total = motivated_count + struggling_count

    if total == 0:
        return "neutral", 0.5

    motivated_score = motivated_count / total

    if motivated_score >= 0.6:
        confidence = min(0.5 + motivated_score * 0.5, 1.0)
        return "motivated", round(confidence, 2)
    elif motivated_score <= 0.4:
        confidence = min(0.5 + (1 - motivated_score) * 0.5, 1.0)
        return "struggling", round(confidence, 2)
    else:
        return "neutral", 0.5

def get_motivation_message(sentiment: str, streak: int) -> str:
    """
    Generate a motivational message based on sentiment and streak length.
    Phase 2 will connect this to the Claude API for personalised messages.
    """
    if sentiment == "motivated":
        if streak >= 30:
            return f"🏆 {streak} days strong! You're an absolute legend!"
        elif streak >= 7:
            return f"🔥 {streak} day streak! You're on fire — keep going!"
        else:
            return "💪 Great energy today! This is how habits are built!"
    elif sentiment == "struggling":
        if streak >= 7:
            return f"💙 Tough day, but you showed up. That {streak} day streak is safe!"
        else:
            return "💙 Hard days build the most character. You showed up — that's what counts."
    else:
        if streak >= 14:
            return f"⚡ {streak} days of consistency. You're building something real."
        else:
            return "✅ Another day checked off. Consistency is the game."

def extract_keywords(captions: list[str]) -> list[str]:
    """
    Extract most common meaningful words from a list of captions.
    Used for goal recommendation and user profiling.
    """
    from collections import Counter
    stop_words = {"i", "the", "a", "an", "and", "or", "but", "in", "on",
                  "at", "to", "for", "of", "with", "my", "me", "was", "is",
                  "it", "this", "that", "so", "did", "do", "today", "day"}
    all_words = []
    for caption in captions:
        words = clean_text(caption).split()
        all_words.extend([w for w in words if w not in stop_words and len(w) > 2])
    
    most_common = Counter(all_words).most_common(10)
    return [word for word, count in most_common]