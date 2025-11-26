import streamlit as st
import datetime
import pandas as pd
import calendar
import random

st.set_page_config(page_title="🌸 Mood Journal", layout="centered")

# ---------- 初始化 ----------
if "page" not in st.session_state:
    st.session_state.page = "date"
if "selected_date" not in st.session_state:
    st.session_state.selected_date = datetime.date.today()
if "selected_mood" not in st.session_state:
    st.session_state.selected_mood = None
if "diary" not in st.session_state:
    st.session_state.diary = {}  # {"2025-11-11": {"mood": "😀", "text": "..."}}

# ---------- 樣式 ----------
st.markdown("""
    <style>
        body {
            background-color: #f7f3ef;
            font-family: 'Segoe UI', sans-serif;
        }
        .title {
            text-align: center;
            font-size: 36px;
            font-weight: bold;
            color: #4b3f37;
            margin-bottom: 10px;
        }
        .subtitle {
            text-align: center;
            font-size: 18px;
            color: #6d5f56;
            margin-bottom: 25px;
        }
        .emoji-btn {
            font-size: 40px;
            cursor: pointer;
            margin: 0 10px;
            transition: transform 0.2s;
        }
        .emoji-btn:hover {
            transform: scale(1.2);
        }
        .save-btn {
            background-color: #c9b9a8;
            color: white;
            border: none;
            border-radius: 10px;
            padding: 8px 16px;
            font-weight: bold;
            cursor: pointer;
            margin-top: 10px;
        }
        .save-btn:hover {
            background-color: #b8a694;
        }
        .calendar-day {
            display: inline-block;
            width: 40px;
            height: 40px;
            text-align: center;
            margin: 2px;
            border-radius: 8px;
            background-color: #fffaf3;
            box-shadow: 0 0 4px #d9d0c9;
            font-size: 20px;
            line-height: 40px;
        }
        .calendar-grid {
            text-align: center;
            margin-top: 15px;
        }
    </style>
""", unsafe_allow_html=True)

# ---------- 暖心回覆 ----------
emotion_responses = {
    "tired": "You sound tired 😴. Rest is productive too — take time to recharge.",
    "bored": "Boredom might mean your heart craves something new 🎨. Try doing something creative today!",
    "calm": "That’s wonderful 🌿. Calmness is peace speaking softly to your soul.",
    "relaxed": "So good to hear that you’re relaxed ☕. Let this moment remind you — peace is power.",
    "guilty": "Guilt shows you care 🌱. Reflect gently and forgive yourself.",
    "ashamed": "You might feel ashamed 😔, but remember — you are learning, not failing.",
    "proud": "That’s amazing! 🎉 You’ve worked hard — let yourself enjoy this feeling!",
    "jealous": "Jealousy means you value something deeply 💚. Use that awareness to inspire growth.",
    "scared": "Fear can be loud 😨, but it can’t last forever. You’re safe.",
    "afraid": "Even fear is part of courage 🌤. You’re doing great.",
    "anxious": "Anxiety can be heavy 😥. Breathe slowly — you’re safe and doing your best.",
    "happy": "Yay! So happy for you! 😄🎈 Let your joy shine and share your smile today!",
    "sad": f"It’s okay to feel sad 💧. Emotions flow and fade — here’s a little cheer-up joke for you:\n\n**{random.choice(['Why did the scarecrow win an award? Because he was outstanding in his field 🌾', 'I told my computer I felt sad — it gave me a byte of comfort 💻', 'Did you hear about the depressed coffee? It got mugged ☕'])}** 😄",
    "upset": "It’s alright to feel upset 😔. Let it out — expression is healing.",
    "lonely": "Loneliness is heavy 🫶. You’re not alone — I’m here listening.",
    "disappointed": "Disappointment means you cared ❤️. That’s a good thing — it shows your heart’s alive.",
}

# ---------- 第1頁：選日期 ----------
if st.session_state.page == "date":
    st.markdown("<div class='title'>🌸 My Mood Journal</div>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle'>Select a date to begin</div>", unsafe_allow_html=True)

    selected_date = st.date_input("📅 Choose a date:", value=st.session_state.selected_date)
    st.session_state.selected_date = selected_date

    col1, col2 = st.columns(2)
    if col1.button("Next ➜ Choose Mood"):
        st.session_state.page = "mood"
        st.rerun()

    if col2.button("📆 View Monthly Calendar"):
        st.session_state.page = "calendar"
        st.rerun()

# ---------- 第2頁：選表情 ----------
elif st.session_state.page == "mood":
    st.markdown("<div class='title'>How do you feel?</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='subtitle'>{st.session_state.selected_date.strftime('%Y-%m-%d')}</div>", unsafe_allow_html=True)

    mood_emojis = {
        "happy": "😀",
        "sad": "😢",
        "angry": "😡",
        "calm": "😌",
        "surprise": "😲"
    }

    cols = st.columns(5)
    for i, (mood, emoji) in enumerate(mood_emojis.items()):
        if cols[i].button(emoji, key=mood):
            st.session_state.selected_mood = emoji
            st.session_state.page = "journal"
            st.rerun()

    if st.button("⬅ Back to Date"):
        st.session_state.page = "date"
        st.rerun()

# ---------- 第3頁：寫日記 ----------
elif st.session_state.page == "journal":
    date_key = st.session_state.selected_date.strftime("%Y-%m-%d")
    mood_icon = st.session_state.selected_mood

    st.markdown(f"<div class='title'>📝 {date_key}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='subtitle'>Your mood: {mood_icon}</div>", unsafe_allow_html=True)

    diary_text = st.text_area("Write about your day:", value=st.session_state.diary.get(date_key, {}).get("text", ""), height=200)

    if st.button("💾 Save"):
        # 檢查關鍵字生成回覆
        response = "Thank you for sharing your feelings 🌷"
        for keyword, reply in emotion_responses.items():
            if keyword in diary_text.lower():
                response = reply
                break

        st.session_state.diary[date_key] = {"mood": mood_icon, "text": diary_text, "response": response}
        st.success("Saved successfully!")
        st.markdown(f"### 🌈 Response:\n{response}")

    if st.button("⬅ Back to Mood"):
        st.session_state.page = "mood"
        st.rerun()

# ---------- 第4頁：月曆總覽 ----------
elif st.session_state.page == "calendar":
    today = datetime.date.today()
    year, month = today.year, today.month

    st.markdown("<div class='title'>📅 Monthly Mood Overview</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='subtitle'>{year}年 {month}月</div>", unsafe_allow_html=True)

    cal = calendar.monthcalendar(year, month)
    st.markdown("<div class='calendar-grid'>", unsafe_allow_html=True)

    weekdays = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    st.markdown(" ".join([f"<b>{d}</b>" for d in weekdays]), unsafe_allow_html=True)

    for week in cal:
        week_row = ""
        for day in week:
            if day == 0:
                week_row += "<span class='calendar-day'></span>"
            else:
                date_str = f"{year}-{month:02d}-{day:02d}"
                mood = st.session_state.diary.get(date_str, {}).get("mood", "")
                week_row += f"<span class='calendar-day'>{mood or '•'}</span>"
        st.markdown(week_row, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    if st.button("⬅ Back to Date Selection"):
        st.session_state.page = "date"
        st.rerun()
