
import streamlit as st
import random
import re
from difflib import SequenceMatcher

# ==========================================================
# RIDDLE AI - CAN YOU OUTSMART THE MACHINE?
# A school AI Club exhibition project
# ==========================================================

st.set_page_config(
    page_title="RIDDLE AI | Outsmart the Machine",
    page_icon="🧠",
    layout="wide"
)

# -------------------- RIDDLE DATABASE --------------------

RIDDLES = [
    {
        "question": "I have keys but no locks. I have space but no room. You can enter, but you cannot go inside. What am I?",
        "answer": "keyboard",
        "aliases": ["computer keyboard", "a keyboard", "the keyboard"],
        "hint": "You use me to type messages on a computer.",
        "difficulty": "Easy"
    },
    {
        "question": "I have hands but cannot clap. What am I?",
        "answer": "clock",
        "aliases": ["a clock", "the clock", "wall clock"],
        "hint": "You probably look at me every day to check the time.",
        "difficulty": "Easy"
    },
    {
        "question": "What has a face and two hands but no arms or legs?",
        "answer": "clock",
        "aliases": ["a clock", "watch", "wristwatch"],
        "hint": "It helps you know what time it is.",
        "difficulty": "Easy"
    },
    {
        "question": "What gets wetter the more it dries?",
        "answer": "towel",
        "aliases": ["a towel", "the towel", "bath towel"],
        "hint": "You often use me after a shower.",
        "difficulty": "Easy"
    },
    {
        "question": "What has many teeth but cannot bite?",
        "answer": "comb",
        "aliases": ["a comb", "hair comb"],
        "hint": "You might use me while getting ready in the morning.",
        "difficulty": "Easy"
    },
    {
        "question": "The more you take, the more you leave behind. What are they?",
        "answer": "footsteps",
        "aliases": ["footprints", "steps", "foot steps"],
        "hint": "Think about what you leave on the ground when walking.",
        "difficulty": "Medium"
    },
    {
        "question": "What can travel around the world while staying in one corner?",
        "answer": "stamp",
        "aliases": ["a stamp", "postage stamp", "the stamp"],
        "hint": "Look at the corner of an envelope.",
        "difficulty": "Medium"
    },
    {
        "question": "I speak without a mouth and hear without ears. I have no body, but I come alive with the wind. What am I?",
        "answer": "echo",
        "aliases": ["an echo", "the echo"],
        "hint": "Shout into a valley and listen carefully.",
        "difficulty": "Medium"
    },
    {
        "question": "What has cities but no houses, forests but no trees, and rivers but no water?",
        "answer": "map",
        "aliases": ["a map", "the map", "world map"],
        "hint": "You might use me to find your way.",
        "difficulty": "Medium"
    },
    {
        "question": "I am an odd number. Remove one letter and I become even. What number am I?",
        "answer": "seven",
        "aliases": ["7", "the number seven"],
        "hint": "Spell the number in English, then remove its first letter.",
        "difficulty": "Medium"
    },
    {
        "question": "A person looks at a photograph and says, 'Brothers and sisters I have none, but that person's father is my father's son.' Who is in the photograph?",
        "answer": "his son",
        "aliases": ["her son", "my son", "their son", "the person's son", "son"],
        "hint": "The speaker's father's son is the speaker themself.",
        "difficulty": "AI Challenge"
    },
    {
        "question": "You have three switches outside a closed room. Only one controls a bulb inside. You may operate the switches however you like, but enter the room only once. How can you identify the correct switch?",
        "answer": "use heat",
        "aliases": [
            "turn one switch on and wait, turn it off, turn another on",
            "switch on one bulb and feel the heat",
            "check whether the bulb is lit or warm",
            "the warm bulb",
            "turn one switch on, turn it off, turn another on, then check the bulb's heat"
        ],
        "hint": "A bulb can give you information even when it is switched off.",
        "difficulty": "AI Challenge"
    },
    {
        "question": "Two fathers and two sons go fishing. They catch three fish, and each person gets one fish. How is this possible?",
        "answer": "three people",
        "aliases": [
            "grandfather father and son",
            "grandfather, father and son",
            "a grandfather, his son, and his grandson",
            "grandfather, father, son",
            "there are three people"
        ],
        "hint": "One person can be both a son and a father.",
        "difficulty": "AI Challenge"
    },
    {
        "question": "I am always in front of you, but you can never see me. What am I?",
        "answer": "future",
        "aliases": ["the future", "your future"],
        "hint": "I have not happened yet.",
        "difficulty": "AI Challenge"
    }
]

