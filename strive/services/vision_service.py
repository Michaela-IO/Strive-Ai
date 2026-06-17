import streamlit as st
from PIL import Image

ACTIVITY_INDICATORS = {
    "Fitness": ["gym", "workout", "exercise", "running", "weights", "training", "sweat"],
    "Coding": ["code", "screen", "laptop", "terminal", "editor", "programming"],
    "Reading": ["book", "pages", "reading", "chapter", "novel"],
    "Meditation": ["meditation", "calm", "breathing", "mindful", "quiet"],
    "Sleep": ["morning", "sunrise", "alarm", "early", "awake"],
    "Productivity": ["desk", "work", "notes", "focused", "session"],
    "Study": ["notes", "books", "studying", "exam", "revision"],
}

def capture_webcam_photo():
    st.markdown("""
    <div style='background:var(--color-background-secondary);
    border:0.5px solid var(--color-border-tertiary);
    border-radius:12px; padding:16px; margin-bottom:16px'>
        <div style='font-size:13px; font-weight:500; color:var(--color-text-primary); margin-bottom:4px'>
            📸 Proof Camera
        </div>
        <div style='font-size:12px; color:var(--color-text-secondary)'>
            Take a photo to prove you completed today's activity.
        </div>
    </div>
    """, unsafe_allow_html=True)

    camera_photo = st.camera_input("Take your proof photo")
    if camera_photo is not None:
        image = Image.open(camera_photo)
        return image, camera_photo.getvalue()
    return None, None

def verify_activity_image(image: Image.Image, category: str, caption: str = "") -> dict:
    if image is None:
        return {"verified": False, "confidence": 0.0, "message": "No image provided", "analysis": {}}

    width, height = image.size
    if image.mode != "RGB":
        image = image.convert("RGB")

    pixels = list(image.getdata())
    avg_brightness = sum(sum(p) / 3 for p in pixels[:1000]) / 1000

    checks = {
        "valid_size": width >= 100 and height >= 100,
        "well_lit": avg_brightness > 40,
        "not_blank": avg_brightness < 240,
        "reasonable_aspect": 0.3 < (width / height) < 4.0,
    }

    caption_score = 0.0
    if caption:
        caption_lower = caption.lower()
        keywords = ACTIVITY_INDICATORS.get(category, [])
        matches = sum(1 for kw in keywords if kw in caption_lower)
        caption_score = min(matches / max(len(keywords), 1), 1.0)
        checks["caption_matches"] = matches > 0

    passed = sum(1 for v in checks.values() if v)
    total = len(checks)
    final_confidence = min((passed / total) + caption_score * 0.2, 1.0)
    verified = final_confidence >= 0.6 and checks.get("valid_size") and checks.get("well_lit")

    if verified and final_confidence >= 0.85:
        message = "✅ Proof verified! Great work — this looks legit!"
    elif verified:
        message = "✅ Proof accepted! Keep showing up!"
    elif not checks.get("well_lit"):
        message = "⚠️ Image is too dark. Try in better lighting."
    elif not checks.get("valid_size"):
        message = "⚠️ Image too small. Please take a clearer photo."
    else:
        message = "⚠️ Could not verify. Add a caption describing your activity."

    return {
        "verified": verified,
        "confidence": round(final_confidence, 2),
        "message": message,
        "analysis": {
            "brightness": round(avg_brightness, 1),
            "resolution": f"{width}x{height}",
            "checks_passed": f"{passed}/{total}",
            "caption_keywords": caption_score > 0
        }
    }

def display_verification_result(result: dict):
    confidence_pct = int(result["confidence"] * 100)
    color = "#1D9E75" if result["verified"] else "#E24B4A"
    bg = "#E1F5EE" if result["verified"] else "#FCEBEB"
    border = "#9FE1CB" if result["verified"] else "#F09595"

    st.markdown(f"""
    <div style='background:{bg}; border:0.5px solid {border};
    border-radius:12px; padding:14px 16px; margin:10px 0'>
        <div style='display:flex; justify-content:space-between; align-items:center'>
            <span style='color:{color}; font-weight:500; font-size:13px'>{result["message"]}</span>
            <span style='color:{color}; font-size:12px; background:white;
            padding:3px 10px; border-radius:20px; border:0.5px solid {border}'>
                {confidence_pct}% confidence
            </span>
        </div>
        <div style='margin-top:8px; display:flex; gap:12px; flex-wrap:wrap'>
            <span style='color:var(--color-text-tertiary); font-size:11px'>
                💡 Brightness: {result["analysis"].get("brightness", "N/A")}
            </span>
            <span style='color:var(--color-text-tertiary); font-size:11px'>
                📐 {result["analysis"].get("resolution", "N/A")}
            </span>
            <span style='color:var(--color-text-tertiary); font-size:11px'>
                ✔️ Checks: {result["analysis"].get("checks_passed", "N/A")}
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)