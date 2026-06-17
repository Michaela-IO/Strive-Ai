import re
import nltk
from config import SENTIMENT_LABELS

nltk.download("vader_lexicon", quiet=True)
from nltk.sentiment import SentimentIntensityAnalyzer

_sia = SentimentIntensityAnalyzer()

def analyze_sentiment(text: str) -> tuple[str, float]:
    if not text or len(text.strip()) == 0:
        return "neutral", 0.5

    cleaned = re.sub(r"[^a-zA-Z0-9\s]", "", text.lower()).strip()
    if not cleaned:
        return "neutral", 0.5

    scores = _sia.polarity_scores(cleaned)
    compound = scores["compound"]

    if compound >= 0.2:
        label = "motivated"
    elif compound <= -0.2:
        label = "struggling"
    else:
        label = "neutral"

    confidence = round(abs(compound) * 0.6 + 0.4, 2)
    confidence = min(max(confidence, 0.4), 1.0)

    return label, confidence

def get_motivation_message(sentiment: str, streak: int) -> str:
    if sentiment == "motivated":
        if streak >= 30:
            return "\U0001f3c6 " + str(streak) + " days strong! You're an absolute legend!"
        elif streak >= 7:
            return "\U0001f525 " + str(streak) + " day streak! You're on fire \u2014 keep going!"
        else:
            return "\U0001f4aa Great energy today! This is how habits are built!"
    elif sentiment == "struggling":
        if streak >= 7:
            return "\U0001f499 Tough day, but you showed up. That " + str(streak) + " day streak is safe!"
        else:
            return "\U0001f499 Hard days build the most character. You showed up \u2014 that's what counts."
    else:
        if streak >= 14:
            return "\u26a1 " + str(streak) + " days of consistency. You're building something real."
        else:
            return "\u2705 Another day checked off. Consistency is the game."

def extract_keywords(captions: list[str]) -> list[str]:
    from collections import Counter
    stop_words = {"i","the","a","an","and","or","but","in","on",
                  "at","to","for","of","with","my","me","was","is",
                  "it","this","that","so","did","do","today","day"}
    all_words = []
    for caption in captions:
        words = re.sub(r"[^a-zA-Z0-9\s]", "", caption.lower()).split()
        all_words.extend([w for w in words if w not in stop_words and len(w) > 2])
    return [w for w, _ in Counter(all_words).most_common(10)]

def evaluate_accuracy(test_messages: list[tuple[str, str, str]]) -> dict:
    correct = 0
    total = len(test_messages)
    by_label = {"motivated": {"correct": 0, "total": 0},
                "neutral": {"correct": 0, "total": 0},
                "struggling": {"correct": 0, "total": 0}}
    for msg, expected, _ in test_messages:
        label, _ = analyze_sentiment(msg)
        by_label[expected]["total"] += 1
        if label == expected:
            correct += 1
            by_label[expected]["correct"] += 1
    accuracy = round(correct / total, 4) if total else 0
    results = {"overall_accuracy": accuracy, "total": total, "correct": correct}
    for label, vals in by_label.items():
        t = vals["total"]
        c = vals["correct"]
        precision = round(c / t, 4) if t else 0
        recall = round(c / t, 4) if t else 0
        f1 = round(2 * precision * recall / (precision + recall), 4) if (precision + recall) else 0
        results[label] = {"precision": precision, "recall": recall, "f1": f1, "total": t}
    return results