# -------------------- SESSION STATE --------------------

if "score" not in st.session_state:
    st.session_state.score = 0

if "questions_answered" not in st.session_state:
    st.session_state.questions_answered = 0

if "correct_answers" not in st.session_state:
    st.session_state.correct_answers = 0

if "attempts" not in st.session_state:
    st.session_state.attempts = 0

if "hint_used" not in st.session_state:
    st.session_state.hint_used = False

if "message" not in st.session_state:
    st.session_state.message = ""

if "feedback_type" not in st.session_state:
    st.session_state.feedback_type = ""

if "finished" not in st.session_state:
    st.session_state.finished = False

if "history" not in st.session_state:
    st.session_state.history = []

if "used_riddles" not in st.session_state:
    st.session_state.used_riddles = []

if "riddle" not in st.session_state:
    st.session_state.riddle = None

if "difficulty_mode" not in st.session_state:
    st.session_state.difficulty_mode = "AI Challenge"

# -------------------- AI ANSWER CHECKER --------------------

def normalize(text):
    """Clean an answer before comparing it."""
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9\s]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text


def calculate_similarity(user_answer, riddle):
    """
    Compare the player's answer with the expected answer
    and known acceptable alternatives.
    """
    user = normalize(user_answer)

    if not user:
        return 0

    accepted_answers = [
        riddle["answer"]
    ] + riddle.get("aliases", [])

    best_score = 0

    for expected in accepted_answers:
        target = normalize(expected)

        if user == target:
            return 100

        # Accept an answer containing a complete expected phrase.
        if f" {target} " in f" {user} ":
            best_score = max(best_score, 95)

        # Similarity matching for spelling variations.
        ratio = SequenceMatcher(
            None, user, target
        ).ratio()

        best_score = max(best_score, round(ratio * 100))

    return best_score


def is_correct(user_answer, riddle):
    """Avoid accepting answers just because they share a word."""
    user = normalize(user_answer)

    if not user:
        return False, 0

    accepted = [
        normalize(riddle["answer"])
    ] + [
        normalize(a) for a in riddle.get("aliases", [])
    ]

    # Exact match or an accepted answer phrase.
    for target in accepted:
        if user == target:
            return True, 100

        # Longer responses may include an accepted answer.
        if len(target) >= 4 and f" {target} " in f" {user} ":
            return True, 95

    similarity = max(
        SequenceMatcher(None, user, target).ratio()
        for target in accepted
    )

    percentage = round(similarity * 100)

    # Require a high match for fuzzy acceptance.
    return percentage >= 85, percentage


# -------------------- DIFFICULTY ENGINE --------------------

def get_current_difficulty():
    mode = st.session_state.difficulty_mode

    if mode != "AI Challenge":
        return mode

    answered = st.session_state.questions_answered
    correct = st.session_state.correct_answers

    if answered == 0:
        return "Easy"

    accuracy = correct / answered

    if answered >= 3 and accuracy >= 0.75:
        return "AI Challenge"

    if answered >= 2 and accuracy >= 0.50:
        return "Medium"

    return "Easy"


def get_next_riddle():
    difficulty = get_current_difficulty()

    available = [
        r for r in RIDDLES
        if r["difficulty"] == difficulty
        and RIDDLES.index(r) not in st.session_state.used_riddles
    ]

    # If the selected level is exhausted, use any unused riddle.
    if not available:
        available = [
            r for r in RIDDLES
            if RIDDLES.index(r) not in st.session_state.used_riddles
        ]

    if not available:
        st.session_state.finished = True
        st.session_state.riddle = None
        return

    selected = random.choice(available)

    st.session_state.riddle = selected
    st.session_state.used_riddles.append(RIDDLES.index(selected))
    st.session_state.attempts = 0
    st.session_state.hint_used = False
    st.session_state.message = ""
    st.session_state.feedback_type = ""
    st.session_state.finished = False


# -------------------- FUTURISTIC DESIGN --------------------

