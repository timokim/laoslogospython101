import streamlit as st

from lib.utils import get_db, render_markdown

st.set_page_config(page_title="Take Midterm", page_icon="🧪", layout="centered")

db = get_db()

st.title("🧪 Take Midterm")


def _is_test(quiz: dict) -> bool:
    title = quiz.get("title", "").lower()
    return "midterm" in title or "final" in title


def _reset_test_attempt(quiz_id: str) -> None:
    for suffix in ("started", "index", "answers", "student_name"):
        st.session_state.pop(f"test_{suffix}_{quiz_id}", None)
    for key in list(st.session_state.keys()):
        if key.startswith(f"test_q_{quiz_id}_"):
            st.session_state.pop(key, None)


query_code = st.query_params.get("code", "")
code = st.text_input("Test code", value=query_code, placeholder="e.g. ABC123").strip().upper()

if not code:
    st.info("Enter the midterm or final test code your instructor gave you.")
    st.stop()

test = db.get_quiz_by_code(code)
if not test:
    st.warning("Test not found or not deployed yet. Check the code with your instructor.")
    st.stop()

if not _is_test(test):
    st.warning("This code is for a regular quiz. Please use the Take Quiz page instead.")
    st.stop()

questions = db.list_questions(test["id"], active_only=True)
if not questions:
    st.warning("This test has no active questions right now. Check with your instructor.")
    st.stop()

submitted_key = f"test_submitted_{test['id']}"
result_key = f"test_result_{test['id']}"

if st.session_state.get(submitted_key):
    result = st.session_state[result_key]
    st.success(f"Submitted! Thanks, **{result['student_name']}**.")
    st.balloons()
    st.metric("Your score", f"{result['score']} / {result['total']}")
    if st.button("Take again"):
        del st.session_state[submitted_key]
        del st.session_state[result_key]
        _reset_test_attempt(test["id"])
        st.rerun()
    st.stop()

st.subheader(test["title"])
st.caption(f"{len(questions)} questions")

started_key = f"test_started_{test['id']}"
index_key = f"test_index_{test['id']}"
answers_key = f"test_answers_{test['id']}"
name_key = f"test_student_name_{test['id']}"

if not st.session_state.get(started_key):
    student_name = st.text_input("Your name", placeholder="Type your full name")
    st.info("This test shows one question at a time. After you click Next, you cannot go back.")
    if st.button("Begin test", type="primary", use_container_width=True):
        if not student_name.strip():
            st.warning("Enter your name to begin.")
        else:
            st.session_state[started_key] = True
            st.session_state[index_key] = 0
            st.session_state[answers_key] = {}
            st.session_state[name_key] = student_name.strip()
            st.rerun()
    st.stop()

current_index = st.session_state.get(index_key, 0)
answers: dict[str, int] = st.session_state.get(answers_key, {})
question = questions[current_index]

st.progress((current_index + 1) / len(questions))
st.markdown(f"**Question {current_index + 1} of {len(questions)}**")
render_markdown(question["question_text"])
choice = st.radio(
    "Choose one:",
    options=[-1, *list(range(len(question["options"])))],
    format_func=lambda idx, opts=question["options"]: "Select an answer" if idx == -1 else opts[idx],
    key=f"test_q_{test['id']}_{question['id']}",
    label_visibility="collapsed",
)

button_label = "Submit test" if current_index == len(questions) - 1 else "Next"
if st.button(button_label, type="primary", use_container_width=True):
    if choice == -1:
        st.warning("Choose an answer before continuing.")
    else:
        answers[question["id"]] = choice
        st.session_state[answers_key] = answers
        if current_index == len(questions) - 1:
            result = db.submit_quiz(test["id"], st.session_state[name_key], answers)
            st.session_state[submitted_key] = True
            st.session_state[result_key] = result
            _reset_test_attempt(test["id"])
        else:
            st.session_state[index_key] = current_index + 1
        st.rerun()
