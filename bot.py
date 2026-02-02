import streamlit as st
import pandas as pd
import json
import datetime

# ================== APP CONFIG ==================
st.set_page_config(page_title="Prep Boost", layout="wide")
DATA_FILE = "prep_boost_data.json"

# ================== SESSION STATE (CRITICAL FIX) ==================
if "jee_main_1" not in st.session_state:
    st.session_state.jee_main_1 = datetime.date(2026, 1, 15)

if "jee_main_2" not in st.session_state:
    st.session_state.jee_main_2 = datetime.date(2026, 4, 5)

if "jee_adv" not in st.session_state:
    st.session_state.jee_adv = datetime.date(2026, 5, 25)

# ================== DATA HANDLING ==================
def load_data():
    try:
        with open(DATA_FILE) as f:
            return json.load(f)
    except:
        return []

def save_data(d):
    with open(DATA_FILE, "w") as f:
        json.dump(d, f, indent=4)

data = load_data()

# ================== UTILS ==================
def normalize(v, m):
    return min(100, (v / m) * 100)

def consistency(d):
    return min(100, len(set(x["date"] for x in d)) * 2)

def streak(d):
    return len(set(x["date"] for x in d))

def xp_level(hours):
    xp = int(hours * 10)
    level = xp // 500 + 1
    return xp, level

# ================== SIDEBAR ==================
st.sidebar.title("🚀 PREP BOOST")
page = st.sidebar.radio(
    "Navigate",
    [
        "Dashboard",
        "Study Tracker",
        "JEE Main Predictor",
        "JEE Advanced Predictor",
        "AIR <100 Analyzer",
        "⏳ Time & Study Planner"
    ]
)

# ================== DASHBOARD ==================
if page == "Dashboard":
    st.title("📊 Prep Boost Dashboard")

    if not data:
        st.info("Start logging study to unlock analytics")
    else:
        df = pd.DataFrame(data)
        total_hours = df["hours"].sum()
        cons = consistency(data)
        st_days = streak(data)
        xp, lvl = xp_level(total_hours)

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Study Hours", round(total_hours, 1))
        c2.metric("Consistency %", cons)
        c3.metric("Streak (days)", st_days)
        c4.metric("Level", lvl)

        st.progress((xp % 500) / 500)

        st.subheader("📈 Daily Study Trend")
        st.line_chart(df.groupby("date")["hours"].sum())

        st.subheader("📚 Subject-wise Effort")
        st.bar_chart(df.groupby("subject")["hours"].sum())

# ================== STUDY TRACKER ==================
elif page == "Study Tracker":
    st.title("📝 Daily Study Tracker")

    subject = st.selectbox("Subject", ["Physics", "Chemistry", "Maths"])
    hours = st.slider("Hours Studied Today", 0.5, 16.0, 1.0)

    if st.button("Save Study Log"):
        data.append({
            "date": str(datetime.date.today()),
            "subject": subject,
            "hours": hours
        })
        save_data(data)
        st.success("Study data saved ✔")

# ================== JEE MAIN ==================
elif page == "JEE Main Predictor":
    st.title("🎯 JEE Main Rank Predictor")

    p = st.slider("Physics Marks", 0, 100)
    c = st.slider("Chemistry Marks", 0, 100)
    m = st.slider("Maths Marks", 0, 100)
    acc = st.slider("Accuracy %", 0, 100)
    mocks = st.slider("Mocks Attempted", 0, 30)

    cons = consistency(data)

    if st.button("Predict JEE Main Rank"):
        score = (
            normalize(p + c + m, 300) * 0.45 +
            acc * 0.20 +
            normalize(m, 100) * 0.15 +
            cons * 0.10 +
            min(mocks * 5, 100) * 0.10
        )

        def rank(s):
            if s >= 90: return "< 1000"
            if s >= 85: return "1k – 3k"
            if s >= 80: return "3k – 6k"
            if s >= 70: return "6k – 15k"
            return "> 15k"

        st.success(f"Expected Rank: {rank(score)}")
        st.info(f"Best Case: {rank(score+5)} | Worst Case: {rank(score-5)}")
        st.metric("Overall Score %", round(score, 1))

