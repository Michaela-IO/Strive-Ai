import streamlit as st
from database import init_db, SessionLocal
from models import User, Goal, StreakGroup, StreakMember, CheckIn, Reaction, Nudge
from config import APP_NAME, GOAL_CATEGORIES
from datetime import datetime, date
from services.auth_service import authenticate_user, create_user
from pathlib import Path
import base64

STATIC_DIR = Path(__file__).resolve().parent / "static"

def img_bg(name):
    p = STATIC_DIR / name
    if p.exists():
        ext = p.suffix.lower()
        mime = {"png": "image/png", "jfif": "image/jpeg", "jpg": "image/jpeg", "jpeg": "image/jpeg"}.get(ext.lstrip("."), "image/jpeg")
        with open(p, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        return f"data:{mime};base64,{b64}"
    return ""

IMG_GYM = img_bg("gym_bg.jfif")
IMG_CODE = img_bg("code.jfif")
IMG_FOCUS = img_bg("focus.jfif")
IMG_STUDY = img_bg("study.jfif")
IMG_SLEEP = img_bg("sleep.jfif")
IMG_VISION = img_bg("vision.jfif")
IMG_LOGIN = img_bg("gemini_bg.jpg")

init_db()
db_check = SessionLocal()
if not db_check.query(User).first():
    from seed_data import seed_database
    seed_database()
db_check.close()

st.set_page_config(page_title="Strive", page_icon="🔥", layout="wide", initial_sidebar_state="collapsed")

P = "#FF4757"
S = "#2ED573"
T = "#7C5CFC"
A = "#FFA502"
D = "#2D3436"
M = "#636E72"
B = "#F8F9FA"

st.markdown("<link rel=\"stylesheet\" href=\"https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css\">", unsafe_allow_html=True)
st.markdown("<style>" + """\
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
* { font-family: 'Inter', sans-serif; }
[data-testid="stAppViewContainer"] { background: linear-gradient(135deg, #FFF5F7 0%, #F0F4FF 50%, #F5FFF7 100%); }
[data-testid="stHeader"] { background: linear-gradient(135deg, #FFF5F7 0%, #F0F4FF 50%, #F5FFF7 100%); }
.block-container { padding-top: 3.2rem !important; max-width: 1100px !important; }
.landing-nav { display: flex; align-items: center; justify-content: space-between; padding: 16px 0; margin-bottom: 8px; }
.landing-logo { font-size: 22px; font-weight: 700; color: #2D3436; }
.landing-nav-links { display: flex; gap: 24px; }
.landing-nav-links a { color: #636E72; text-decoration: none; font-size: 14px; font-weight: 500; }
.landing-nav-links a:hover { color: #FF4757; }
[data-testid="column"]:has(.form-header) > div:first-child { background: linear-gradient(135deg, #FFFFFF, #FAFBFF); border: 1px solid #E9ECEF; border-radius: 16px; padding: 20px; box-shadow: 0 8px 30px rgba(0,0,0,0.06); }
.hero-badge { display: inline-block; background: #FFF0F0; color: #FF4757; font-size: 12px; font-weight: 600; padding: 6px 16px; border-radius: 20px; margin-bottom: 14px; letter-spacing: 0.03em; }
.hero-title { font-size: 48px; font-weight: 800; color: #2D3436; margin: 0; line-height: 1.1; letter-spacing: -0.02em; }
.hero-subtitle { font-size: 48px; font-weight: 800; margin: 0 0 8px; line-height: 1.1; letter-spacing: -0.02em; color: #FF4757; }
.hero-desc { font-size: 14px; color: #636E72; line-height: 1.6; margin-bottom: 20px; }
html { scroll-behavior: smooth; }
.hero-stats { display: flex; gap: 16px; flex-wrap: wrap; }
.stat-item { display: inline-flex; align-items: center; gap: 6px; font-size: 13px; font-weight: 600; color: #2D3436; background: white; border: 1px solid #E9ECEF; padding: 8px 14px; border-radius: 10px; transition:all 0.2s; }
.stat-item:hover { border-color:#FF4757; transform:translateY(-2px); box-shadow:0 4px 12px rgba(255,71,87,0.12); }
.hero-form-card { background: white; border: 1px solid #E9ECEF; border-radius: 16px; padding: 20px; box-shadow: 0 8px 30px rgba(0,0,0,0.06); }
.form-header { display: flex; align-items: center; gap: 10px; margin-bottom: 12px; font-size: 16px; font-weight: 700; color: #2D3436; }
.section-title { text-align: center; font-size: 28px; font-weight: 700; color: #2D3436; margin: 0 0 8px; }
.section-desc { text-align: center; font-size: 14px; color: #636E72; margin: 0 0 28px; }
.step-card { background: linear-gradient(135deg, #FFFFFF, #F5F3FF); border: 1px solid #E9ECEF; border-radius: 14px; padding: 24px 16px; text-align: center; margin-bottom: 12px; }
.step-number { width: 40px; height: 40px; border-radius: 50%; background: #FF4757; color: white; display: flex; align-items: center; justify-content: center; font-size: 18px; font-weight: 700; margin: 0 auto 12px; }
.step-title { font-size: 14px; font-weight: 600; color: #2D3436; margin-bottom: 8px; }
.step-desc { font-size: 12px; color: #636E72; line-height: 1.5; }
.landing-footer { display: flex; justify-content: space-between; flex-wrap: wrap; gap: 24px; padding: 40px 0 0; border-top: 1px solid #E9ECEF; margin-top: 48px; }
.footer-col { min-width: 120px; }
.footer-brand { font-size: 18px; font-weight: 700; color: #2D3436; margin-bottom: 6px; }
.footer-text { font-size: 13px; color: #636E72; }
.footer-heading { font-size: 12px; font-weight: 600; color: #2D3436; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 8px; }
.footer-link { display: block; font-size: 13px; color: #636E72; text-decoration: none; margin-bottom: 6px; }
.footer-link:hover { color: #FF4757; }
.footer-bottom { text-align: center; font-size: 11px; color: #ADB5BD; padding: 16px 0; }
@keyframes fadeUp { from { opacity:0; transform:translateY(20px) } to { opacity:1; transform:translateY(0) } }
@keyframes fadeIn { from { opacity:0 } to { opacity:1 } }
@keyframes pulse { 0%,100% { transform:scale(1) } 50% { transform:scale(1.05) } }
@keyframes float { 0%,100% { transform:translateY(0) } 50% { transform:translateY(-12px) } }
@keyframes shimmer { 0% { background-position:-200% 0 } 100% { background-position:200% 0 } }
@keyframes countUp { from { opacity:0; transform:translateY(10px) } to { opacity:1; transform:translateY(0) } }
.animate-fade-up { animation:fadeUp 0.6s ease both; }
.animate-fade-in { animation:fadeIn 0.8s ease both; }
.animate-pulse { animation:pulse 2s ease infinite; }
.animate-float { animation:float 4s ease-in-out infinite; }
.hero-badge { animation:fadeUp 0.5s ease 0.1s both; }
.hero-title { animation:fadeUp 0.5s ease 0.2s both; }
.hero-subtitle { animation:fadeUp 0.5s ease 0.3s both; }
.hero-desc { animation:fadeUp 0.5s ease 0.4s both; }
.hero-stats { animation:fadeUp 0.5s ease 0.5s both; }
.hero-stats .stat-item:nth-child(1) { animation:fadeUp 0.4s ease 0.6s both; }
.hero-stats .stat-item:nth-child(2) { animation:fadeUp 0.4s ease 0.7s both; }
.hero-stats .stat-item:nth-child(3) { animation:fadeUp 0.4s ease 0.8s both; }
.form-header { animation:fadeUp 0.5s ease 0.4s both; }
.demo-card { background:linear-gradient(135deg,#FFFFFF,#F5F3FF); border:1px solid #E9ECEF; border-radius:12px; padding:12px; cursor:pointer; transition:all 0.2s; text-align:center; animation:fadeUp 0.4s ease both; }
.demo-card:hover { border-color:#FF4757; box-shadow:0 4px 16px rgba(255,71,87,0.15); transform:translateY(-2px); }
.demo-avatar { width:40px; height:40px; border-radius:50%; display:flex; align-items:center; justify-content:center; font-weight:700; font-size:14px; margin:0 auto 6px; }
.demo-name { font-size:13px; font-weight:600; color:#2D3436; }
.demo-email { font-size:10px; color:#ADB5BD; }
.step-card { transition:all 0.3s; cursor:default; }
.step-card:hover { transform:translateY(-4px); box-shadow:0 8px 24px rgba(0,0,0,0.08); border-color:#FF4757; }
.step-card:hover .step-number { animation:pulse 0.6s ease; }
.section-title { animation:fadeUp 0.5s ease 0.1s both; }
.section-desc { animation:fadeUp 0.5s ease 0.2s both; }
.floating-shape { position:fixed; border-radius:50%; pointer-events:none; z-index:-1; opacity:0.06; }
.floating-shape-1 { width:300px; height:300px; background:#FF4757; top:-80px; right:-60px; animation:float 6s ease-in-out infinite; }
.floating-shape-2 { width:200px; height:200px; background:#7C5CFC; bottom:120px; left:-40px; animation:float 8s ease-in-out infinite 1s; }
.floating-shape-3 { width:150px; height:150px; background:#2ED573; bottom:-30px; right:20%; animation:float 5s ease-in-out infinite 0.5s; }
""" + "</style>", unsafe_allow_html=True)
st.markdown("<style>" + """\
.app-nav { background: linear-gradient(135deg, #FFFFFF, #FFF5F7); border: 1px solid #E9ECEF; border-radius: 16px; padding: 6px 20px; margin-bottom: 16px; display: flex; align-items: center; justify-content: space-between; box-shadow: 0 2px 8px rgba(0,0,0,0.04); }
.nav-logo { font-size: 18px; font-weight: 700; color: #2D3436; display: flex; align-items: center; gap: 8px; }
.nav-logo i { color: #FF4757; font-size: 20px; }
.nav-user { font-size: 13px; color: #636E72; display: flex; align-items: center; gap: 6px; }
.nav-user i { font-size: 16px; color: #ADB5BD; }
div[data-testid="stRadio"] > div { display: flex; gap: 2px; flex-wrap: wrap; }
div[data-testid="stRadio"] label { background: transparent; border: none; padding: 6px 14px; border-radius: 8px; font-size: 13px; font-weight: 500; color: #636E72; cursor: pointer; transition: all 0.2s ease; }
div[data-testid="stRadio"] label:hover { background: rgba(255,71,87,0.06); color: #FF4757; }
div[data-testid="stRadio"] label[data-baseweb="radio"][aria-checked="true"] { background: linear-gradient(135deg,#FF4757,#FF6B81); color: white !important; font-weight: 600; }
div[data-testid="stRadio"] input { display: none; }
div[data-testid="stRadio"] label > div:first-child { display: none; }

.card, .goal-card, .stat-card, .profile-header, .notif-card { background: linear-gradient(135deg, #FFFFFF, #FAFBFF); border: 1px solid #E9ECEF; border-radius: 14px; padding: 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.03); transition: all 0.2s ease; }
.card:hover, .goal-card:hover, .notif-card:hover { border-color: #FF4757; box-shadow: 0 4px 16px rgba(255,71,87,0.08); }
.goal-card { padding: 16px; margin-bottom: 10px; }
.stat-card { padding: 20px 16px; text-align: center; margin-bottom: 12px; }
.stat-number { font-size: 32px; font-weight: 700; color: #FF4757; display: block; line-height: 1.2; }
.stat-label { font-size: 11px; color: #636E72; margin-top: 6px; text-transform: uppercase; letter-spacing: 0.06em; font-weight: 600; }
.avatar { width: 36px; height: 36px; border-radius: 50%; background: #E1F5EE; color: #0F6E56; display: inline-flex; align-items: center; justify-content: center; font-weight: 600; font-size: 12px; flex-shrink: 0; }
.avatar-purple { background: #EEEDFE; color: #534AB7; }
.avatar-coral  { background: #FAECE7; color: #993C1D; }
.avatar-amber  { background: #FAEEDA; color: #854F0B; }
.profile-avatar { width: 72px; height: 72px; border-radius: 50%; background: #E1F5EE; color: #0F6E56; display: flex; align-items: center; justify-content: center; font-size: 28px; font-weight: 700; margin: 0 auto 14px; border: 3px solid #9FE1CB; }
.section-label { font-size: 11px; font-weight: 600; color: #636E72; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 10px; }
.feed-section-label { font-size: 11px; font-weight: 600; color: #636E72; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 8px; margin-top: 20px; }
.feed-allclear { font-size: 13px; color: #636E72; padding: 4px 0 12px; }
.feed-allclear i { color: #2ED573; margin-right: 6px; }
.streak-pill { background: #FFF3E0; color: #E65100; font-size: 11px; font-weight: 600; padding: 4px 10px; border-radius: 20px; white-space: nowrap; border: 1px solid #FFB74D; display: inline-flex; align-items: center; gap: 4px; }
.category-badge { display: inline-block; padding: 3px 10px; border-radius: 20px; font-size: 11px; font-weight: 600; background: #EEEDFE; color: #534AB7; border: 1px solid #D0C9F5; margin-bottom: 8px; }
.sentiment-chip { display: inline-flex; align-items: center; gap: 4px; padding: 2px 10px; border-radius: 20px; font-size: 11px; font-weight: 500; }
.sentiment-motivated  { background: #E1F5EE; color: #0F6E56; border: 1px solid #9FE1CB; }
.sentiment-struggling { background: #FCEBEB; color: #A32D2D; border: 1px solid #F09595; }
.sentiment-neutral    { background: #F8F9FA; color: #636E72; border: 1px solid #DEE2E6; }
.at-risk-row { display: flex; align-items: center; gap: 10px; background: #FFF3E0; border: 1px solid #FFB74D; border-radius: 10px; padding: 10px 14px; margin-bottom: 8px; }
.at-risk-avatar { width: 32px; height: 32px; font-size: 11px; }
.at-risk-name { font-size: 13px; font-weight: 600; color: #854F0B; }
.at-risk-goals { font-size: 11px; color: #BF6A00; }
.feed-card { padding: 14px 0; border-bottom: 1px solid #F0F0F0; }
.feed-row { display: flex; gap: 10px; align-items: flex-start; }
.feed-avatar { width: 32px; height: 32px; font-size: 11px; margin-top: 2px; }
.feed-body { flex: 1; min-width: 0; }
.feed-head { display: flex; align-items: center; gap: 4px; flex-wrap: wrap; font-size: 13px; margin-bottom: 4px; }
.feed-user { font-weight: 600; color: #2D3436; }
.feed-sep { color: #ADB5BD; font-size: 10px; }
.feed-goal { color: #636E72; }
.feed-time { color: #ADB5BD; font-size: 12px; }
.feed-caption { font-size: 13px; color: #636E72; line-height: 1.5; margin-bottom: 6px; font-style: italic; }
.feed-foot { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }
.feed-streak { font-size: 12px; color: #E65100; font-weight: 600; display: inline-flex; align-items: center; gap: 3px; }
.feed-reactions { font-size: 12px; color: #ADB5BD; display: inline-flex; align-items: center; gap: 3px; }
.verified-icon { color: #2ED573; font-size: 12px; margin-left: 2px; }
.action-btn-joined { background: #E1F5EE; color: #0F6E56; border-color: #9FE1CB; }
.profile-header { padding: 28px; text-align: center; margin-bottom: 20px; }
.notif-card { padding: 12px 14px; margin-bottom: 8px; display: flex; align-items: flex-start; gap: 10px; }
.notif-icon { width: 34px; height: 34px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 15px; flex-shrink: 0; }
.ai-message-user { background: #FF4757; color: white; border-radius: 16px 16px 4px 16px; padding: 10px 14px; font-size: 13px; margin: 6px 0; max-width: 80%; margin-left: auto; line-height: 1.5; }
.ai-message-bot { background: white; border: 1px solid #E9ECEF; border-radius: 16px 16px 16px 4px; padding: 10px 14px; font-size: 13px; margin: 6px 0; max-width: 85%; line-height: 1.5; }
div[data-testid="stButton"] button { background: linear-gradient(135deg, #FF4757, #FF6B81) !important; color: white !important; border: none !important; border-radius: 10px !important; font-weight: 600 !important; font-size: 13px !important; padding: 8px 18px !important; transition: all 0.2s !important; }
div[data-testid="stButton"] button:hover { background: linear-gradient(135deg, #E63946, #FF4757) !important; }
button[key="logout_btn"] { background: white !important; color: #ADB5BD !important; border: 1px solid #DEE2E6 !important; padding: 4px 14px !important; font-size: 12px !important; font-weight: 500 !important; border-radius: 8px !important; }
button[key="logout_btn"]:hover { color: #FF4757 !important; border-color: #FF4757 !important; }
.stTextInput input, .stTextArea textarea { background: #F8F9FA !important; border: 1px solid #DEE2E6 !important; border-radius: 10px !important; color: #2D3436 !important; font-size: 13px !important; }
.stTextInput input:focus, .stTextArea textarea:focus { border-color: #FF4757 !important; background: white !important; }
.stTabs [data-baseweb="tab"] { font-size: 13px; font-weight: 500; color: #636E72; }
.stTabs [aria-selected="true"] { color: #FF4757 !important; border-bottom-color: #FF4757 !important; }
div[data-testid="metric-container"] { background: white; border: 1px solid #E9ECEF; border-radius: 14px; padding: 16px; }
div[data-testid="stSelectbox"] label { display: none !important; }
div[data-testid="stSelectbox"] { margin-bottom: 0 !important; }
div[data-testid="stSelectbox"] div[data-baseweb="select"] { background: white; border: 1px solid #E9ECEF; border-radius: 8px; }
button[data-testid="stPasswordVisibilityToggle"] { display: none !important; }
[data-testid="stPasswordVisibilityToggle"] { display: none !important; }
input[type="password"]::-ms-reveal { display: none !important; }
input[type="password"]::-ms-clear { display: none !important; }
input[type="password"]::-webkit-credentials-auto-fill-button { display: none !important; }
input[type="password"]::-webkit-text-security { display: none !important; }
""" + "</style><img src onerror=\"var t=setInterval(function(){document.querySelectorAll('[data-testid=\\'stPasswordVisibilityToggle\\']').forEach(function(e){e.style.display='none';e.style.width='0';e.style.height='0';e.style.overflow='hidden';e.style.padding='0';e.style.margin='0';e.style.border='0';})},200);setTimeout(function(){clearInterval(t)},15000)\" style=\"display:none\">", unsafe_allow_html=True)

for k, v in [("user_id", None), ("username", None), ("show_notifs", False), ("chat_history", []), ("stay_logged_in", False)]:
    if k not in st.session_state:
        st.session_state[k] = v

if st.session_state.user_id is None:
    qp = st.query_params
    if "uid" in qp and "uname" in qp:
        try:
            uid = int(qp["uid"])
            db = SessionLocal()
            exists = db.query(User).filter(User.id == uid, User.username == qp["uname"]).first()
            db.close()
            if exists:
                st.session_state.user_id = uid
                st.session_state.username = qp["uname"]
        except (ValueError, TypeError):
            pass

def initials(u):
    return u[:2].upper() if u else "??"

def get_notifications(user_id):
    db = SessionLocal()
    today = date.today()
    notifs = []
    nudges = db.query(Nudge).filter(
        Nudge.receiver_id == user_id,
        Nudge.created_at >= datetime(today.year, today.month, today.day)
    ).all()
    for n in nudges:
        sender = db.query(User).filter(User.id == n.sender_id).first()
        group = db.query(StreakGroup).filter(StreakGroup.id == n.streak_group_id).first()
        if sender and group:
            notifs.append({
                "icon": "<i class='fas fa-hand-wave'></i>", "color": "#FFF3E0",
                "title": f"@{sender.username} nudged you!",
                "body": f"Don't forget to check in for {group.goal.title if group.goal else 'your group'} today"
            })
    my_checkins = db.query(CheckIn).filter(
        CheckIn.user_id == user_id,
        CheckIn.created_at >= datetime(today.year, today.month, today.day)
    ).all()
    for c in my_checkins:
        reactions = db.query(Reaction).filter(Reaction.checkin_id == c.id).count()
        if reactions > 0:
            notifs.append({
                "icon": "<i class='fas fa-fire'></i>", "color": "#FFF3E0",
                "title": f"{reactions} reaction{'s' if reactions > 1 else ''} on your check-in",
                "body": "People are loving your progress!"
            })
    memberships = db.query(StreakMember).filter(StreakMember.user_id == user_id).all()
    for m in memberships:
        group = db.query(StreakGroup).filter(StreakGroup.id == m.streak_group_id).first()
        if not group:
            continue
        members = db.query(StreakMember).filter(StreakMember.streak_group_id == m.streak_group_id).all()
        missing = []
        for mem in members:
            if mem.user_id == user_id:
                continue
            checked = db.query(CheckIn).filter(
                CheckIn.user_id == mem.user_id,
                CheckIn.streak_group_id == m.streak_group_id,
                CheckIn.created_at >= datetime(today.year, today.month, today.day)
            ).first()
            if not checked:
                u = db.query(User).filter(User.id == mem.user_id).first()
                if u:
                    missing.append(u.username)
        if missing:
            notifs.append({
                "icon": "<i class='fas fa-exclamation-triangle'></i>", "color": "#FCEBEB",
                "title": f"{len(missing)} member{'s' if len(missing) > 1 else ''} haven't checked in",
                "body": f"@{', @'.join(missing[:3])} in {group.goal.title if group.goal else 'your group'}"
            })
    db.close()
    return notifs

def render_login():
    st.markdown(f"""<div style='position:fixed;top:0;left:0;width:100%;height:100%;z-index:-2;background:linear-gradient(135deg,rgba(248,249,250,0.85),rgba(255,255,255,0.8)),url("{IMG_LOGIN}");background-size:cover;background-position:center;background-attachment:fixed'></div>""", unsafe_allow_html=True)
    st.markdown("""
    <div style='display:flex;align-items:center;justify-content:space-between;padding:16px 0;margin-bottom:8px'>
        <div style='font-size:22px;font-weight:700;color:#2D3436;display:flex;align-items:center;gap:10px'>
            <i class='fas fa-fire' style='color:#FF4757'></i> Strive
        </div>
        <div style='display:flex;gap:24px'>
            <a href='#how-it-works' style='color:#636E72;text-decoration:none;font-size:14px;font-weight:500;transition:color 0.2s' onmouseover='this.style.color="#FF4757"' onmouseout='this.style.color="#636E72"'>How It Works</a>
            <a href='#get-started' style='color:white;text-decoration:none;font-size:14px;font-weight:600;background:linear-gradient(135deg,#FF4757,#FF6B81);padding:6px 20px;border-radius:10px;transition:all 0.2s' onmouseover='this.style.background="linear-gradient(135deg,#E63946,#FF4757)"' onmouseout='this.style.background="linear-gradient(135deg,#FF4757,#FF6B81)"'>Get Started</a>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col_text, col_form = st.columns([1.15, 0.85], gap="large")
    with col_text:
        st.markdown("""
        <div style='padding:40px 0'>
            <div style='display:inline-block;background:#FFF0F0;color:#FF4757;font-size:12px;font-weight:600;padding:6px 16px;border-radius:20px;margin-bottom:14px;letter-spacing:0.03em'>#1 Accountability Habit Tracker</div>
            <h1 style='font-size:48px;font-weight:800;color:#2D3436;margin:0;line-height:1.1;letter-spacing:-0.02em'>Strive</h1>
            <h2 style='font-size:48px;font-weight:800;margin:0 0 8px;line-height:1.1;letter-spacing:-0.02em;color:#FF4757'>For Your Goals.</h2>
            <p style='font-size:14px;color:#636E72;line-height:1.6;margin-bottom:20px;max-width:380px'>Stay consistent. Stay accountable with your team. Build streaks that matter.</p>
            <div style='display:flex;gap:12px;flex-wrap:wrap'>
                <div class='stat-item'><i class='fas fa-fire' style='color:#FF4757'></i> 4,200+ streaks</div>
                <div class='stat-item'><i class='fas fa-users' style='color:#7C5CFC'></i> 850+ groups</div>
                <div class='stat-item'><i class='fas fa-check-circle' style='color:#2ED573'></i> 12K+ check-ins</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_form:
        st.markdown("<div id='get-started'></div><div class='hero-form-card'><div class='form-header'><i class='fas fa-fire' style='color:#FF4757'></i> Welcome to Strive</div>", unsafe_allow_html=True)
        tab1, tab2 = st.tabs(["Sign In", "Create Account"])
        with tab1:
            email = st.text_input("Email", placeholder="you@example.com", key="l_email")
            password = st.text_input("Password", type="password", placeholder="Enter your password", key="l_pass")
            stay = st.checkbox("Stay logged in", key="stay_chk")
            if st.button("Sign In", use_container_width=True, key="signin_btn"):
                if not email or not password:
                    st.error("Please fill in all fields")
                else:
                    db = SessionLocal()
                    user = authenticate_user(db, email, password)
                    db.close()
                    if user:
                        st.session_state.user_id = user.id
                        st.session_state.username = user.username
                        st.session_state.stay_logged_in = stay
                        if stay:
                            st.query_params["uid"] = str(user.id)
                            st.query_params["uname"] = user.username
                        st.rerun()
                    else:
                        st.error("Invalid email or password")
            st.markdown("<div style='text-align:center; margin-top:6px'><a style='color:#ADB5BD; font-size:12px; text-decoration:none'>Forgot password?</a></div>", unsafe_allow_html=True)
            st.markdown("<hr style='margin:14px 0; border:none; border-top:1px solid #E9ECEF'>", unsafe_allow_html=True)
            st.markdown("<div style='font-size:12px; font-weight:600; color:#636E72; margin-bottom:8px; text-align:center'>Try a demo account</div>", unsafe_allow_html=True)
            demos = [
                ("demo@strive.app", "demo1234", "Demo", "#FF4757"),
                ("alice@strive.app", "alice1234", "Alice", "#7C5CFC"),
                ("bob@strive.app", "bob1234", "Bob", "#2ED573"),
                ("charlie@strive.app", "charlie1234", "Charlie", "#FFA502"),
                ("diana@strive.app", "diana1234", "Diana", "#2ED573"),
            ]
            cols = st.columns(len(demos))
            for i, (em, pw, name, color) in enumerate(demos):
                with cols[i]:
                    st.markdown(f"<div class='demo-card'><div class='demo-avatar' style='background:{color}20;color:{color}'>{name[0]}</div><div class='demo-name'>{name}</div><div class='demo-email'>{em}</div></div>", unsafe_allow_html=True)
                    if st.button("Go", key=f"demo_{i}", use_container_width=True):
                        db = SessionLocal()
                        user = authenticate_user(db, em, pw)
                        db.close()
                        if user:
                            st.session_state.user_id = user.id
                            st.session_state.username = user.username
                            st.session_state.stay_logged_in = True
                            st.query_params["uid"] = str(user.id)
                            st.query_params["uname"] = user.username
                            st.rerun()

        with tab2:
            username = st.text_input("Username", placeholder="e.g. strive_warrior", key="s_user")
            email2 = st.text_input("Email", placeholder="you@example.com", key="s_email")
            password2 = st.text_input("Password", type="password", placeholder="Create a strong password", key="s_pass")
            col_agree = st.columns([1, 12])
            with col_agree[0]:
                agree = st.checkbox("Agree to terms", label_visibility="collapsed", key="terms_check")
            with col_agree[1]:
                st.markdown("<span style='font-size:12px; color:#636E72'>I agree to the Terms & Privacy Policy</span>", unsafe_allow_html=True)
            if st.button("Create Account", use_container_width=True, key="signup_btn"):
                if not username or not email2 or not password2:
                    st.error("Please fill in all fields")
                elif not agree:
                    st.error("Please agree to the terms")
                else:
                    db = SessionLocal()
                    ok, msg, user = create_user(db, username, email2, password2)
                    db.close()
                if ok and user:
                    st.success(msg)
                    st.session_state.user_id = user.id
                    st.session_state.username = user.username
                    st.session_state.stay_logged_in = True
                    st.query_params["uid"] = str(user.id)
                    st.query_params["uname"] = user.username
                    st.rerun()
                else:
                    st.error(msg)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<hr style='border:none; border-top:1px solid #E9ECEF; margin:48px 0 28px' id='how-it-works'>", unsafe_allow_html=True)
    st.markdown("<h2 class='section-title'>How It Works</h2>", unsafe_allow_html=True)
    st.markdown("<p class='section-desc'>Start your streak journey in four simple steps</p>", unsafe_allow_html=True)

    step_imgs = [IMG_VISION, IMG_CODE, IMG_FOCUS, IMG_SLEEP]
    steps_data = [
        ("1", "Create Your Goal", "Set a personal or team goal \u2014 morning gym, daily reading, or any habit you want to build", "Start small \u2014 pick one habit you can realistically do daily. Studies show that tying your goal to an existing routine (like \u201Cafter my morning coffee\u201D) boosts follow-through by 40%."),
        ("2", "Join a Streak Group", "Find accountability partners working toward similar goals", "Groups of 3\u20135 work best. You\u2019re 65% more likely to meet a goal when you commit to someone. Share progress, cheer each other on, and keep the streak alive together."),
        ("3", "Check In Daily", "Log your progress with captions, photos, and your mood", "Consistency beats intensity. A 5-minute check-in daily builds momentum far faster than a 2-hour session once a week. Use photos to prove your progress and track your journey."),
        ("4", "Stay Consistent", "Build streaks, earn rewards, and let AI keep you motivated", "Every day you check in, your streak grows. Miss a day and it resets. Our AI Coach sends personalized motivation based on your mood and history to keep you on track.")
    ]
    if "step_expanded" not in st.session_state:
        st.session_state.step_expanded = -1
    cols = st.columns(4)
    for i, (num, title, desc, tip) in enumerate(steps_data):
        with cols[i]:
            expanded = st.session_state.step_expanded == i
            si = step_imgs[i]
            st.markdown(f"""
            <div class='step-card' {'id=step-' + str(i) if expanded else ''} style='position:relative;overflow:hidden'>
                <div style='position:absolute;top:0;left:0;width:100%;height:100%;background:linear-gradient(180deg,rgba(255,255,255,0.3),rgba(255,255,255,0.5)),url("{si}");background-size:cover;background-position:center;opacity:0.25;z-index:0'></div>
                <div style='position:relative;z-index:1'>
                    <div class='step-number'>{num}</div>
                    <div class='step-title'>{title}</div>
                    <div class='step-desc'>{desc if not expanded else tip}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Learn more" if not expanded else "Show less", key=f"step_{i}", use_container_width=True):
                st.session_state.step_expanded = i if not expanded else -1
                st.rerun()

    st.markdown("""
    <div class='landing-footer'>
        <div class='footer-col'>
            <div class='footer-brand'><i class='fas fa-fire' style='color:#FF4757'></i> Strive</div>
            <div class='footer-text'>Stay consistent. Stay accountable.</div>
        </div>
        <div class='footer-col'>
            <div class='footer-heading'>Product</div>
            <a href='#how-it-works' class='footer-link'>How It Works</a>
            <a class='footer-link'>Features</a>
            <a class='footer-link'>FAQ</a>
        </div>
        <div class='footer-col'>
            <div class='footer-heading'>Company</div>
            <a class='footer-link'>About</a>
            <a class='footer-link'>Blog</a>
            <a class='footer-link'>Contact</a>
        </div>
        <div class='footer-col'>
            <div class='footer-heading'>Legal</div>
            <a class='footer-link'>Privacy</a>
            <a class='footer-link'>Terms</a>
        </div>
    </div>
    <div class='footer-bottom'>Strive &copy; 2026</div>
    """, unsafe_allow_html=True)

def render_feed():
    notifs = get_notifications(st.session_state.user_id)
    notif_count = len(notifs)
    today = date.today()
    day_name = today.strftime("%A")
    date_str = today.strftime("%b %d")

    st.markdown(f"""
    <div style='margin-bottom:20px;position:relative;overflow:hidden;border-radius:16px;padding:18px 20px;background:linear-gradient(135deg,rgba(248,249,250,0.75),rgba(255,255,255,0.8)),url("{IMG_CODE}");background-size:cover;background-position:center;display:flex;align-items:center;justify-content:space-between'>
        <div><span style='font-size:13px;color:#636E72'>{day_name}</span><br><span style='font-size:22px;font-weight:700;color:#2D3436'>Activity Feed</span></div>
        <button onclick='alert("notifs toggle coming soon")' style='background:{"#FF4757" if notif_count else "#F8F9FA"};color:{"white" if notif_count else "#636E72"};border:none;border-radius:8px;padding:6px 12px;cursor:pointer;position:relative;font-size:14px'>
            <i class='fas fa-bell'></i>{" <span style=\"background:white;color:#FF4757;font-size:10px;font-weight:700;padding:1px 5px;border-radius:6px;margin-left:2px\">" + str(notif_count) + "</span>" if notif_count else ""}
        </button>
    </div>""", unsafe_allow_html=True)

    if st.button(f"Notifications ({notif_count})" if notif_count else "No notifications", key="bell"):
        st.session_state.show_notifs = not st.session_state.show_notifs

    if st.session_state.show_notifs:
        st.markdown(f"<div class='section-label'>Notifications ({notif_count})</div>", unsafe_allow_html=True)
        if not notifs:
            st.markdown("<div style='text-align:center; padding:20px; color:#ADB5BD; font-size:13px'>All caught up!</div>", unsafe_allow_html=True)
        for n in notifs:
            st.markdown(f"""
            <div class='notif-card'>
                <div class='notif-icon' style='background:{n["color"]}'>{n["icon"]}</div>
                <div>
                    <div style='font-size:13px; font-weight:600; color:#2D3436'>{n["title"]}</div>
                    <div style='font-size:12px; color:#636E72; margin-top:2px'>{n["body"]}</div>
                </div>
            </div>""", unsafe_allow_html=True)

    db = SessionLocal()
    memberships = db.query(StreakMember).filter(StreakMember.user_id == st.session_state.user_id).all()
    group_ids = [m.streak_group_id for m in memberships]
    if not group_ids:
        st.markdown("""
        <div style='text-align:center; padding:60px 20px'>
            <div style='font-size:48px; color:#FF4757'><i class='fas fa-bullseye'></i></div>
            <h3 style='color:#2D3436'>No streak groups yet</h3>
            <p style='color:#636E72'>Head to Goals to join or create a streak group</p>
        </div>""", unsafe_allow_html=True)
        db.close()
        return

    today = date.today()
    st.markdown("<div class='feed-section-label'>Needs attention</div>", unsafe_allow_html=True)
    at_risk = {}
    for gid in group_ids:
        group = db.query(StreakGroup).filter(StreakGroup.id == gid).first()
        if not group:
            continue
        for m in db.query(StreakMember).filter(StreakMember.streak_group_id == gid).all():
            if m.user_id == st.session_state.user_id:
                continue
            checked = db.query(CheckIn).filter(
                CheckIn.user_id == m.user_id,
                CheckIn.streak_group_id == gid,
                CheckIn.created_at >= datetime(today.year, today.month, today.day)
            ).first()
            if not checked:
                u = db.query(User).filter(User.id == m.user_id).first()
                if u:
                    if u.id not in at_risk:
                        at_risk[u.id] = {"user": u, "groups": []}
                    at_risk[u.id]["groups"].append(group.goal.title if group.goal else "Unknown")

    if not at_risk:
        st.markdown("<div class='feed-allclear'><i class='fas fa-check-circle'></i> Everyone has checked in today</div>", unsafe_allow_html=True)
    else:
        for uid, info in at_risk.items():
            u = info["user"]
            goals_str = ", ".join(info["groups"])
            col_a, col_b = st.columns([6, 2])
            with col_a:
                st.markdown(f"""
                <div class='at-risk-row'>
                    <div class='avatar at-risk-avatar'>{initials(u.username)}</div>
                    <div>
                        <div class='at-risk-name'>@{u.username}</div>
                        <div class='at-risk-goals'>Missed: {goals_str}</div>
                    </div>
                </div>""", unsafe_allow_html=True)
            with col_b:
                if st.button("Send Nudge", key=f"nudge_{uid}"):
                    for gid in group_ids:
                        group = db.query(StreakGroup).filter(StreakGroup.id == gid).first()
                        if group and group.goal and group.goal.title in info["groups"]:
                            db.add(Nudge(sender_id=st.session_state.user_id, receiver_id=uid, streak_group_id=gid))
                    db.commit()
                    st.success(f"Nudge sent to @{u.username}!")
                    st.rerun()

    checkins = db.query(CheckIn).filter(
        CheckIn.streak_group_id.in_(group_ids)
    ).order_by(CheckIn.created_at.desc()).limit(30).all()
    if not checkins:
        st.markdown("""
        <div style='text-align:center; padding:40px'>
            <div style='font-size:40px; color:#ADB5BD'><i class='fas fa-inbox'></i></div>
            <p style='color:#636E72'>No check-ins yet. Be the first!</p>
        </div>""", unsafe_allow_html=True)
        db.close()
        return

    from datetime import timedelta
    today_dt = date.today()
    yesterday_dt = today_dt - timedelta(days=1)
    date_groups = {}
    for c in checkins:
        c_date = c.created_at.date()
        if c_date == today_dt:
            key = "Today"
        elif c_date == yesterday_dt:
            key = "Yesterday"
        else:
            key = c.created_at.strftime("%b %d")
        date_groups.setdefault(key, []).append(c)

    for label in ["Today", "Yesterday"] + [k for k in date_groups if k not in ("Today", "Yesterday")]:
        items = date_groups.get(label)
        if not items:
            continue
        is_today = label == "Today"
        with st.expander(f"**{label}** ({len(items)})", expanded=is_today):
            for c in items:
                u = db.query(User).filter(User.id == c.user_id).first()
                group = db.query(StreakGroup).filter(StreakGroup.id == c.streak_group_id).first()
                goal = group.goal if group else None
                member = db.query(StreakMember).filter(
                    StreakMember.user_id == c.user_id,
                    StreakMember.streak_group_id == c.streak_group_id
                ).first()
                streak = member.current_streak if member else 0
                ini = initials(u.username) if u else "??"
                sentiment = c.sentiment or "neutral"
                s_icon = "fa-rocket" if sentiment == "motivated" else "fa-frown" if sentiment == "struggling" else "fa-meh"
                flames = db.query(Reaction).filter(Reaction.checkin_id == c.id, Reaction.type == "flame").count()
                verified_icon = ' <i class="fas fa-check-circle verified-icon"></i>' if c.verified else ""
                time_str = c.created_at.strftime("%I:%M %p").lstrip("0")
                st.markdown(f"""
                <div class='feed-card'>
                    <div class='feed-row'>
                        <div class='avatar feed-avatar'>{ini}</div>
                        <div class='feed-body'>
                            <div class='feed-head'>
                                <span class='feed-user'>@{u.username if u else 'unknown'}{verified_icon}</span>
                                <span class='feed-sep'>&middot;</span>
                                <span class='feed-goal'>{goal.title if goal else 'Unknown'}</span>
                                <span class='feed-sep'>&middot;</span>
                                <span class='feed-time'>{time_str}</span>
                            </div>
                            <div class='feed-caption'>"{c.caption}"</div>
                            <div class='feed-foot'>
                                <span class='sentiment-chip sentiment-{sentiment}'><i class='fas {s_icon}'></i>{sentiment}</span>
                                <span class='feed-streak'><i class='fas fa-fire'></i>{streak}d</span>
                                <span class='feed-reactions'><i class='fas fa-fire'></i>{flames}</span>
                            </div>
                        </div>
                    </div>
                </div>""", unsafe_allow_html=True)
                col1, col2, col3 = st.columns([1, 1, 1])
                with col1:
                    if st.button(f"React ({flames})", key=f"react_{c.id}"):
                        db.add(Reaction(user_id=st.session_state.user_id, checkin_id=c.id, type="flame"))
                        db.commit()
                        st.rerun()
                with col2:
                    if st.button("Comment", key=f"comment_{c.id}"):
                        st.info("Comments coming soon")
                        st.rerun()
                with col3:
                    if st.button("Nudge", key=f"nudge_card_{c.id}"):
                        if c.user_id == st.session_state.user_id:
                            st.warning("Can't nudge yourself!")
                        else:
                            db.add(Nudge(sender_id=st.session_state.user_id, receiver_id=c.user_id, streak_group_id=c.streak_group_id))
                            db.commit()
                            st.success(f"Nudge sent to @{u.username}!")
                        st.rerun()
    db.close()

def render_checkin():
    today = date.today()
    day_name = today.strftime("%A")
    date_str = today.strftime("%b %d")
    db = SessionLocal()
    memberships = db.query(StreakMember).filter(StreakMember.user_id == st.session_state.user_id).all()
    if not memberships:
        st.info("Join a streak group first from the Goals page.")
        db.close()
        return
    cat_icons = {"Fitness":"fa-dumbbell","Coding":"fa-code","Reading":"fa-book-open","Meditation":"fa-spa","Study":"fa-graduation-cap","Sleep":"fa-bed","Productivity":"fa-tasks","Health":"fa-heartbeat","Mindfulness":"fa-brain","Learning":"fa-book","Creativity":"fa-palette","Finance":"fa-coins","Social":"fa-users","Other":"fa-star"}
    rows = []
    total = 0
    done = 0
    for m in memberships:
        group = db.query(StreakGroup).filter(StreakGroup.id == m.streak_group_id).first()
        if not group or not group.goal:
            continue
        total += 1
        cat = group.goal.category
        icon = cat_icons.get(cat, "fa-star")
        checked = db.query(CheckIn).filter(
            CheckIn.user_id == st.session_state.user_id,
            CheckIn.streak_group_id == group.id,
            CheckIn.created_at >= datetime(today.year, today.month, today.day)
        ).first()
        if checked:
            done += 1
        rows.append((group.id, group.goal.title, cat, icon, m.current_streak, m.longest_streak, checked))
    pct = int((done / total) * 100) if total > 0 else 0

    st.markdown(f"""
    <div style='margin-bottom:20px;position:relative;overflow:hidden;border-radius:16px;padding:20px;background:linear-gradient(135deg,rgba(255,255,255,0.7),rgba(248,249,250,0.75)),url("{IMG_VISION}");background-size:cover;background-position:center'>
        <div style='display:flex;align-items:center;justify-content:space-between;position:relative;z-index:1'>
            <div><span style='font-size:14px;color:#636E72'>{day_name}</span><br><span style='font-size:24px;font-weight:700;color:#2D3436'>{date_str}</span></div>
            <div style='text-align:right'>
                <span style='font-size:13px;color:#636E72'>Today's Progress</span><br>
                <span style='font-size:22px;font-weight:700;color:#FF4757'>{done}</span><span style='font-size:14px;color:#ADB5BD'>/{total}</span>
            </div>
        </div>
        <div style='margin-top:12px;background:rgba(0,0,0,0.08);border-radius:10px;height:6px;overflow:hidden;position:relative;z-index:1'>
            <div style='width:{pct}%;height:100%;background:linear-gradient(90deg,#FF4757,#FF6B81);border-radius:10px;transition:width 0.5s'></div>
        </div>
    </div>""", unsafe_allow_html=True)

    for gid, title, cat, icon, streak, longest, checked in rows:
        checked_in = checked is not None
        st.markdown(f"""
        <div style='background:white;border:1px solid {("#E9ECEF","#2ED573")[checked_in]};border-radius:12px;padding:12px 16px;margin-bottom:8px;display:flex;align-items:center;gap:12px'>
            <div style='width:38px;height:38px;border-radius:10px;background:{"#E1F5EE" if not checked_in else "#D4EDDA"};display:flex;align-items:center;justify-content:center;flex-shrink:0'>
                <i class='fas {icon}' style='font-size:16px;color:{"#0F6E56" if not checked_in else "#155724"}'></i>
            </div>
            <div style='flex:1;min-width:0'>
                <div style='font-size:14px;font-weight:600;color:#2D3436'>{title}</div>
                <div style='display:flex;align-items:center;gap:8px;margin-top:2px'>
                    <span style='font-size:11px;color:#636E72'>{cat}</span>
                    <span style='font-size:11px;color:#E65100'><i class='fas fa-fire'></i> {streak}d</span>
                    <span style='font-size:11px;color:#ADB5BD'>best {longest}d</span>
                </div>
            </div>
            <div style='display:flex;align-items:center;gap:6px;flex-shrink:0'>
                <span style='font-size:20px;color:{"#2ED573" if checked_in else "#ADB5BD"};transition:all 0.2s'><i class='fas {"fa-check-circle" if checked_in else "fa-circle"}'></i></span>
            </div>
        </div>""", unsafe_allow_html=True)

    if not any(not r[6] for r in rows):
        st.markdown("<div style='text-align:center;padding:20px 0;color:#2ED573;font-size:14px'><i class='fas fa-check-circle'></i> All done for today!</div>", unsafe_allow_html=True)

    st.markdown("<div style='margin:16px 0 8px;font-size:12px;font-weight:600;color:#636E72;text-transform:uppercase;letter-spacing:0.06em'>Quick Check-in</div>", unsafe_allow_html=True)
    sel_opts = [f"{title}" for gid, title, cat, icon, streak, longest, checked in rows if not checked]
    if sel_opts:
        selected = st.selectbox("Select habit", sel_opts, label_visibility="collapsed", key="checkin_select")
        caption = st.text_area("What did you do?", placeholder="e.g. Ran 5km — felt amazing!", key="checkin_caption", label_visibility="collapsed")
        with st.expander("Add photo", expanded=False):
            col_upload, col_cam = st.columns(2)
            with col_upload:
                photo_file = st.file_uploader("Upload", type=["jpg", "jpeg", "png"], label_visibility="collapsed", key="checkin_photo")
            with col_cam:
                photo_cam = st.camera_input("Camera", label_visibility="collapsed", key="checkin_cam")
        photo_data = None
        if photo_cam is not None:
            photo_data = base64.b64encode(photo_cam.getvalue()).decode()
        elif photo_file is not None:
            photo_data = base64.b64encode(photo_file.getvalue()).decode()
        col_mood, col_submit = st.columns([1, 1])
        with col_mood:
            mood = st.select_slider("", options=["Struggling", "Okay", "Motivated"], value="Okay", label_visibility="collapsed")
        with col_submit:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Check In", use_container_width=True, key="checkin_submit"):
                gid = None
                cat = None
                for gid_, title_, cat_, icon_, streak_, longest_, checked_ in rows:
                    if title_ == selected:
                        gid = gid_
                        cat = cat_
                        break
                if gid:
                    from services.nlp_service import analyze_sentiment, get_motivation_message
                    from services.rewards_service import check_and_award_all
                    existing = db.query(CheckIn).filter(
                        CheckIn.user_id == st.session_state.user_id,
                        CheckIn.streak_group_id == gid,
                        CheckIn.created_at >= datetime(today.year, today.month, today.day)
                    ).first()
                    if existing:
                        st.warning("Already checked in!")
                    else:
                        sentiment = "motivated" if "Motivated" in mood else "struggling" if "Struggling" in mood else "neutral"
                        if caption:
                            sentiment, score = analyze_sentiment(caption)
                        img_url = f"data:image/jpeg;base64,{photo_data}" if photo_data else None
                        db.add(CheckIn(user_id=st.session_state.user_id, streak_group_id=gid, caption=caption, image_url=img_url, sentiment=sentiment, sentiment_score=score if caption else 0.5, verified=False))
                        member = db.query(StreakMember).filter(StreakMember.user_id == st.session_state.user_id, StreakMember.streak_group_id == gid).first()
                        if member:
                            member.current_streak += 1
                            if member.current_streak > member.longest_streak:
                                member.longest_streak = member.current_streak
                        db.commit()
                        new_rewards = check_and_award_all(db, st.session_state.user_id)
                        msg = get_motivation_message(sentiment, member.current_streak if member else 1)
                        st.success(msg)
                        for reward in new_rewards:
                            st.markdown(f"<div style='background:#E1F5EE;border:1px solid #9FE1CB;border-radius:10px;padding:10px 14px;margin-bottom:6px'><span style='font-size:18px;margin-right:8px'>{reward['emoji']}</span><strong>{reward['title']}</strong> <span style='color:#0F6E56'>+{reward['points']} points!</span></div>", unsafe_allow_html=True)
                        st.balloons()
                        st.rerun()
    else:
        st.info("All caught up! Create a new goal to track more.")
    db.close()

def render_goals():
    st.markdown(f"""
    <div style='margin-bottom:20px;position:relative;overflow:hidden;border-radius:16px;padding:20px;background:linear-gradient(135deg,rgba(248,249,250,0.7),rgba(255,255,255,0.75)),url("{IMG_VISION}");background-size:cover;background-position:center'>
        <div style='position:relative;z-index:1'><span style='font-size:13px;color:#636E72'>Create & Join</span><br><span style='font-size:22px;font-weight:700;color:#2D3436'>Goals</span></div>
    </div>""", unsafe_allow_html=True)
    db = SessionLocal()
    tab1, tab2 = st.tabs(["Discover", "Create New"])
    with tab1:
        goals = db.query(Goal).filter(Goal.visibility == "public").all()
        if not goals:
            st.markdown("""
            <div style='text-align:center; padding:40px'>
                <div style='font-size:40px; color:#2ED573'><i class='fas fa-seedling'></i></div>
                <p style='color:#636E72'>No public goals yet — be the first!</p>
            </div>""", unsafe_allow_html=True)
        for g in goals:
            group = g.streak_group
            already = db.query(StreakMember).filter(
                StreakMember.user_id == st.session_state.user_id,
                StreakMember.streak_group_id == (group.id if group else 0)
            ).first()
            cat_goal_imgs = {"Gym": IMG_GYM, "Fitness": IMG_GYM, "Coding": IMG_CODE, "Study": IMG_STUDY, "Reading": IMG_STUDY, "Meditation": IMG_FOCUS, "Focus": IMG_FOCUS, "Sleep": IMG_SLEEP}
            gimg = cat_goal_imgs.get(g.category, IMG_VISION)
            st.markdown(f"""
            <div class='goal-card' style='position:relative;overflow:hidden'>
                <div style='position:absolute;top:0;left:0;width:100%;height:100%;background:linear-gradient(135deg,rgba(255,255,255,0.6),rgba(255,255,255,0.75)),url("{gimg}");background-size:cover;background-position:center;opacity:0.5;z-index:0'></div>
                <div style='position:relative;z-index:1'>
                    <span class='category-badge'>{g.category}</span>
                    <div style='font-size:15px; font-weight:600; color:#2D3436; margin-bottom:6px'>{g.title}</div>
                    <div style='font-size:13px; color:#636E72; margin-bottom:12px'>{g.description or 'No description provided.'}</div>
                    <div style='display:flex; gap:16px; font-size:12px; color:#ADB5BD'>
                        <span><i class='fas fa-users'></i> {group.member_count if group else 0} members</span>
                        <span><i class='fas fa-fire'></i> {group.current_streak if group else 0} day streak</span>
                        <span><i class='fas fa-bullseye'></i> {g.target_duration} day goal</span>
                    </div>
                </div>
            </div>""", unsafe_allow_html=True)
            if already:
                st.markdown("<div class='action-btn action-btn-joined' style='text-align:center; padding:8px; border-radius:8px; margin-bottom:8px'><i class='fas fa-check-circle' style='margin-right:4px'></i>Already joined</div>", unsafe_allow_html=True)
            elif group:
                if st.button("Join Group", key=f"join_{g.id}"):
                    db.add(StreakMember(user_id=st.session_state.user_id, streak_group_id=group.id))
                    group.member_count += 1
                    db.commit()
                    st.success(f"Joined '{g.title}'!")
                    st.rerun()
    with tab2:
        st.markdown("<div class='section-label'>Create a new streak goal</div>", unsafe_allow_html=True)
        title = st.text_input("Goal title", placeholder="e.g. Morning gym every day")
        description = st.text_area("Description", placeholder="What is this goal about?")
        col1, col2 = st.columns(2)
        with col1:
            category = st.selectbox("Category", GOAL_CATEGORIES)
        with col2:
            target = st.slider("Target duration (days)", 7, 365, 30)
        visibility = st.radio("Visibility", ["public", "private"], horizontal=True)
        if st.button("Create Goal", use_container_width=True):
            if not title:
                st.error("Please enter a title")
            else:
                goal = Goal(creator_id=st.session_state.user_id, title=title,
                            description=description, category=category,
                            target_duration=target, visibility=visibility)
                db.add(goal)
                db.flush()
                group = StreakGroup(goal_id=goal.id)
                db.add(group)
                db.flush()
                db.add(StreakMember(user_id=st.session_state.user_id, streak_group_id=group.id))
                db.commit()
                st.success(f"'{title}' created!")
                st.rerun()
    db.close()

def render_stats():
    st.markdown(f"""
    <div style='margin-bottom:20px;position:relative;overflow:hidden;border-radius:16px;padding:20px;background:linear-gradient(135deg,rgba(248,249,250,0.7),rgba(255,255,255,0.75)),url("{IMG_FOCUS}");background-size:cover;background-position:center'>
        <div style='position:relative;z-index:1'><span style='font-size:13px;color:#636E72'>Analytics</span><br><span style='font-size:22px;font-weight:700;color:#2D3436'>My Stats</span></div>
    </div>""", unsafe_allow_html=True)
    db = SessionLocal()
    memberships = db.query(StreakMember).filter(StreakMember.user_id == st.session_state.user_id).all()
    checkins = db.query(CheckIn).filter(CheckIn.user_id == st.session_state.user_id).all()
    best = max([m.longest_streak for m in memberships], default=0)
    current = max([m.current_streak for m in memberships], default=0)
    col1, col2, col3, col4 = st.columns(4)
    for col, num, label in [
        (col1, len(checkins), "Total Check-ins"),
        (col2, current, "Current Streak"),
        (col3, best, "Longest Streak"),
        (col4, len(memberships), "Active Groups")
    ]:
        with col:
            st.markdown(f"""
            <div class='stat-card'>
                <span class='stat-number'>{num}</span>
                <span class='stat-label'>{label}</span>
            </div>""", unsafe_allow_html=True)
    if checkins:
        import pandas as pd
        import plotly.express as px
        df = pd.DataFrame([{"date": c.created_at.date(), "sentiment": c.sentiment or "neutral"} for c in checkins])
        daily = df.groupby("date").size().reset_index(name="checkins")
        st.markdown("<div class='section-label' style='margin-top:20px'>Check-in history</div>", unsafe_allow_html=True)
        fig = px.area(daily, x="date", y="checkins", color_discrete_sequence=["#FF4757"])
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font_color="#636E72",
            xaxis=dict(gridcolor="#E9ECEF"),
            yaxis=dict(gridcolor="#E9ECEF"),
            margin=dict(l=0, r=0, t=20, b=0)
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("<div class='section-label'>Mood breakdown</div>", unsafe_allow_html=True)
        mood_counts = df["sentiment"].value_counts()
        fig2 = px.pie(
            values=mood_counts.values, names=mood_counts.index, hole=0.6,
            color_discrete_map={"motivated": "#2ED573", "neutral": "#7C5CFC", "struggling": "#FF4757"}
        )
        fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)", margin=dict(l=0, r=0, t=0, b=0))
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.markdown("""
        <div style='text-align:center; padding:40px'>
            <div style='font-size:40px; color:#ADB5BD'><i class='fas fa-inbox'></i></div>
            <p style='color:#636E72'>No check-ins yet. Start your first streak!</p>
        </div>""", unsafe_allow_html=True)
    db.close()

def generate_ai_response(message, context, current, best, total, motivated, struggling):
    msg = message.lower()
    if any(w in msg for w in ["analyse", "analyze", "summary", "progress", "how am i"]):
        consistency = round((motivated / total * 100) if total > 0 else 0)
        trend = "improving" if motivated > struggling else "needs attention"
        return (f"Here's your progress summary:\n\n"
                f"You've completed **{total} check-ins** total with a current streak of **{current} days**.\n\n"
                f"Your best ever streak is **{best} days** — that's your benchmark to beat!\n\n"
                f"Your mood trend is **{trend}** — {motivated} motivated vs {struggling} struggling check-ins.\n\n"
                f"Consistency score: **{consistency}%** motivated check-ins. "
                f"{'Keep it up!' if consistency > 60 else 'Focus on showing up even on tough days.'}")
    elif any(w in msg for w in ["motivat", "inspire", "keep going", "push", "encouragement"]):
        if current >= 14:
            return (f"{current} days straight?! You're not just building a habit — "
                    f"you're building an identity. Most people quit before day 7. "
                    f"You're already in the top 1%. Don't stop now!")
        elif current >= 7:
            return (f"One week and counting! Research shows habits start forming at day 21. "
                    f"You're already 1/3 of the way there. Keep pushing!")
        else:
            return (f"Every legend started at day 1. Don't focus on the streak number — "
                    f"focus on just showing up TODAY. One day at a time!")
    elif any(w in msg for w in ["suggest", "goal", "new", "try", "recommend"]):
        if total < 5:
            return ("Since you're just getting started, pick ONE simple goal. "
                    "Try **'Drink 2 litres of water daily'** — easy to prove and builds discipline fast!")
        elif current >= 7:
            return ("You're clearly consistent — time to level up! Consider adding a "
                    "**'Morning Pages'** streak — write 3 pages every morning.")
        else:
            return ("A **'Read 10 Pages Daily'** streak would complement your goals perfectly. "
                    "Only 15 minutes a day and 10 pages x 365 days = 12+ books a year!")
    elif any(w in msg for w in ["break", "broke", "miss", "failed", "quit", "give up"]):
        return ("Breaking a streak feels awful — but **one missed day doesn't erase your progress.** "
                "What matters is never missing twice. Make today non-negotiable!")
    elif any(w in msg for w in ["tired", "burnout", "exhausted", "hard", "difficult"]):
        return ("Burnout is real. Lower the bar temporarily — instead of a full workout, do 10 push-ups. "
                "The goal isn't perfection — it's not breaking the chain.")
    elif any(w in msg for w in ["reward", "points", "badge", "level"]):
        return (f"The Strive rewards system gives you points for every check-in, streak milestone, "
                f"nudge sent, and verified proof photo. Check the **Rewards** page to see your badges, "
                f"level progress, and leaderboard ranking!")
    else:
        return (f"As your AI coach, I'm here to help you stay consistent. "
                f"You currently have a {current}-day streak — let's keep building! "
                f"Try asking me to 'analyse my progress', 'motivate me', or 'suggest a new goal'.")

def render_ai_assistant():
    st.markdown(f"""
    <div style='margin-bottom:20px;position:relative;overflow:hidden;border-radius:16px;padding:20px;background:linear-gradient(135deg,rgba(248,249,250,0.7),rgba(255,255,255,0.75)),url("{IMG_CODE}");background-size:cover;background-position:center'>
        <div style='position:relative;z-index:1'><span style='font-size:13px;color:#636E72'>AI Assistant</span><br><span style='font-size:22px;font-weight:700;color:#2D3436'>Strive AI Coach</span></div>
    </div>""", unsafe_allow_html=True)
    db = SessionLocal()
    user = db.query(User).filter(User.id == st.session_state.user_id).first()
    memberships = db.query(StreakMember).filter(StreakMember.user_id == st.session_state.user_id).all()
    checkins = db.query(CheckIn).filter(CheckIn.user_id == st.session_state.user_id).all()
    best = max([m.longest_streak for m in memberships], default=0)
    current = max([m.current_streak for m in memberships], default=0)
    total = len(checkins)
    motivated = sum(1 for c in checkins if c.sentiment == "motivated")
    struggling = sum(1 for c in checkins if c.sentiment == "struggling")
    db.close()
    user_context = f"User: @{user.username if user else 'unknown'}, Streak: {current}, Best: {best}, Check-ins: {total}"
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Analyse my progress", use_container_width=True):
            st.session_state.chat_history.append({"role": "user", "content": "Can you analyse my progress?"})
    with col2:
        if st.button("Motivate me", use_container_width=True):
            st.session_state.chat_history.append({"role": "user", "content": "I need motivation to keep going!"})
    with col3:
        if st.button("Suggest a goal", use_container_width=True):
            st.session_state.chat_history.append({"role": "user", "content": "Suggest a new streak goal for me."})
    st.markdown("---")
    if not st.session_state.chat_history:
        st.markdown(f"""
        <div class='notif-card'>
            <div class='notif-icon' style='background:#E1F5EE; font-size:20px'><i class='fas fa-robot'></i></div>
            <div>
                <div style='font-size:13px; font-weight:600; color:#2D3436'>
                    Hey @{user.username if user else 'there'}! I'm your Strive AI Coach.
                </div>
                <div style='font-size:13px; color:#636E72; margin-top:4px'>
                    I can analyse your streak data, motivate you, suggest new goals,
                    and help you build better habits. Ask me anything!
                </div>
            </div>
        </div>""", unsafe_allow_html=True)
    else:
        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                st.markdown(f"""
                <div style='display:flex; justify-content:flex-end; margin:8px 0'>
                    <div class='ai-message-user'>{msg["content"]}</div>
                </div>""", unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style='display:flex; justify-content:flex-start; margin:8px 0'>
                    <div class='ai-message-bot'><i class='fas fa-robot' style='margin-right:6px'></i>{msg["content"]}</div>
                </div>""", unsafe_allow_html=True)
    if st.session_state.chat_history and st.session_state.chat_history[-1]["role"] == "user":
        last_msg = st.session_state.chat_history[-1]["content"]
        response = generate_ai_response(last_msg, user_context, current, best, total, motivated, struggling)
        st.session_state.chat_history.append({"role": "assistant", "content": response})
        st.rerun()
    st.markdown("<br>", unsafe_allow_html=True)
    user_input = st.text_input("Ask your AI coach anything...",
                               placeholder="e.g. Why do I keep breaking my streaks?",
                               key="ai_input")
    col_send, col_clear = st.columns([3, 1])
    with col_send:
        if st.button("Send", use_container_width=True):
            if user_input.strip():
                st.session_state.chat_history.append({"role": "user", "content": user_input})
                st.rerun()
    with col_clear:
        if st.button("Clear chat", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()

def render_rewards():
    st.markdown(f"""
    <div style='margin-bottom:20px;position:relative;overflow:hidden;border-radius:16px;padding:20px;background:linear-gradient(135deg,rgba(248,249,250,0.7),rgba(255,255,255,0.75)),url("{IMG_VISION}");background-size:cover;background-position:center'>
        <div style='position:relative;z-index:1'><span style='font-size:13px;color:#636E72'>Earnings & Recognition</span><br><span style='font-size:22px;font-weight:700;color:#2D3436'>Rewards</span></div>
    </div>""", unsafe_allow_html=True)
    from services.rewards_service import (
        get_or_create_points, get_level, get_next_level,
        get_user_rewards, get_leaderboard, REWARDS, check_and_award_all
    )
    db = SessionLocal()
    check_and_award_all(db, st.session_state.user_id)
    points_obj = get_or_create_points(db, st.session_state.user_id)
    total_points = points_obj.total_points
    _, level, level_name, level_color = get_level(total_points)
    next_threshold, next_name, next_color = get_next_level(total_points)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class='stat-card'>
            <span class='stat-number'>{total_points}</span>
            <span class='stat-label'>Total Points</span>
        </div>""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class='stat-card'>
            <span class='stat-number'>{level_color} {level}</span>
            <span class='stat-label'>Current Level</span>
        </div>""", unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class='stat-card'>
            <span class='stat-number' style='font-size:22px'>{level_name}</span>
            <span class='stat-label'>Rank Title</span>
        </div>""", unsafe_allow_html=True)
    if next_threshold:
        progress = min(total_points / next_threshold, 1.0)
        points_needed = next_threshold - total_points
        st.markdown(f"""
        <div class='goal-card' style='margin-top:4px'>
            <div style='display:flex; justify-content:space-between; margin-bottom:8px'>
                <span style='font-size:13px; font-weight:600; color:#2D3436'>
                    Progress to {next_color} Level {level + 1} — {next_name}
                </span>
                <span style='font-size:12px; color:#636E72'>{points_needed} points to go</span>
            </div>
            <div style='background:#F8F9FA; border-radius:20px; height:10px; overflow:hidden'>
                <div style='background:#FF4757; width:{int(progress*100)}%; height:100%; border-radius:20px'></div>
            </div>
            <div style='font-size:11px; color:#ADB5BD; margin-top:6px'>{int(progress*100)}% of the way there</div>
        </div>""", unsafe_allow_html=True)
    st.markdown("---")
    tab1, tab2, tab3 = st.tabs(["My Badges", "All Rewards", "Leaderboard"])
    with tab1:
        user_rewards = get_user_rewards(db, st.session_state.user_id)
        if not user_rewards:
            st.markdown("""
            <div style='text-align:center; padding:40px'>
                <div style='font-size:48px; color:#FF4757'><i class='fas fa-bullseye'></i></div>
                <h3 style='color:#2D3436'>No badges yet!</h3>
                <p style='color:#636E72'>Start checking in to earn your first reward</p>
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='section-label'>{len(user_rewards)} rewards earned</div>", unsafe_allow_html=True)
            cols = st.columns(3)
            for i, r in enumerate(user_rewards):
                reward_info = REWARDS.get(r.reward_key, {})
                with cols[i % 3]:
                    st.markdown(f"""
                    <div class='stat-card' style='border:1px solid #9FE1CB; background:#E1F5EE22'>
                        <div style='font-size:32px'>{r.reward_emoji}</div>
                        <div style='font-size:13px; font-weight:600; color:#2D3436; margin-top:8px'>{r.reward_title}</div>
                        <div style='font-size:11px; color:#636E72; margin-top:4px'>{reward_info.get("desc", "")}</div>
                        <div style='font-size:12px; color:#2ED573; font-weight:600; margin-top:8px'>+{r.points_earned} pts</div>
                        <div style='font-size:10px; color:#ADB5BD; margin-top:4px'>{r.earned_at.strftime('%b %d, %Y')}</div>
                    </div>""", unsafe_allow_html=True)
    with tab2:
        user_rewards = get_user_rewards(db, st.session_state.user_id)
        earned_keys = {r.reward_key for r in user_rewards}
        categories = {
            "Streak Milestones": ["streak_3","streak_7","streak_14","streak_21","streak_30","streak_60","streak_100"],
            "Check-in Milestones": ["checkins_1","checkins_10","checkins_25","checkins_50","checkins_100"],
            "Social Rewards": ["first_nudge","nudge_5","joined_3_groups","joined_5_groups"],
            "Mood Rewards": ["motivated_10","motivated_25"],
            "Proof Rewards": ["verified_5","verified_20"],
            "Special": ["early_bird","consistency_7_days"],
        }
        for cat_title, keys in categories.items():
            st.markdown(f"<div class='section-label' style='margin-top:12px'>{cat_title}</div>", unsafe_allow_html=True)
            cols = st.columns(4)
            for i, key in enumerate(keys):
                if key not in REWARDS:
                    continue
                r = REWARDS[key]
                earned = key in earned_keys
                with cols[i % 4]:
                    st.markdown(f"""
                    <div class='stat-card' style='opacity:{"1" if earned else "0.4"};
                    border:{"1px solid #9FE1CB" if earned else "1px solid #E9ECEF"};
                    background:{"#E1F5EE22" if earned else "white"}'>
                        <div style='font-size:24px'>{r["emoji"]}{"" if earned else " <i class='fas fa-lock' style='color:#ADB5BD;font-size:16px'></i>"}</div>
                        <div style='font-size:12px; font-weight:600; color:#2D3436; margin-top:6px'>{r["title"]}</div>
                        <div style='font-size:10px; color:#636E72; margin-top:3px'>{r["desc"]}</div>
                        <div style='font-size:11px; color:#2ED573; font-weight:600; margin-top:6px'>+{r["points"]} pts</div>
                    </div>""", unsafe_allow_html=True)
    with tab3:
        st.markdown("<div class='section-label'>Top strivers</div>", unsafe_allow_html=True)
        leaderboard = get_leaderboard(db, limit=10)
        rank_icons = [
            "<i class='fas fa-medal' style='color:#FFD700;font-size:22px'></i>",
            "<i class='fas fa-medal' style='color:#C0C0C0;font-size:22px'></i>",
            "<i class='fas fa-medal' style='color:#CD7F32;font-size:22px'></i>",
        ] + [f"<span style='font-size:18px;font-weight:700;color:#ADB5BD'>{i+1}</span>" for i in range(3, 10)]
        if not leaderboard:
            st.info("No leaderboard data yet. Start checking in!")
        else:
            for i, (pts_obj, user) in enumerate(leaderboard):
                is_me = user.id == st.session_state.user_id
                _, _, lv_name, lv_color = get_level(pts_obj.total_points)
                you = " (you)" if is_me else ""
                st.markdown(f"""
                <div style='background:{"#E1F5EE22" if is_me else "white"};
                border:{"1px solid #9FE1CB" if is_me else "1px solid #E9ECEF"};
                border-radius:12px; padding:12px 16px; margin-bottom:8px;
                display:flex; align-items:center; justify-content:space-between'>
                    <div style='display:flex; align-items:center; gap:12px'>
                        <span style='width:28px;text-align:center'>{rank_icons[i]}</span>
                        <div class='avatar'>{initials(user.username)}</div>
                        <div>
                            <div style='font-size:13px; font-weight:600; color:#2D3436'>@{user.username}{you}</div>
                            <div style='font-size:11px; color:#636E72'>{lv_color} {lv_name}</div>
                        </div>
                    </div>
                    <div style='text-align:right'>
                        <div style='font-size:15px; font-weight:700; color:#FF4757'>{pts_obj.total_points:,} pts</div>
                        <div style='font-size:11px; color:#ADB5BD'>Level {pts_obj.level}</div>
                    </div>
                </div>""", unsafe_allow_html=True)
    db.close()

def render_profile():
    st.markdown(f"""
    <div style='margin-bottom:20px;position:relative;overflow:hidden;border-radius:16px;padding:20px;background:linear-gradient(135deg,rgba(248,249,250,0.7),rgba(255,255,255,0.75)),url("{IMG_GYM}");background-size:cover;background-position:center'>
        <div style='position:relative;z-index:1'><span style='font-size:13px;color:#636E72'>Account</span><br><span style='font-size:22px;font-weight:700;color:#2D3436'>My Profile</span></div>
    </div>""", unsafe_allow_html=True)
    db = SessionLocal()
    user = db.query(User).filter(User.id == st.session_state.user_id).first()
    memberships = db.query(StreakMember).filter(StreakMember.user_id == st.session_state.user_id).all()
    checkins = db.query(CheckIn).filter(CheckIn.user_id == st.session_state.user_id).all()
    best = max([m.longest_streak for m in memberships], default=0)
    ini = initials(user.username) if user else "??"
    st.markdown(f"""
    <div class='profile-header'>
        <div class='profile-avatar'>{ini}</div>
        <div style='font-size:20px; font-weight:700; color:#2D3436'>@{user.username}</div>
        <div style='font-size:13px; color:#636E72; margin-top:4px'>{user.email}</div>
        <div style='font-size:12px; color:#ADB5BD; margin-top:6px'>Member since {user.created_at.strftime('%B %Y')}</div>
        <div style='font-size:13px; color:#636E72; margin-top:8px'>{user.bio or "No bio yet — add one below!"}</div>
    </div>""", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    for col, num, label in [(col1, len(checkins), "Check-ins"), (col2, best, "Best Streak"), (col3, len(memberships), "Groups")]:
        with col:
            st.markdown(f"""
            <div class='stat-card'>
                <span class='stat-number'>{num}</span>
                <span class='stat-label'>{label}</span>
            </div>""", unsafe_allow_html=True)
    st.markdown("<div class='section-label' style='margin-top:8px'>Achievements</div>", unsafe_allow_html=True)
    motivated_count = sum(1 for c in checkins if c.sentiment == "motivated")
    badges = []
    if len(checkins) >= 1:    badges.append(("<i class='fas fa-seedling'></i>", "First Step",     "First check-in done"))
    if len(checkins) >= 7:    badges.append(("<i class='fas fa-bolt'></i>",    "Week Warrior",    "7 check-ins total"))
    if best >= 7:             badges.append(("<i class='fas fa-fire'></i>",    "On Fire",         "7 day streak"))
    if best >= 30:            badges.append(("<i class='fas fa-gem'></i>",     "Diamond Habit",   "30 day streak"))
    if len(memberships) >= 3: badges.append(("<i class='fas fa-users'></i>",   "Social Striver",  "Joined 3 groups"))
    if motivated_count >= 10: badges.append(("<i class='fas fa-smile'></i>",   "Positivity King", "10 motivated check-ins"))
    if len(checkins) >= 30:   badges.append(("<i class='fas fa-trophy'></i>",  "Consistency Pro", "30 total check-ins"))
    if badges:
        cols = st.columns(min(len(badges), 4))
        for i, (emoji, title, desc) in enumerate(badges):
            with cols[i % 4]:
                st.markdown(f"""
                <div class='stat-card'>
                    <div style='font-size:26px'>{emoji}</div>
                    <div style='font-size:13px; font-weight:600; color:#2D3436; margin-top:6px'>{title}</div>
                    <div style='font-size:11px; color:#636E72; margin-top:2px'>{desc}</div>
                </div>""", unsafe_allow_html=True)
    else:
        st.info("Complete your first check-in to earn achievements!")
    st.markdown("<div class='section-label' style='margin-top:16px'>Edit profile</div>", unsafe_allow_html=True)
    new_bio = st.text_area("Bio", value=user.bio or "", placeholder="Tell your streak groups about yourself...")
    if st.button("Save Changes", use_container_width=True):
        user.bio = new_bio
        db.commit()
        st.success("Profile updated!")
    db.close()

def main():
    if st.session_state.user_id is None:
        render_login()
        return

    st.markdown(f"""
    <div class='app-nav'>
        <div class='nav-logo'><i class='fas fa-fire'></i> Strive</div>
        <div class='nav-user'><i class='fas fa-user-circle'></i> @{st.session_state.username}</div>
    </div>""", unsafe_allow_html=True)

    nav_cols = st.columns([6, 1])
    with nav_cols[0]:
        page = st.radio(
            "Navigate",
            ["Feed", "Check In", "Goals", "Stats", "AI Coach", "Rewards", "Profile"],
            horizontal=True,
            label_visibility="collapsed",
            key="page_nav"
        )
    with nav_cols[1]:
        if st.button("Sign Out", key="logout_btn"):
            st.session_state.user_id = None
            st.session_state.username = None
            st.session_state.chat_history = []
            st.session_state.stay_logged_in = False
            st.query_params.clear()
            st.rerun()

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    st.markdown("""<div style='position:fixed;top:0;left:0;width:100%;height:100%;z-index:-2;background:linear-gradient(135deg,#FFF5F7 0%,#F0F4FF 50%,#F5FFF7 100%);pointer-events:none'></div><div style='position:fixed;bottom:-20%;right:-10%;width:600px;height:600px;background:radial-gradient(circle,rgba(255,71,87,0.06),transparent 70%);border-radius:50%;pointer-events:none;z-index:-1;animation:float 8s ease-in-out infinite'></div><div style='position:fixed;top:-10%;left:-5%;width:400px;height:400px;background:radial-gradient(circle,rgba(124,92,252,0.04),transparent 70%);border-radius:50%;pointer-events:none;z-index:-1;animation:float 10s ease-in-out infinite 1s'></div>""", unsafe_allow_html=True)

    pages = {
        "Feed": render_feed,
        "Check In": render_checkin,
        "Goals": render_goals,
        "Stats": render_stats,
        "AI Coach": render_ai_assistant,
        "Rewards": render_rewards,
        "Profile": render_profile
    }
    pages[page]()

if __name__ == "__main__":
    main()
