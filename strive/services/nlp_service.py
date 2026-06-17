import re
import nltk
from config import SENTIMENT_LABELS

nltk.download("vader_lexicon", quiet=True)
from nltk.sentiment import SentimentIntensityAnalyzer

_sia = SentimentIntensityAnalyzer()

_BOOST_WORDS = {
    "crushed": 0.5, "crushing": 0.5, "nailed": 0.6, "killed": 0.5, "beast": 0.6,
    "unstoppable": 0.7, "fired": 0.4, "grind": 0.3, "grinding": 0.3, "progress": 0.3,
    "strong": 0.3, "stronger": 0.4, "proud": 0.4, "amazing": 0.6, "awesome": 0.5,
    "killing": 0.4, "personal": 0.2, "finally": 0.2, "woke": 0.3, "pushed": 0.3,
    "barely": -0.5, "tough": -0.3, "exhausted": -0.5, "drained": -0.5, "rough": -0.4,
    "struggled": -0.5, "struggling": -0.5, "hard": -0.2, "tired": -0.3,
    "didnt": -0.2, "almost": -0.3, "missed": -0.4, "skip": -0.3, "lazy": -0.5,
}

def analyze_sentiment(text: str) -> tuple[str, float]:
    if not text or len(text.strip()) == 0:
        return "neutral", 0.5

    cleaned = re.sub(r"[^a-zA-Z0-9\s]", "", text.lower()).strip()
    if not cleaned:
        return "neutral", 0.5

    scores = _sia.polarity_scores(cleaned)
    compound = scores["compound"]
    words = cleaned.split()

    boost = sum(_BOOST_WORDS.get(w, 0) for w in words)
    adjusted = compound + boost * 0.3
    adjusted = max(min(adjusted, 1.0), -1.0)

    if adjusted >= 0.15:
        label = "motivated"
    elif adjusted <= -0.1:
        label = "struggling"
    else:
        label = "neutral"

    confidence = round(abs(adjusted) * 0.5 + 0.5, 2)
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
    labels = ["motivated", "neutral", "struggling"]
    confusion = {t: {p: 0 for p in labels} for t in labels}
    for msg, expected, _ in test_messages:
        predicted, _ = analyze_sentiment(msg)
        confusion[expected][predicted] += 1
        if predicted == expected:
            correct += 1
    accuracy = round(correct / total, 4) if total else 0
    results = {"overall_accuracy": accuracy, "total": total, "correct": correct}
    for label in labels:
        tp = confusion[label][label]
        fp = sum(confusion[other][label] for other in labels if other != label)
        fn = sum(confusion[label][other] for other in labels if other != label)
        prec = round(tp / (tp + fp), 4) if (tp + fp) else 0
        rec = round(tp / (tp + fn), 4) if (tp + fn) else 0
        f1 = round(2 * prec * rec / (prec + rec), 4) if (prec + rec) else 0
        results[label] = {"precision": prec, "recall": rec, "f1": f1, "total": tp + fn}
    return results