# ================== JEE ADV ==================
elif page == "JEE Advanced Predictor":
    st.title("🔥 JEE Advanced Rank Predictor")

    p1 = st.slider("Paper-1 Marks", 0, 180)
    p2 = st.slider("Paper-2 Marks", 0, 180)
    acc = st.slider("Accuracy %", 0, 100)
    mp = st.slider("Maths + Physics Strength", 0, 100)
    neg = st.slider("Negative Marking Control", 0, 100)

    cons = consistency(data)

    if st.button("Predict JEE Advanced Rank"):
        score = (
            normalize(p1 + p2, 360) * 0.40 +
            acc * 0.20 +
            mp * 0.20 +
            cons * 0.10 +
            neg * 0.10
        )

        if score >= 90: r = "AIR < 100"
        elif score >= 85: r = "AIR 100 – 300"
        elif score >= 80: r = "AIR 300 – 800"
        elif score >= 70: r = "AIR 800 – 2000"
        else: r = "AIR > 2000"

        st.success(r)
        st.metric("Overall Score %", round(score, 1))

# ================== AIR <100 ==================
elif page == "AIR <100 Analyzer":
    st.title("🏆 AIR <100 Probability Engine")

    adv_marks = st.slider("Current Advanced Marks", 0, 360)
    cons = consistency(data)
    total_hours = sum(x["hours"] for x in data)

    probability = (
        normalize(adv_marks, 360) * 0.6 +
        cons * 0.2 +
        min(total_hours / 500 * 100, 100) * 0.2
    )

    st.metric("AIR <100 Probability", f"{int(probability)}%")

    if probability > 80:
        st.success("🔥 Very strong chance")
    elif probability > 60:
        st.warning("⚠ Possible with strict discipline")
    else:
        st.error("🚨 Needs serious improvement")

# ================== TIME & PLANNER ==================
elif page == "⏳ Time & Study Planner":
    st.title("⏳ Time-Left Based Smart Planner")

    today = datetime.date.today()

    st.subheader("📅 Exam Dates (Stable)")

    st.session_state.jee_main_1 = st.date_input(
        "JEE Main – 1st Attempt", st.session_state.jee_main_1
    )
    st.session_state.jee_main_2 = st.date_input(
        "JEE Main – 2nd Attempt", st.session_state.jee_main_2
    )
    st.session_state.jee_adv = st.date_input(
        "JEE Advanced", st.session_state.jee_adv
    )

    d1 = (st.session_state.jee_main_1 - today).days
    d2 = (st.session_state.jee_main_2 - today).days
    d3 = (st.session_state.jee_adv - today).days

    c1, c2, c3 = st.columns(3)
    c1.metric("Days Left – Main 1", max(d1, 0))
    c2.metric("Days Left – Main 2", max(d2, 0))
    c3.metric("Days Left – Advanced", max(d3, 0))

    st.subheader("📚 Auto Study Plan (for Main-1)")

    syllabus_left = st.slider("Syllabus Remaining (%)", 0, 100, 50)
    max_daily = st.slider("Max Daily Capacity (hrs)", 4, 16, 10)

    total_required = syllabus_left * 8
    daily_required = int(total_required / max(d1, 1))

    st.metric("Required Daily Hours", daily_required)

    if daily_required > max_daily:
        st.error("🚨 Pace insufficient – increase hours")
    else:
        st.success("🔥 Target achievable")

    phy = int(daily_required * 0.35)
    chem = int(daily_required * 0.30)
    math = daily_required - phy - chem

    st.write(f"⚛ Physics: **{phy} hrs/day**")
    st.write(f"🧪 Chemistry: **{chem} hrs/day**")
    st.write(f"📐 Maths: **{math} hrs/day**")

    st.subheader("🔥 Advanced Intensity Mode")
    if d3 > 180:
        st.success("Concept Building Phase")
    elif d3 > 120:
        st.warning("Concept + PYQ Phase")
    else:
        st.error("HARDCORE MODE – ONLY PYQs & MOCKS")