st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #07111f 0%, #10243b 55%, #07111f 100%);
    color: #f1f5f9;
}
h1, h2, h3 {
    color: #55edc0 !important;
}
[data-testid="stMetric"] {
    background: rgba(24, 44, 66, 0.85);
    border: 1px solid #24516a;
    padding: 16px;
    border-radius: 14px;
}
.riddle-card {
    background: rgba(18, 38, 59, 0.95);
    border: 1px solid #35d9b0;
    border-radius: 18px;
    padding: 28px;
    margin: 12px 0 22px 0;
}
.small-label {
    color: #8ca8c3;
    font-size: 13px;
    letter-spacing: 2px;
}
div.stButton > button {
    border-radius: 10px;
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)

# -------------------- SIDEBAR --------------------

with st.sidebar:
    st.markdown("# 🧠 RIDDLE AI")
    st.caption("HUMAN INTELLIGENCE vs MACHINE LOGIC")
    st.divider()

    mode = st.selectbox(
        "SELECT GAME MODE",
        ["Easy", "Medium", "AI Challenge"],
        index=["Easy", "Medium", "AI Challenge"].index(
            st.session_state.difficulty_mode
        )
    )

    if mode != st.session_state.difficulty_mode:
        st.session_state.difficulty_mode = mode
        st.session_state.riddle = None
        st.session_state.finished = False
        st.session_state.attempts = 0
        st.session_state.message = ""
        st.session_state.feedback_type = ""
        st.rerun()

    st.markdown("### 🎮 HOW TO PLAY")
    st.write("1. Read the riddle.")
    st.write("2. Enter your answer.")
    st.write("3. You get three attempts.")
    st.write("4. Use a hint if needed.")
    st.write("5. Outsmart the machine!")

    st.divider()
    st.caption("POWERED BY PYTHON SIMILARITY MATCHING")

# -------------------- MAIN HEADER --------------------

st.markdown(
    "<p class='small-label'>EXPERIMENT 001 // HUMAN REASONING</p>",
    unsafe_allow_html=True
)

st.title("RIDDLE AI")
st.subheader("Can you outsmart the machine?")
st.write(
    "Think carefully. The AI is analysing your answers, "
    "learning from your performance, and adjusting the challenge."
)

# -------------------- SCOREBOARD --------------------

accuracy = (
    round(
        st.session_state.correct_answers
        / st.session_state.questions_answered * 100
    )
    if st.session_state.questions_answered > 0
    else 0
)

col1, col2, col3, col4 = st.columns(4)

col1.metric("🏆 SCORE", st.session_state.score)
col2.metric("🧩 ATTEMPTED", st.session_state.questions_answered)
col3.metric("✓ CORRECT", st.session_state.correct_answers)
col4.metric("🎯 ACCURACY", f"{accuracy}%")

st.divider()

# -------------------- START GAME --------------------

if st.session_state.riddle is None and not st.session_state.finished:
    st.markdown("### READY TO TEST YOUR INTELLIGENCE?")
    st.write("The machine is waiting. Let's see what you've got.")

    if st.button("🚀 START GAME", use_container_width=True):
        get_next_riddle()
        st.rerun()

# -------------------- GAME OVER --------------------

elif st.session_state.finished:
    st.markdown("## 🏁 CHALLENGE COMPLETE")
    st.write("You have solved all available riddles!")

    st.success(
        f"Final score: {st.session_state.score} | "
        f"Accuracy: {accuracy}%"
    )

    if st.button("🔄 PLAY AGAIN", use_container_width=True):
        st.session_state.score = 0
        st.session_state.questions_answered = 0
        st.session_state.correct_answers = 0
        st.session_state.attempts = 0
        st.session_state.hint_used = False
        st.session_state.history = []
        st.session_state.used_riddles = []
        st.session_state.riddle = None
        st.session_state.finished = False
        st.session_state.message = ""
        st.session_state.feedback_type = ""
        st.rerun()

# -------------------- RIDDLE SCREEN --------------------

