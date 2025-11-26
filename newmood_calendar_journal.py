import streamlit as st
import datetime
import calendar
import random
import json
import os
import pandas as pd
import time 
import plotly.express as px 

# -------------------- 1. GLOBAL CONSTANTS AND MAPPINGS --------------------

POINTS_PER_ENTRY = 10 

st.set_page_config(page_title="🌸 Personalized Mood Journal Pro", layout="centered")

# --- Global Lists (English) ---
ACTIVITY_TAGS = [
    "Work 💻", "Exercise 🏋️", "Socializing 👥", "Food 🍕", 
    "Family ❤️", "Hobbies 🎨", "Rest 🛋️", "Study 📚", "Travel ✈️", "Nature 🏞️", "Money 💰"
]

MOOD_MAPPING = {
    "Happy": "😀", "Sad": "😢", "Angry": "😡", "Calm": "😌", 
    "Excited": "🤩", "Tired": "😴", "Anxious": "😥",
}
MOOD_SCORES = {
    "😀": 5, "🤩": 4, "😌": 3, "😴": 2, "😢": 1, "😡": 1, "😥": 1
}

EMOTION_RESPONSES = {
    "tired": "You sound tired 😴. Rest is productive too — take time to recharge.",
    "bored": "Boredom might mean your heart craves something new 🎨. Try doing something creative today!",
    "calm": "That’s wonderful 🌿. Calmness is peace speaking softly to your soul.",
    "guilty": "Guilt shows you care 🌱. Reflect gently and forgive yourself.",
    "anxious": "Anxiety can be heavy 😥. Breathe slowly — you’re safe and doing your best.",
    "happy": "Yay! So happy for you! 😄🎈 Let your joy shine and share your smile today!",
    "sad": f"It’s okay to feel sad 💧. Emotions flow and fade — here’s a little cheer-up joke for you:\n\n**{random.choice(['Why did the scarecrow win an award? Because he was outstanding in his field 🌾', 'I told my computer I felt sad — it gave me a byte of comfort 💻', 'Did you hear about the depressed coffee? It got mugged ☕'])}**",
    "lonely": "Loneliness is heavy 🫶. You’re not alone — I’m here listening.",
    "angry": "It’s alright to feel upset 😔. Let it out — expression is healing.",
}

GENERAL_RESPONSES = [
    "Thank you for sharing your entry ✍️. Remember, small steps lead to big changes.",
    "Your feelings are valid. Take a moment to focus on your breath and find peace. 🌬️",
    "It takes courage to write down your thoughts. We're here to listen to your journey! 🫂",
    "Keep up the habit of reflection! Every day is a new story waiting to unfold. 🌿",
    "Well done on making an entry today! You are prioritizing your well-being. 😊",
]

DAILY_PROMPTS = [
    "What is one thing that made you feel proud or accomplished today?",
    "If you could give yesterday's self one piece of advice, what would it be?",
    "Describe three sounds, smells, or sights you encountered today.",
    "Did you express gratitude to anyone today, or did someone make you feel grateful?",
    "What is one small thing you can do tomorrow to make it better?",
    "What is a new thing you learned today, no matter how small?",
]

SURPRISE_FACTS = [
    "Did you know a group of flamingos is called a 'flamboyance'? Stay flamboyant! 💖",
    "Fun Fact: Honey never spoils. Keep your good memories preserved like honey! 🍯",
    "Quick Riddle: What has to be broken before you can use it? An egg! Break those barriers!🥚",
    "A moment of wonder: There are more trees on Earth than stars in the Milky Way. Keep growing! 🌳",
    "Your lucky number today is 7! May your day be seven times brighter! ✨",
]

# --- V15: Fortune Slips (50 total) ---
FORTUNE_SLIPS = (
    # Supreme Luck (大吉 - 5 slips)
    [("Supreme Luck", "🌟", "A day of profound clarity and happiness awaits. Trust your highest vision; your energy is magnetic today.")] * 2 +
    [("Supreme Luck", "🌟", "All relationships are blessed today. Reach out and share your good fortune; it will return tenfold.")] +
    [("Supreme Luck", "🌟", "An obstacle you faced yesterday dissolves today. Unexpected success finds you when you stay open.")] +
    [("Supreme Luck", "🌟", "Inner peace is your greatest asset. Use this calm to make powerful, confident decisions.")] +
    
    # Excellent Luck (吉 - 15 slips)
    [("Excellent Luck", "✨", "Your mind is sharp and ideas flow. Write down new goals; you have the power to achieve them.")] * 3 +
    [("Excellent Luck", "✨", "Take a risk today, especially in creative endeavors. Joy follows bold action.")] * 3 +
    [("Excellent Luck", "✨", "Unexpected kindness comes from a stranger or colleague. Pay it forward and brighten someone else's day.")] * 3 +
    [("Excellent Luck", "✨", "A lingering doubt is resolved easily. Feel lighter and move forward with purpose.")] * 3 +
    [("Excellent Luck", "✨", "The path to self-improvement is wide open. Commit to a healthy habit today.")] * 3 +

    # Good Prospect (中吉 - 15 slips)
    [("Good Prospect", "🍀", "A feeling of balance settles in. Trust the rhythm of your day and avoid unnecessary rushing.")] * 3 +
    [("Good Prospect", "🍀", "Someone needs your support. Offering a listening ear will deepen your connection.")] * 3 +
    [("Good Prospect", "🍀", "Your emotional well-being requires gentle attention. Focus on rest and simple pleasures.")] * 3 +
    [("Good Prospect", "🍀", "A small personal victory is on the horizon. Acknowledge and reward your efforts.")] * 3 +
    [("Good Prospect", "🍀", "Change is coming, but it is manageable. Prepare your mind for gentle adjustments.")] * 3 +

    # Moderate Fortune (小吉 - 10 slips)
    [("Moderate Fortune", "🌤️", "It is a day for careful planning. Avoid spontaneity and stick to your schedule for best results.")] * 2 +
    [("Moderate Fortune", "🌤️", "Energy levels are moderate. Conserve your efforts for what truly matters by saying 'no' when needed.")] * 2 +
    [("Moderate Fortune", "🌤️", "A minor misunderstanding may occur. Approach conversations with patience and seek clarity.")] * 2 +
    [("Moderate Fortune", "🌤️", "Don't dwell on perfection. Good enough is perfect for today; accept progress over flawless execution.")] * 2 +
    [("Moderate Fortune", "🌤️", "Neutral energy surrounds you. Use this quiet day for thoughtful reflection in your journal.")] * 2 +

    # Minor Challenge (凶 - 5 slips)
    [("Minor Challenge", "⚠️", "Frustration is possible. Use this as a signal to step away and seek immediate stress relief.")] +
    [("Minor Challenge", "⚠️", "A feeling of heaviness may arise. Be extra gentle with yourself and prioritize basic self-care.")] +
    [("Minor Challenge", "⚠️", "Be mindful of unnecessary spending or overcommitment. Your boundaries need protection today.")] +
    [("Minor Challenge", "⚠️", "Doubt may creep in. Remember your core strengths and seek external encouragement if needed.")] +
    [("Minor Challenge", "⚠️", "Communication requires extra effort. Write down your thoughts before speaking to avoid conflict.")]
)

