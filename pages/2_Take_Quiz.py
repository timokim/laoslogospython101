import streamlit as st

from lib.utils import get_db, render_markdown

st.set_page_config(page_title="Take Quiz", page_icon="✏️", layout="centered")

db = get_db()

st.title("✏️ Take Quiz")

query_code = st.query_params.get("code", "")
code = st.text_input("Quiz code", value=query_code, placeholder="e.g. ABC123").strip().upper()

if not code:
    st.info("Enter the quiz code your instructor gave you.")
    st.stop()

quiz = db.get_quiz_by_code(code)
if not quiz:
    st.warning("Quiz not found or not deployed yet. Check the code with your instructor.")
    st.stop()

questions = db.list_questions(quiz["id"], active_only=True)
if not questions:
    st.warning("This quiz has no active questions right now. Check with your instructor.")
    st.stop()

if st.session_state.get("quiz_submitted"):
    result = st.session_state.quiz_result
    st.success(f"Submitted! Thanks, **{result['student_name']}**.")
    st.balloons()
    st.metric("Your score", f"{result['score']} / {result['total']}")
    if st.button("Take again"):
        del st.session_state.quiz_submitted
        del st.session_state.quiz_result
        st.rerun()
    st.stop()

st.subheader(quiz["title"])
st.caption(f"{len(questions)} questions")

student_name = st.text_input("Your name", placeholder="Type your full name")

if not student_name.strip():
    st.info("Enter your name to begin.")
    st.stop()

answers: dict[str, int] = {}

for i, q in enumerate(questions, start=1):
    st.divider()
    st.markdown(f"**Question {i}**")
    render_markdown(q["question_text"])
    choice = st.radio(
        "Choose one:",
        options=list(range(len(q["options"]))),
        format_func=lambda idx, opts=q["options"]: opts[idx],
        key=f"q_{q['id']}",
        label_visibility="collapsed",
    )
    answers[q["id"]] = choice

st.divider()
if st.button("Submit quiz", type="primary", use_container_width=True):
    result = db.submit_quiz(quiz["id"], student_name, answers)
    st.session_state.quiz_submitted = True
    st.session_state.quiz_result = result
    st.rerun()