else:
    riddle = st.session_state.riddle

    st.markdown(
        f"<p class='small-label'>"
        f"CURRENT LEVEL // {riddle['difficulty'].upper()}"
        f"</p>",
        unsafe_allow_html=True
    )

    st.markdown(
        f"<div class='riddle-card'>"
        f"<h3>🧩 YOUR RIDDLE</h3>"
        f"<p style='font-size:21px; color:#f1f5f9;'>"
        f"{riddle['question']}</p>"
        f"</div>",
        unsafe_allow_html=True
    )

    attempts_left = 3 - st.session_state.attempts
    st.caption(f"ATTEMPTS REMAINING: {attempts_left}/3")

    # Only allow answers while the riddle is unresolved.
    if not st.session_state.message or st.session_state.feedback_type == "warning":
        with st.form("answer_form", clear_on_submit=True):
            user_answer = st.text_input(
                "YOUR ANSWER",
                placeholder="Type your answer here...",
                max_chars=150
            )

            submitted = st.form_submit_button(
                "🤖 ANALYSE ANSWER",
                use_container_width=True
            )

        if submitted:
            if not user_answer.strip():
                st.warning("Please enter an answer first.")
            else:
                st.session_state.attempts += 1
                correct, similarity = is_correct(user_answer, riddle)

                st.session_state.history.append({
                    "riddle": riddle["question"],
                    "your_answer": user_answer,
                    "similarity": similarity
                })

                if correct:
                    st.session_state.questions_answered += 1
                    st.session_state.correct_answers += 1

                    points = 100

                    if st.session_state.attempts == 2:
                        points = 70
                    elif st.session_state.attempts == 3:
                        points = 40

                    if st.session_state.hint_used:
                        points = max(20, points - 20)

                    st.session_state.score += points
                    st.session_state.message = (
                        f"✓ CORRECT! Your answer matches. "
                        f"You earned {points} points."
                    )
                    st.session_state.feedback_type = "success"

                elif st.session_state.attempts >= 3:
                    st.session_state.questions_answered += 1
                    st.session_state.message = (
                        f"❌ OUT OF ATTEMPTS! "
                        f"The expected answer was: {riddle['answer'].title()}."
                    )
                    st.session_state.feedback_type = "error"

                else:
                    st.session_state.message = (
                        f"Not quite! The AI estimates a "
                        f"{similarity}% similarity. Try again!"
                    )
                    st.session_state.feedback_type = "warning"

                st.rerun()

    # -------------------- FEEDBACK --------------------

    if st.session_state.message:
        feedback = st.session_state.feedback_type

        if feedback == "success":
            st.success(st.session_state.message)
            st.markdown("### 🤖 ANSWER ACCEPTED")
            st.progress(1.0)
            st.caption("ANSWER MATCH: 100%")

        elif feedback == "error":
            st.error(st.session_state.message)

        elif feedback == "warning":
            st.warning(st.session_state.message)

    # -------------------- HINT BUTTON --------------------

    if (
        not st.session_state.message
        or st.session_state.feedback_type == "warning"
    ):
        if st.button("💡 GET A HINT", use_container_width=True):
            st.session_state.hint_used = True
            st.info(f"💡 AI HINT: {riddle['hint']}")

        if st.session_state.hint_used:
            st.info(f"💡 AI HINT: {riddle['hint']}")

    # -------------------- NEXT RIDDLE --------------------

    if st.session_state.feedback_type in ["success", "error"]:
        st.divider()

        if st.button("➡️ NEXT RIDDLE", use_container_width=True):
            get_next_riddle()
            st.rerun()

# -------------------- ADAPTIVE AI PANEL --------------------

st.divider()
st.markdown("### 🤖 AI PERFORMANCE ANALYSIS")

if st.session_state.questions_answered == 0:
    st.write("System status: Waiting for the first response.")
else:
    accuracy = round(
        st.session_state.correct_answers
        / st.session_state.questions_answered * 100
    )

    st.progress(accuracy / 100)

    st.write(f"**Player accuracy:** {accuracy}%")

    if st.session_state.difficulty_mode == "AI Challenge":
        next_level = get_current_difficulty()

        st.write(f"**Adaptive difficulty:** {next_level}")

        if accuracy >= 75 and st.session_state.questions_answered >= 3:
            st.success(
                "High performance detected. "
                "The machine is increasing the difficulty!"
            )
        elif accuracy < 50:
            st.info(
                "The machine is keeping the challenge manageable "
                "while you improve."
            )
        else:
            st.info(
                "The machine is analysing your performance..."
            )
    else:
        st.write(
            f"**Selected mode:** {st.session_state.difficulty_mode}"
        )

st.caption(
    "RIDDLE AI v1.0 | SCHOOL AI CLUB PROJECT | "
    "Python + Streamlit + Similarity Matching"
)