# --- NEW: Gamification Constants ---
DARK_MODE_COST = 500
ACHIEVEMENTS = [
    {"name": "Journaling Beginner", "desc": "Achieve 5 total entries.", "threshold": 5, "type": "total_entries"},
    {"name": "Consistent Companion", "desc": "Achieve a 7-day streak.", "threshold": 7, "type": "streak"},
    {"name": "Emotion Explorer", "desc": "Log all 7 mood types at least once.", "threshold": 7, "type": "unique_moods"},
    {"name": "Insight Master", "desc": "Log 30 total entries.", "threshold": 30, "type": "total_entries"},
]

# --- NEW: Pet Mode Constants ---
PET_INITIAL_HEALTH = 100
PET_INITIAL_HAPPINESS = 50
PET_DAILY_COST = 5 
PET_REWARD_HAPPINESS = 10 
PET_INTERACTION_COST = 0 
PET_IMAGE_WIDTH = 250

# --- NEW: Mood-Pet Mapping (情緒與寵物對應表 - 使用本地圖片檔案名) ---
# NOTE: You MUST have a subfolder named 'pet_images' with corresponding PNG files
MOOD_PET_MAPPING = {
    "😀": {"name": "Joyful Puppy", "emoji": "🐕", "img_path": "pet_images/happy.png", "desc": "Your puppy is wagging its tail happily!"},
    "🤩": {"name": "Excited Koala", "emoji": "🐨", "img_path": "pet_images/excited.png", "desc": "Your koala is ready for an adventure!"},
    "😌": {"name": "Peaceful Cat", "emoji": "🐈", "img_path": "pet_images/calm.png", "desc": "Your cat is resting in a sunbeam."},
    "😴": {"name": "Tired Sloth", "emoji": "🦥", "img_path": "pet_images/tired.png", "desc": "Your tired sloth could use a nap."},
    "😢": {"name": "Sad Hamster", "emoji": "🐹", "img_path": "pet_images/sad.png", "desc": "Your little hamster needs a kind ear."},
    "😡": {"name": "Angry Lion", "emoji": "🦁", "img_path": "pet_images/angry.png", "desc": "Your lion is about to roar!"},
    "😥": {"name": "Anxious Turtle", "emoji": "🐢", "img_path": "pet_images/anxious.png", "desc": "Your anxious turtle is hiding in its shell."},
}
# --------------------------------------------------------------------------------


# --- Helper Functions (Data & Streak) ---

def get_user_data_file(user_name):
    """Generates a unique file name based on user name."""
    if not user_name:
        return None
    safe_name = user_name.strip().lower().replace(" ", "_")
    return f"diary_{safe_name}.json"

def load_diary(user_name):
    """Loads diary data for the specified user."""
    data_file = get_user_data_file(user_name)
    if not data_file: return
    
    if os.path.exists(data_file):
        try:
            with open(data_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                st.session_state.diary = data.get("diary", {})
                st.session_state.total_points = data.get("total_points", 0)
                st.session_state.dark_mode = data.get("dark_mode", False)
                
                # Load pet state
                st.session_state.pet_name = data.get("pet_name", "MoodBuddy")
                st.session_state.pet_health = data.get("pet_health", PET_INITIAL_HEALTH)
                st.session_state.pet_happiness = data.get("pet_happiness", PET_INITIAL_HAPPINESS)
                st.session_state.last_pet_interaction = data.get("last_pet_interaction", datetime.date.today().strftime("%Y-%m-%d"))
                
                loaded_date = data.get("fortune_date")
                today_str = datetime.date.today().strftime("%Y-%m-%d")
                
                if loaded_date == today_str:
                    st.session_state.fortune_drawn = True
                    st.session_state.fortune_result = data.get("fortune_result", None)
                else:
                    st.session_state.fortune_drawn = False
                    st.session_state.fortune_result = None
        except json.JSONDecodeError:
            st.session_state.diary = {}
    else:
        st.session_state.diary = {}

def save_diary():
    """Saves diary and state data for the current user."""
    user_name = st.session_state.get("user_name")
    data_file = get_user_data_file(user_name)
    if not data_file: return

    data_to_save = {
        "diary": st.session_state.diary,
        "total_points": st.session_state.total_points,
        "user_name": user_name,
        "fortune_drawn": st.session_state.get("fortune_drawn", False),
        "fortune_result": st.session_state.get("fortune_result", None),
        "fortune_date": datetime.date.today().strftime("%Y-%m-%d"),
        "dark_mode": st.session_state.get("dark_mode", False),
        
        # Save pet state
        "pet_name": st.session_state.get("pet_name", "MoodBuddy"),
        "pet_health": st.session_state.get("pet_health", PET_INITIAL_HEALTH),
        "pet_happiness": st.session_state.get("pet_happiness", PET_INITIAL_HAPPINESS),
        "last_pet_interaction": st.session_state.get("last_pet_interaction", datetime.date.today().strftime("%Y-%m-%d"))
    }
    with open(data_file, "w", encoding="utf-8") as f:
        json.dump(data_to_save, f, ensure_ascii=False, indent=4)

def calculate_streak(diary):
    """Calculates the current consecutive logging streak."""
    if not diary: return 0
    logged_dates = set(
        datetime.datetime.strptime(d, "%Y-%m-%d").date() 
        for d in diary.keys()
    )
    today = datetime.date.today()
    streak = 0
    day_to_check = today
    if day_to_check in logged_dates:
        streak = 1
        day_to_check -= datetime.timedelta(days=1)
    elif (day_to_check - datetime.timedelta(days=1)) in logged_dates:
        streak = 1
        day_to_check -= datetime.timedelta(days=2) 
    else:
        return 0
    while day_to_check in logged_dates:
        streak += 1
        day_to_check -= datetime.timedelta(days=1)
    return streak

def get_diary_response(text):
    """Generates response based on keywords or random general."""
    text_lower = text.lower()
    for keyword, reply in EMOTION_RESPONSES.items():
        if keyword in text_lower:
            return reply
    return random.choice(GENERAL_RESPONSES)

def analyze_recent_mood_for_advice(diary):
    
    if not diary:
        return "👋 Time to start your first entry and unlock personalized advice!"
    today = datetime.date.today()
    one_week_ago = today - datetime.timedelta(days=7)
    recent_scores = []
    for date_str, entry in diary.items():
        entry_date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
        if one_week_ago <= entry_date < today:
            recent_scores.append(entry.get('score', 3))
    if not recent_scores:
        return "🤔 Need a week of data for personalized advice. Keep logging!"
    df = pd.Series(recent_scores)
    avg_score = df.mean()
    if avg_score <= 2.5:
        low_moods = [entry['mood'] for date_str, entry in diary.items() 
                     if one_week_ago <= datetime.datetime.strptime(date_str, "%Y-%m-%d").date() < today and entry.get('score', 3) <= 2]
        if low_moods:
            most_common_low_mood = pd.Series(low_moods).mode()[0]
            if most_common_low_mood in ["😢", "😥"]:
                return f"😥 Recent Mood Alert: You've often felt sad/anxious. **Challenge:** Try a 10-minute mindfulness exercise today."
            elif most_common_low_mood in ["😴"]:
                return f"😴 Recent Mood Alert: You've often felt tired. **Challenge:** Aim for 30 minutes of light physical activity today."
            elif most_common_low_mood in ["😡"]:
                return f"😡 Recent Mood Alert: You've often felt angry. **Challenge:** Write down 3 things you are grateful for before bed."
            else:
                return f"📉 Recent Mood Alert: Your average mood score is low. **Challenge:** Reach out to a friend or loved one today."
    elif avg_score >= 4.0:
        return "✨ Great Job! Your recent mood trend is excellent! **Advice:** Share your joy—compliment someone today!"
    else:
        return "⚖️ Your mood is balanced. **Advice:** Keep exploring your activities! Try adding one new tag today."

# --- Achievement Calculation ---
def calculate_achievements(diary, streak):
    """Checks the user's diary against predefined achievement thresholds."""
    total_entries = len(diary)
    logged_moods = set(entry['mood'] for entry in diary.values())
    unique_moods_count = len(logged_moods)
    
    unlocked_achievements = []
    
    for achievement in ACHIEVEMENTS:
        is_unlocked = False
        if achievement['type'] == 'total_entries' and total_entries >= achievement['threshold']:
            is_unlocked = True
        elif achievement['type'] == 'streak' and streak >= achievement['threshold']:
            is_unlocked = True
        elif achievement['type'] == 'unique_moods' and unique_moods_count >= achievement['threshold']:
            if achievement['threshold'] == len(MOOD_MAPPING):
                 is_unlocked = unique_moods_count >= achievement['threshold']
            else:
                 is_unlocked = unique_moods_count >= achievement['threshold']
            
        if is_unlocked:
            unlocked_achievements.append(achievement['name'])
            
    return unlocked_achievements

# --- NEW: Pet Status Update ---
def update_pet_status():
    """Calculates pet status based on logging streak and mood, and applies daily decay."""
    today = datetime.date.today()
    
    try:
        last_interaction_date = datetime.datetime.strptime(st.session_state.last_pet_interaction, "%Y-%m-%d").date()
    except ValueError:
        last_interaction_date = today 
    
    days_since_interaction = (today - last_interaction_date).days
    
    if days_since_interaction > 0:
        decay_amount = days_since_interaction * PET_DAILY_COST
        
        st.session_state.pet_health = max(0, st.session_state.pet_health - decay_amount)
        st.session_state.pet_happiness = max(0, st.session_state.pet_happiness - decay_amount)
        
        for i in range(1, days_since_interaction + 1):
            past_date = last_interaction_date + datetime.timedelta(days=i)
            past_date_str = past_date.strftime("%Y-%m-%d")
            
            if past_date_str in st.session_state.diary:
                st.session_state.pet_health = min(100, st.session_state.pet_health + PET_REWARD_HAPPINESS)
                entry_score = st.session_state.diary[past_date_str].get('score', 3)
                st.session_state.pet_happiness = min(100, st.session_state.pet_happiness + entry_score)
        
        st.session_state.last_pet_interaction = today.strftime("%Y-%m-%d")
        save_diary()


# --- Initialization ---
def initialize_session_state():
    if "user_name" not in st.session_state:
        st.session_state.page = "onboarding"
    elif "page" not in st.session_state:
        st.session_state.page = "fortune_draw"
        
    if "selected_date" not in st.session_state:
        st.session_state.selected_date = datetime.date.today()
    if "selected_mood_emoji" not in st.session_state:
        st.session_state.selected_mood_emoji = None
    
    if "diary" not in st.session_state:
        st.session_state.diary = {}
    if "total_points" not in st.session_state:
        st.session_state.total_points = 0
        
    if "fortune_drawn" not in st.session_state:
        st.session_state.fortune_drawn = False
        st.session_state.fortune_result = None
    
    if "dark_mode" not in st.session_state:
        st.session_state.dark_mode = False

    # Pet state initialization
    if "pet_name" not in st.session_state:
        st.session_state.pet_name = "MoodBuddy" 
    if "pet_health" not in st.session_state:
        st.session_state.pet_health = PET_INITIAL_HEALTH
    if "pet_happiness" not in st.session_state:
        st.session_state.pet_happiness = PET_INITIAL_HAPPINESS
    if "last_pet_interaction" not in st.session_state:
        st.session_state.last_pet_interaction = datetime.date.today().strftime("%Y-%m-%d")
    
    # Pet interaction messages
    if "pet_interaction_message" not in st.session_state:
        st.session_state.pet_interaction_message = None
    
    # Track if user interacted today
    if "pet_interacted_today" not in st.session_state:
        st.session_state.pet_interacted_today = False
        
    today_str = datetime.date.today().strftime("%Y-%m-%d")
    if st.session_state.last_pet_interaction != today_str:
        st.session_state.pet_interacted_today = False


initialize_session_state() 

# -------------------- 2. STYLES --------------------

FIXED_THEME_COLOR = "#c9b9a8" 
FIXED_ACCENT_COLOR = "#4b3f37" 

# --- NEW: Dynamic Style Variables (Background Locked) ---
is_dark = st.session_state.get("dark_mode", False)

# Lock background color
BG_LOCK_COLOR = "#f0f2f6" 
# ----------------------------------------------------
TEXT_MAIN = "#000000" if is_dark else "#4b3f37" 
ACCENT_COLOR = "#a090ff" if is_dark else "#4b3f37"
SUBTITLE_COLOR = "#cccccc" if is_dark else "#6d5f56"
FORTUNE_BOX_BG = "#3a3a3a" if is_dark else "#fff8e1"
CARD_BG = "#2e2e2e" if is_dark else "#e6ffe6" # Inner card background

st.markdown(f"""
    <style>
        /* Lock Streamlit app background */
        .stApp {{
            background-color: {BG_LOCK_COLOR}; 
        }}
        /* Lock main content area background */
        .main > div {{
            background-color: {BG_LOCK_COLOR};
        }}
        
        .title {{
            text-align: center;
            font-size: 36px;
            font-weight: bold;
            color: {ACCENT_COLOR}; 
            margin-bottom: 10px;
        }}
        .subtitle {{
            text-align: center;
            font-size: 18px;
            color: {SUBTITLE_COLOR};
            margin-bottom: 25px;
        }}
        /* Dynamic colors for info/advice boxes */
        .advice-box, .insight-box {{
            padding: 10px;
            border-radius: 8px;
            background-color: {CARD_BG}; 
            border: 1px solid {'#555' if is_dark else '#ccc'};
            color: {TEXT_MAIN};
            margin-bottom: 15px;
        }}
        .fortune-result-box {{
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            text-align: center;
            background-color: {FORTUNE_BOX_BG}; 
            margin-top: 20px;
        }}
        .fortune-level {{
            font-size: 40px;
            font-weight: bold;
            color: {ACCENT_COLOR};
        }}
        .fortune-emoji {{
            font-size: 60px;
            margin: 10px 0;
        }}
        .fortune-description {{
            font-size: 18px;
            font-style: italic;
            color: {SUBTITLE_COLOR};
        }}
        /* Styles for the shaking container */
        .shaking-container {{
            text-align: center;
            margin: 40px auto;
            max-width: 300px;
        }}
        .shaking-icon {{
            font-size: 100px;
            display: inline-block;
        }}
        /* Streamlit widget adjustments for Dark Mode */
        .stMultiSelect, .stTextArea, .stTextInput {{
            color: {TEXT_MAIN};
            background-color: {'#1e1e1e' if is_dark else '#ffffff'};
        }}
        /* Achievement icon style */
        .achievement-icon-gold {{
            font-size: 2em;
            color: gold; 
            margin-right: 10px;
        }}
        .achievement-icon-grey {{
            font-size: 2em;
            color: #9e9e9e; /* Grey */
            margin-right: 10px;
        }}
        /* Pet image container style */
        .pet-image-container {{
            text-align: center;
            margin-bottom: 20px;
        }}
        /* Fix Streamlit image border */
        .stImage > img {{
            border-radius: 15px;
            border: 4px solid {ACCENT_COLOR};
            box-shadow: 0 4px 10px rgba(0,0,0,0.1);
            max-width: {PET_IMAGE_WIDTH}px;
            height: auto;
        }}
        /* Fix mood-picker style */
        .stRadio div[role="radiogroup"] > label {{
            margin-right: 10px;
        }}
        
    </style>
""", unsafe_allow_html=True)

# -------------------- 3. PAGE FUNCTIONS --------------------

def render_onboarding_page():
    
    st.markdown("<div class='title'>Welcome to Your Mood Journal!</div>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle'>Let's start by entering your name to load your journal.</div>", unsafe_allow_html=True)

    with st.container():
        name = st.text_input("Enter your name:", key="name_input", placeholder="Enter your name")
        
        if st.button("Start Journaling 🚀", use_container_width=True):
            if name:
                st.session_state.user_name = name.strip()
                load_diary(st.session_state.user_name)
                
                st.session_state.page = "fortune_draw"
                st.rerun() 
            else:
                st.error("Please enter your name to proceed.")


def render_fortune_draw_page():
    
    user = st.session_state.user_name
    st.markdown(f"<div class='title'>⛩️ Daily Fortune Draw</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='subtitle'>Welcome back, {user}! Draw your fortune to guide your day.</div>", unsafe_allow_html=True)
    
    draw_container = st.empty()
    
    if not st.session_state.fortune_drawn:
        draw_container.markdown(
            f"<div class='shaking-container'>", unsafe_allow_html=True
        )
        draw_container.markdown(
            f"<div class='shaking-icon'>🎋</div>", unsafe_allow_html=True
        )
        
        if st.button("🥠 Draw Your Destiny! (Daily Draw)", use_container_width=True):
            
            for i in range(5):
                icon = "🎍" if i % 2 == 0 else "🎋"
                draw_container.markdown(
                    f"<div class='shaking-container'><div class='shaking-icon'>{icon}</div></div>", 
                    unsafe_allow_html=True
                )
                time.sleep(0.05) 

            fortune = random.choice(FORTUNE_SLIPS)
            st.session_state.fortune_result = fortune
            st.session_state.fortune_drawn = True
            save_diary() 
            st.balloons()
            st.rerun() 
        
    
    if st.session_state.fortune_drawn and st.session_state.fortune_result:
        level, emoji, description = st.session_state.fortune_result
        
        draw_container.empty() 
        
        st.markdown("---")
        st.markdown(f"### ✨ Your Daily Guidance for {datetime.date.today().strftime('%Y-%m-%d')}")
        
        st.markdown("<div class='fortune-result-box'>", unsafe_allow_html=True)
        st.markdown(f"<div class='fortune-level'>{level}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='fortune-emoji'>{emoji}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='fortune-description'>{description}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("---")
        if st.button("Start Journaling for Today 📝", use_container_width=True):
            st.session_state.page = "date"
            st.rerun()

    elif st.session_state.fortune_drawn:
        st.info("You have already drawn your fortune for today. Please start journaling!")
        if st.button("Go to Journal 📝", use_container_width=True):
            st.session_state.page = "date"
            st.rerun()


def render_date_page():
    
    update_pet_status() 
    
    user = st.session_state.user_name
    points = st.session_state.total_points
    current_streak = calculate_streak(st.session_state.diary) 

    st.markdown(f"<div class='title'>🌸 Hi, {user}!</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='subtitle'>🔥 **Streak:** {current_streak} days | ⭐ **Mood Points:** {points} | Select a date to begin your entry.</div>", unsafe_allow_html=True)
    
    if st.session_state.fortune_result:
        level, emoji, _ = st.session_state.fortune_result
        st.success(f"🔮 Today's Fortune: **{level} {emoji}** - Use this guidance for your entry!")
    
    advice = analyze_recent_mood_for_advice(st.session_state.diary)
    st.markdown(f"<div class='advice-box'>💡 **Today's Insight:** {advice}</div>", unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("📅 **Choose a date:**") # Repositioned label for styling
    selected_date = st.date_input("Choose a date:", value=st.session_state.selected_date, key="date_picker", label_visibility="collapsed")
    st.session_state.selected_date = selected_date
    st.markdown("---")
    
    col1, col2, col3, col4 = st.columns(4) 
    date_key = selected_date.strftime("%Y-%m-%d")
    is_logged = date_key in st.session_state.diary
    button_text = "Next ➜ Edit/Choose Mood" if is_logged else "Next ➜ Choose Mood"
    
    if col1.button(button_text, use_container_width=True):
        st.session_state.page = "mood"
        st.rerun()
    if col2.button("📆 View Monthly Calendar", use_container_width=True):
        st.session_state.page = "calendar"
        st.rerun()
    if col3.button("🔮 View Fun Insights", use_container_width=True):
        st.session_state.page = "insight"
        st.rerun()
    if col4.button("🏆 Achievements & Rewards", use_container_width=True): 
        st.session_state.page = "rewards"
        st.rerun()

def render_mood_page():
    date_key = st.session_state.selected_date.strftime("%Y-%m-%d")
    st.markdown("<div class='title'>How do you feel, today?</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='subtitle'>{date_key}</div>", unsafe_allow_html=True)
    
    st.markdown("### Choose the emotion that best represents your current mood:")
    
    current_mood = st.session_state.diary.get(date_key, {}).get("mood", None)
    if current_mood and st.session_state.selected_mood_emoji is None:
        st.session_state.selected_mood_emoji = current_mood
        
    # Get mood names for options
    mood_names = list(MOOD_MAPPING.keys())

    # Use st.radio to select emotion
    selected_name = st.radio(
        "Select an emotion to summon your companion:",
        options=mood_names,
        format_func=lambda x: f"{MOOD_MAPPING[x]} {x}",
        index=mood_names.index(next((k for k, v in MOOD_MAPPING.items() if v == st.session_state.selected_mood_emoji), "Happy")) if st.session_state.selected_mood_emoji else 0,
        horizontal=True,
    )
    
    # Update session state with emoji
    selected_emoji = MOOD_MAPPING[selected_name]
    st.session_state.selected_mood_emoji = selected_emoji
    
    st.markdown("---")
    
    col_nav1, col_nav2 = st.columns(2)
    
    if col_nav1.button("🐾 Interact with Companion", use_container_width=True):
        # Navigate to pet interaction page
        st.session_state.page = "pet_interact" 
        st.rerun()

    if col_nav2.button("⬅ Back to Date", use_container_width=True):
        st.session_state.page = "date"
        st.rerun()

# --- NEW: Pet Interaction Page (Step 3/3b) ---
def render_pet_interact_page():
    
    if "last_interaction_success" in st.session_state:
        # Display success message after a successful interaction
        st.success(st.session_state.last_interaction_success)
        del st.session_state.last_interaction_success
          
    mood_emoji = st.session_state.selected_mood_emoji
    
    pet_data = MOOD_PET_MAPPING.get(mood_emoji, MOOD_PET_MAPPING["😀"])
    
    pet_name = pet_data["name"]
    pet_emoji = pet_data["emoji"]
    pet_img_path = pet_data["img_path"] 
    pet_desc = pet_data["desc"]

    health = st.session_state.pet_health
    happy = st.session_state.pet_happiness

    st.markdown(f"<div class='title'>🐾 {pet_emoji} Interact with Your Companion</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='subtitle'>You are feeling {mood_emoji}. Meet your **{pet_name}**!</div>", unsafe_allow_html=True)

    # Pet Image (Handling potential FileNotFoundError)
    st.markdown("<div class='pet-image-container'>", unsafe_allow_html=True)
    try:
        st.image(pet_img_path, caption=f"{pet_name} - {pet_desc}", width=PET_IMAGE_WIDTH)
    except FileNotFoundError:
        st.error(f"⚠️ Image not found! Please ensure '{pet_img_path}' exists in your **pet_images** folder.")
        # Fallback to large emoji
        st.markdown(f"<div style='font-size: 100px;'>{pet_emoji}</div>", unsafe_allow_html=True)
    except Exception as e:
        st.error(f"⚠️ Image loading error: {e}. Check the file path and type.")
        st.markdown(f"<div style='font-size: 100px;'>{pet_emoji}</div>", unsafe_allow_html=True)
        
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Status display
    st.markdown("---")
    st.markdown("##### ❤️ Health")
    st.progress(health, text=f"**{health}%**")
    st.markdown("##### 😊 Happiness")
    st.progress(happy, text=f"**{happy}%**")
    
    st.markdown("---")
    st.markdown("### ✨ Daily Free Interaction")
    
    col_interact_1, col_interact_2 = st.columns(2)
    
    # Pet button (focus on happiness)
    if col_interact_1.button(f"Pet {pet_name}", key="pet_interact_stroke", use_container_width=True):
        happy_boost = random.randint(10, 20)
        health_boost = random.randint(1, 5)
        
        st.session_state.pet_happiness = min(100, happy + happy_boost)
        st.session_state.pet_health = min(100, health + health_boost)
        
        st.session_state.last_interaction_success = f"💖 {pet_name} purrs happily! Happiness +{happy_boost}, Health +{health_boost}"
        save_diary()
        st.rerun()

    # Feed button (focus on health)
    if col_interact_2.button(f"Feed {pet_name}", key="pet_interact_feed", use_container_width=True):
        health_boost = random.randint(15, 25)
        happy_boost = random.randint(1, 5)
        
        st.session_state.pet_health = min(100, health + health_boost)
        st.session_state.pet_happiness = min(100, happy + happy_boost)
        
        st.session_state.last_interaction_success = f"🦴 {pet_name} eats heartily! Health +{health_boost}, Happiness +{happy_boost}"
        save_diary()
        st.rerun()

    st.markdown("---")
    
    col_nav1, col_nav2 = st.columns(2)
    
    if col_nav1.button("📝 Continue to Journal", use_container_width=True):
        st.session_state.page = "journal"
        st.rerun()
    
    if col_nav2.button("⬅ Back to Mood Selection", use_container_width=True):
        st.session_state.page = "mood"
        st.rerun()


def render_journal_page():
    
    date_key = st.session_state.selected_date.strftime("%Y-%m-%d")
    mood_icon = st.session_state.selected_mood_emoji
    existing_entry = st.session_state.diary.get(date_key, {})
    initial_text = existing_entry.get("text", "")
    initial_tags = existing_entry.get("tags", [])
    st.markdown(f"<div class='title'>📝 Journal Entry for {date_key}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='subtitle'>Your mood: {mood_icon}</div>", unsafe_allow_html=True)
    
    pet_data = MOOD_PET_MAPPING.get(mood_icon, MOOD_PET_MAPPING["😀"])
    st.info(f"✨ Companion Tip: Your {pet_data['name']} is listening to your thoughts... ({pet_data['desc']})")
    
    prompt_seed = st.session_state.selected_date.toordinal()
    random.seed(prompt_seed)
    daily_prompt = random.choice(DAILY_PROMPTS)
    random.seed() 
    st.info(f"✨ **Today's Prompt:** {daily_prompt}")
    selected_tags = st.multiselect(
        "🏷️ **Select relevant activities/causes:** (Optional)", 
        options=ACTIVITY_TAGS, 
        default=initial_tags,
        key="activity_tags"
    )
    diary_text = st.text_area("Write about your day:", value=initial_text, height=200, key="diary_text_area", placeholder="Start typing here...")
    col1, col2 = st.columns(2)
    if col1.button("💾 Save & Get Reflection", use_container_width=True):
        response = get_diary_response(diary_text)
        reward_points = 0
        is_new_entry = date_key not in st.session_state.diary
        if is_new_entry:
            reward_points = POINTS_PER_ENTRY
            st.session_state.total_points += reward_points
        st.session_state.diary[date_key] = {
            "mood": mood_icon, 
            "text": diary_text, 
            "response": response,
            "score": MOOD_SCORES.get(mood_icon, 3),
            "tags": selected_tags
        }
        save_diary()
        st.session_state.page = "action_page"
        st.session_state.last_response = response
        st.session_state.reward_points = reward_points
        st.rerun()
    if col2.button("⬅ Back to Mood", use_container_width=True):
        st.session_state.page = "mood"
        st.rerun()
    if 'response' in existing_entry:
        st.markdown(f"---")
        st.markdown(f"### 💬 Last Reflection:")
        st.info(f"*{existing_entry['response']}*")

# -------------------- 4. OPTIMIZED ACTION PAGE (Journal End Page) - ENGLISH VERSION --------------------
def render_action_page():
    """
    The final page after a journal entry is successfully saved.
    - Displays point rewards.
    - Shows the emotional reflection/response.
    - Displays a random surprise fact.
    - Provides navigation options for the next step.
    """
    
    st.markdown("<div class='title'>✅ Entry Saved Successfully!</div>", unsafe_allow_html=True)
    
    # ------------------ 1. Reward & Pet Interaction ------------------
    col_reward, col_points = st.columns([2, 1])

    if st.session_state.reward_points > 0:
        # Display point reward
        col_reward.success(f"🎉 **Reward!** You earned **{st.session_state.reward_points} Mood Points** for your first entry today!")
        st.balloons()
    else:
        # Display update status
        col_reward.info("📝 **Updated:** You have updated today's journal entry.")

    col_points.metric("⭐ Total Mood Points", st.session_state.total_points)

    st.markdown("---")

    # ------------------ 2. Emotional Reflection ------------------
    st.markdown(f"### 🌈 Today's Reflection:")
    # Use a different background color to highlight the reflection
    st.markdown(f"<div class='advice-box' style='background-color:#ffe0b2; color:#4b3f37;'>💭 *{st.session_state.last_response}*</div>", unsafe_allow_html=True)
    
    # ------------------ 3. Daily Surprise (25% chance) ------------------
    if random.random() < 0.25: 
        st.markdown("### 🔮 Daily Surprise:")
        st.info(random.choice(SURPRISE_FACTS))
        
    st.markdown("---")

    # ------------------ 4. Next Step Navigation ------------------
    st.markdown("### 🚀 What would you like to do next?")
    col1, col2, col3 = st.columns(3)
    
    if col1.button("🔮 View Fun Insights", use_container_width=True):
        st.session_state.page = "insight"
        st.rerun()
        
    if col2.button("🏆 Achievements & Rewards", use_container_width=True): 
        st.session_state.page = "rewards"
        st.rerun()
        
    if col3.button("🏠 Back to Home", use_container_width=True):
        st.session_state.selected_date = datetime.date.today()
        st.session_state.selected_mood_emoji = None
        st.session_state.page = "date"
        st.rerun()

    st.markdown("<br>", unsafe_allow_html=True) # Add space
# -------------------- END OF OPTIMIZED ACTION PAGE --------------------

def render_calendar_page():
    
    col_nav_1, col_nav_2, col_nav_3 = st.columns([1, 2, 1])
    
    current_date = st.session_state.selected_date

    with col_nav_1:
        if st.button("◀ Previous Month", key="prev_month", use_container_width=True):
            prev_month_date = current_date.replace(day=1) - datetime.timedelta(days=1)
            st.session_state.selected_date = prev_month_date
            st.rerun()

    with col_nav_3:
        if st.button("Next Month ▶", key="next_month", use_container_width=True):
            if current_date.month == 12:
                next_month_date = current_date.replace(year=current_date.year + 1, month=1, day=1)
            else:
                next_month_date = current_date.replace(month=current_date.month + 1, day=1)
            st.session_state.selected_date = next_month_date
            st.rerun()
            
    year, month = st.session_state.selected_date.year, st.session_state.selected_date.month
    
    with col_nav_2:
        st.markdown(f"<div style='text-align:center; font-size: 24px; font-weight: bold; color: {ACCENT_COLOR}; padding-top:10px;'>{calendar.month_name[month]} {year}</div>", unsafe_allow_html=True)
        
    st.markdown("---")
    
    cal = calendar.monthcalendar(year, month)
    weekdays = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    col_w = st.columns(7)
    for i, d in enumerate(weekdays):
        col_w[i].markdown(f"<div style='text-align:center; font-weight:bold; color:{SUBTITLE_COLOR};'>{d}</div>", unsafe_allow_html=True)
    for week in cal:
        cols = st.columns(7)
        for i, day in enumerate(week):
            if day != 0:
                date_str = f"{year}-{month:02d}-{day:02d}"
                entry = st.session_state.diary.get(date_str, {})
                mood = entry.get("mood", "")
                display_day = day
                display_mood = mood or "•"

                cell_bg = '#f0f0f0' if is_dark and mood else ('#ffffff' if is_dark else ('#e6ffe6' if mood else '#ffffff'))
                cell_text_color = '#000000'
                
                if cols[i].button("", key=f"cal_day_{date_str}", use_container_width=True):
                    st.session_state.selected_date = datetime.date(year, month, day)
                    st.session_state.selected_mood_emoji = mood
                    st.session_state.page = "journal"
                    st.rerun()
                
                cols[i].markdown(
                    f"""<div style='text-align:center; border: 1px solid {'#ccc'}; border-radius: 5px; margin: 2px; padding: 5px; height: 50px; background-color: {cell_bg}; color: {cell_text_color};'>
                        {display_day}<br>
                        <span style='font-size: 1.2em;'>{display_mood}</span>
                    </div>""", unsafe_allow_html=True
                )
            else:
                cols[i].markdown("<div style='width: 45px; height: 45px; margin: 2px;'></div>", unsafe_allow_html=True)
    st.markdown("---")
    if st.button("⬅ Back to Date Selection", use_container_width=True):
        st.session_state.page = "date"
        st.rerun()

def render_insight_page():
    
    user = st.session_state.user_name
    st.markdown(f"<div class='title'>🔮 {user}'s Fun Insights!</div>", unsafe_allow_html=True)
    
    if not st.session_state.diary:
        st.warning("You need at least one entry to unlock your insights!")
        if st.button("Start Journaling Now", use_container_width=True):
            st.session_state.page = "date"
            st.rerun()
        return

    all_dates = list(st.session_state.diary.keys())
    
    # ------------------ 1. Mood Trend Chart (Plotly) ------------------
    st.markdown("---")
    st.markdown("### 📊 Recent Mood Trend (Past 30 Days)")

    data = []
    for date_str, entry in st.session_state.diary.items():
        data.append({
            'Date': datetime.datetime.strptime(date_str, "%Y-%m-%d").date(),
            'Score': entry.get('score', 3)
        })

    df = pd.DataFrame(data)
    df = df.set_index('Date').sort_index()

    today = datetime.date.today()
    thirty_days_ago = today - datetime.timedelta(days=30)
    recent_df = df[df.index >= thirty_days_ago].copy()
    
    if not recent_df.empty:
        recent_df.rename(columns={'Score': 'Mood Score'}, inplace=True)
        
        fig = px.line(
            recent_df, 
            x=recent_df.index, 
            y='Mood Score',
            title='Mood Score Trend Over Past 30 Days',
            labels={'Date': 'Date', 'Mood Score': 'Score'},
            line_shape='spline',
            template="plotly_dark" if is_dark else "plotly_white" 
        )
        fig.update_yaxes(range=[1, 5]) 
        st.plotly_chart(fig, use_container_width=True)
        
        avg_score = recent_df['Mood Score'].mean()
        st.info(f"💡 **Average Score (Past 30 Days):** {avg_score:.2f} / 5.0")
    else:
        st.info("More entries (within the past 30 days) are needed to display the trend chart.")
        
    # ------------------ 2. Activity Tag Chart (Plotly) ------------------
    
    all_tags = []
    tag_scores = {}
    tag_counts = {}
    
    for entry in st.session_state.diary.values():
        score = entry.get('score', 3)
        for tag in entry.get('tags', []):
            all_tags.append(tag)
            tag_counts[tag] = tag_counts.get(tag, 0) + 1
            tag_scores[tag] = tag_scores.get(tag, []) + [score]
            
    st.markdown("---")
    if tag_counts:
        tag_df = pd.Series(tag_counts).sort_values(ascending=False).to_frame(name='Count').reset_index()
        tag_df.columns = ['Activity Tag', 'Count']
        
        st.markdown(f"### 🏷️ Activity Tag Frequency (Top {min(10, len(tag_df))})")
        
        fig_bar = px.bar(
            tag_df.head(10), 
            x='Activity Tag', 
            y='Count',
            title='Frequency of Logged Activity Tags',
            color='Count', 
            color_continuous_scale=px.colors.sequential.Teal,
            template="plotly_dark" if is_dark else "plotly_white" 
        )
        fig_bar.update_xaxes(title=None) 
        st.plotly_chart(fig_bar, use_container_width=True)

        avg_scores = {tag: sum(scores) / len(scores) for tag, scores in tag_scores.items()}
        avg_df = pd.Series(avg_scores).sort_values(ascending=False).to_frame(name='Average Mood Score')
        
        st.markdown(f"### 💖 Activity Correlation (Average Score)")
        st.info("Higher scores indicate activities generally associated with better moods.")
        st.dataframe(avg_df, use_container_width=True)
    else:
        st.info("Please use activity tags more often to unlock deeper analysis!")

    # Milestones, Top Mood, Throwback
    first_entry_date = min(all_dates)
    total_entries = len(all_dates)
    st.markdown("<div class='insight-box'>", unsafe_allow_html=True)
    st.markdown(f"### 🎉 Your Journaling Milestones")
    st.markdown(f"**Total Entries:** **{total_entries}** 🥳")
    st.markdown(f"**First Entry:** You started your journey on **{first_entry_date}**!")
    st.markdown("</div>", unsafe_allow_html=True)

    mood_list = [entry['mood'] for entry in st.session_state.diary.values()]
    top_mood_emoji = pd.Series(mood_list).mode()[0]
    top_mood_name = next(name for name, emoji in MOOD_MAPPING.items() if emoji == top_mood_emoji)
    st.markdown("<div class='insight-box'>", unsafe_allow_html=True)
    st.markdown(f"### 🥇 Your Top Mood")
    st.markdown(f"Your most common mood so far is **{top_mood_name} {top_mood_emoji}**! Keep exploring your emotions.")
    st.markdown("</div>", unsafe_allow_html=True)

    happy_tags = []
    for entry in st.session_state.diary.values():
        if entry.get('mood') == '😀':
            happy_tags.extend(entry.get('tags', []))
            
    if happy_tags:
        st.markdown(f"---")
        top_happy_tag = pd.Series(happy_tags).mode()
        st.markdown("<div class='insight-box'>", unsafe_allow_html=True)
        st.markdown(f"### 💖 What Makes You Happy?")
        st.markdown(f"Based on your **Happy 😀** entries, the activity most associated with your joy is:")
        st.markdown(f"### **{top_happy_tag[0]}** 🎉")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown(f"### 🕰️ Throwback Entry")
    if st.button("Shuffle and Reveal a Past Entry!", use_container_width=True):
        random_date = random.choice(all_dates)
        entry_data = st.session_state.diary[random_date]
        st.markdown("<div class='insight-box'>", unsafe_allow_html=True)
        st.markdown(f"**📅 Date:** **{random_date}** | **Mood:** {entry_data['mood']}")
        st.markdown(f"**Tags:** {', '.join(entry_data.get('tags', ['None']))}")
        st.markdown(f"**Your Thoughts:** *{entry_data['text'][:200]}...*")
        st.markdown(f"**Reflection:** {entry_data['response']}")
        st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("---")
    if st.button("⬅ Back to Date Selection"): 
        st.session_state.page = "date"
        st.rerun()

# --- Rewards and Pet Page ---
def render_rewards_and_pet_page():
    user = st.session_state.user_name
    points = st.session_state.total_points
    current_streak = calculate_streak(st.session_state.diary)
    unlocked_achievements = calculate_achievements(st.session_state.diary, current_streak)
    is_dark = st.session_state.get("dark_mode", False)
    
    st.markdown(f"<div class='title'>🏆 {user}'s Achievements & Rewards</div>", unsafe_allow_html=True)
    st.markdown(f"### ⭐ Mood Points: **{points}**")
    st.markdown("---")
    
    tab1, tab2 = st.tabs(["🏆 Achievements", "🎁 Rewards Shop"])


    # ========================== TAB 1: ACHIEVEMENTS ==========================
    with tab1:
        st.markdown("### 🏅 Achievements Log")
        for ach in ACHIEVEMENTS:
            unlocked = ach['name'] in unlocked_achievements
            
            if unlocked:
                icon_html = f'<span class="achievement-icon-gold">🏆</span>' 
            else:
                icon_html = f'<span class="achievement-icon-grey">🔗</span>'

            st.markdown(f"""
                <div style="display: flex; align-items: center; margin-bottom: 10px;">
                    {icon_html}
                    <div>
                        <div style="font-weight: bold; color: {TEXT_MAIN};">{ach['name']}</div>
                        <div style="font-size: 0.9em; color: {SUBTITLE_COLOR};">{ach['desc']}</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)


    # ========================== TAB 2: REWARDS SHOP ==========================
    with tab2:
        st.markdown("### 🎁 Rewards Shop")
        can_afford = points >= DARK_MODE_COST
        
        st.markdown("#### ✨ Dark Mode Toggle (Premium Feature)")
        st.markdown(f"*{'Currently Active!' if is_dark else 'Give your elements a break! Toggle dark mode.'}*")
        
        if is_dark:
            if st.button("Turn Light Mode On ☀️", key="toggle_light", use_container_width=True):
                st.session_state.dark_mode = False
                save_diary()
                st.rerun()
        elif not can_afford:
            st.button(f"Cannot Afford ({DARK_MODE_COST} Points needed)", disabled=True, use_container_width=True)
        else:
            if st.button(f"Redeem Dark Mode ({DARK_MODE_COST} Points)", key="redeem_dark", use_container_width=True):
                st.session_state.total_points -= DARK_MODE_COST
                st.session_state.dark_mode = True
                save_diary()
                st.success("Dark Mode activated! Enjoy the change. Your new point total has been saved.")
                st.rerun()
                
    st.markdown("---")
    if st.button("⬅ Back to Date Selection", use_container_width=True):
        st.session_state.page = "date"
        st.rerun()


# -------------------- 5. MAIN APPLICATION LOGIC (PAGE ROUTER) --------------------
if st.session_state.page == "onboarding":
    render_onboarding_page()
elif st.session_state.page == "fortune_draw":
    render_fortune_draw_page()
elif st.session_state.page == "date":
    render_date_page()
elif st.session_state.page == "mood":
    render_mood_page()
elif st.session_state.page == "pet_interact": 
    render_pet_interact_page()
elif st.session_state.page == "journal":
    if st.session_state.selected_mood_emoji:
        render_journal_page()
    else:
        st.session_state.page = "mood"
        st.rerun()
elif st.session_state.page == "action_page":
    render_action_page()
elif st.session_state.page == "calendar":
    render_calendar_page()
elif st.session_state.page == "insight": 
    render_insight_page()
elif st.session_state.page == "rewards": 
    render_rewards_and_pet_page()