import json
from pathlib import Path

import streamlit as st

from lib.utils import get_db, render_markdown, require_instructor


def _question_preview(text: str, limit: int = 55) -> str:
    one_line = " ".join(text.split())
    return one_line if len(one_line) <= limit else one_line[: limit - 3] + "..."


def _toggle_question_enabled(
    question_id: str, widget_key: str, manage_key: str | None = None
) -> None:
    if manage_key is not None:
        st.session_state[manage_key] = True
    get_db().set_question_enabled(question_id, st.session_state[widget_key])


st.set_page_config(page_title="Instructor — Quizzes", page_icon="📝", layout="wide")

if not require_instructor():
    st.stop()

db = get_db()
QUIZ_JSON_DIR = Path(__file__).resolve().parent.parent / "data" / "quizzes"

st.title("📝 Instructor — Quizzes")
st.caption(f"Backend: {db.backend_name}")

tab_list, tab_edit, tab_results, tab_import = st.tabs(
    ["My quizzes", "Edit questions", "Results", "Import from code"]
)

with tab_list:
    st.subheader("Prepared quizzes")
    quizzes = db.list_quizzes()

    with st.form("create_quiz", clear_on_submit=True):
        title = st.text_input("New quiz title", placeholder="Python Module 1")
        if st.form_submit_button("Create quiz"):
            if title.strip():
                quiz = db.create_quiz(title.strip())
                st.success(f"Created **{quiz['title']}** with code `{quiz['code']}`")
                st.rerun()
            else:
                st.warning("Enter a title.")

    if not quizzes:
        st.info("No quizzes yet. Create one above or import from JSON.")
    else:
        for quiz in quizzes:
            with st.container(border=True):
                c1, c2, c3 = st.columns([3, 1, 1])
                with c1:
                    status = "🟢 Deployed" if quiz.get("deployed") else "⚪ Draft"
                    total = quiz.get("question_count", 0)
                    active = quiz.get("active_question_count", total)
                    st.markdown(f"**{quiz['title']}** — `{quiz['code']}` — {status}")
                    st.caption(f"{active} of {total} questions active")
                with c2:
                    if quiz.get("deployed"):
                        if st.button("Undeploy", key=f"undep_{quiz['id']}"):
                            db.set_quiz_deployed(quiz["id"], False)
                            st.rerun()
                    else:
                        if st.button("Deploy", key=f"dep_{quiz['id']}"):
                            db.set_quiz_deployed(quiz["id"], True)
                            st.rerun()
                with c3:
                    if st.button("Delete", key=f"del_{quiz['id']}"):
                        db.delete_quiz(quiz["id"])
                        st.rerun()

                if quiz.get("deployed"):
                    st.code(
                        f"Quiz code: {quiz['code']}\n"
                        f"Or open Take Quiz with: ?code={quiz['code']}",
                        language=None,
                    )
                else:
                    questions = db.list_questions(quiz["id"])
                    manage_key = f"manage_open_{quiz['id']}"
                    manage_label = f"Manage questions ({active} active)"

                    if not st.session_state.get(manage_key, False):
                        if st.button(manage_label, key=f"open_manage_{quiz['id']}"):
                            st.session_state[manage_key] = True
                            st.rerun()
                    else:
                        with st.container(border=True):
                            head_col, close_col = st.columns([5, 1])
                            with head_col:
                                st.markdown(f"**{manage_label}**")
                            with close_col:
                                if st.button("Close", key=f"close_manage_{quiz['id']}"):
                                    st.session_state[manage_key] = False
                                    st.rerun()

                            if not questions:
                                st.caption(
                                    "No questions yet. Add them in **Edit questions** or **Import from code**."
                                )
                            else:
                                st.caption(
                                    "Toggle off questions to exclude them when students take the quiz."
                                )
                                for i, q in enumerate(questions, start=1):
                                    preview = _question_preview(q["question_text"])
                                    widget_key = f"qen_{quiz['id']}_{q['id']}"
                                    st.toggle(
                                        f"Q{i}: {preview}",
                                        value=q["enabled"],
                                        key=widget_key,
                                        on_change=_toggle_question_enabled,
                                        args=(q["id"], widget_key, manage_key),
                                    )

with tab_edit:
    quizzes = db.list_quizzes()
    if not quizzes:
        st.info("Create a quiz first.")
    else:
        quiz_options = {f"{q['title']} ({q['code']})": q["id"] for q in quizzes}
        selected = st.selectbox("Select quiz to edit", list(quiz_options.keys()))
        quiz_id = quiz_options[selected]

        with st.form("add_question", clear_on_submit=True):
            st.markdown("Add a question (markdown supported — use triple backticks for code)")
            question_text = st.text_area(
                "Question",
                height=120,
                placeholder="What does this print?\n\n```python\nprint(2 + 2)\n```",
            )
            opt1 = st.text_input("Option A")
            opt2 = st.text_input("Option B")
            opt3 = st.text_input("Option C")
            opt4 = st.text_input("Option D")
            correct = st.selectbox("Correct answer", ["A", "B", "C", "D"])
            if st.form_submit_button("Add question"):
                options = [opt1, opt2, opt3, opt4]
                if not question_text.strip() or any(not o.strip() for o in options):
                    st.warning("Fill in the question and all four options.")
                else:
                    idx = {"A": 0, "B": 1, "C": 2, "D": 3}[correct]
                    db.add_question(quiz_id, question_text.strip(), options, idx)
                    st.success("Question added.")
                    st.rerun()

        st.divider()
        st.subheader("Current questions")
        questions = db.list_questions(quiz_id)
        if not questions:
            st.info("No questions yet.")
        for i, q in enumerate(questions, start=1):
            with st.expander(f"Q{i}: {q['question_text'][:60]}..."):
                render_markdown(q["question_text"])
                for j, opt in enumerate(q["options"]):
                    marker = "✅" if j == q["correct_index"] else "○"
                    st.write(f"{marker} {opt}")
                widget_key = f"qedit_{quiz_id}_{q['id']}"
                st.toggle(
                    "Active for students",
                    value=q["enabled"],
                    key=widget_key,
                    on_change=_toggle_question_enabled,
                    args=(q["id"], widget_key),
                )
                if st.button("Remove question", key=f"rmq_{q['id']}"):
                    db.delete_question(q["id"])
                    st.rerun()

with tab_results:
    quizzes = db.list_quizzes()
    if not quizzes:
        st.info("No quizzes yet.")
    else:
        quiz_options = {f"{q['title']} ({q['code']})": q["id"] for q in quizzes}
        selected = st.selectbox("View results for", list(quiz_options.keys()), key="results_quiz")
        quiz_id = quiz_options[selected]
        submissions = db.list_submissions(quiz_id)

        if not submissions:
            st.info("No submissions yet.")
        else:
            st.metric("Submissions", len(submissions))
            avg = sum(s["score"] for s in submissions) / len(submissions)
            st.metric("Average score", f"{avg:.1f} / {submissions[0]['total']}")

            rows = [
                {
                    "Name": s["student_name"],
                    "Score": f"{s['score']}/{s['total']}",
                    "Percent": f"{100 * s['score'] / s['total']:.0f}%",
                    "Submitted": s.get("submitted_at", ""),
                }
                for s in submissions
            ]
            st.dataframe(rows, use_container_width=True, hide_index=True)

with tab_import:
    st.markdown(
        """
Import quizzes defined as JSON files in `data/quizzes/`. Edit those files in your code editor,
commit to Git, then import here — or upload a JSON file directly.
"""
    )

    json_files = sorted(QUIZ_JSON_DIR.glob("*.json"))
    if json_files:
        st.subheader("From repo files")
        for path in json_files:
            col_a, col_b = st.columns([3, 1])
            with col_a:
                st.write(f"`{path.name}`")
            with col_b:
                if st.button("Import", key=f"imp_{path.name}"):
                    payload = json.loads(path.read_text())
                    quiz = db.import_quiz_json(payload)
                    st.success(f"Imported as **{quiz['title']}** (`{quiz['code']}`)")
                    st.rerun()

    st.subheader("Upload JSON")
    uploaded = st.file_uploader("Quiz JSON file", type=["json"])
    if uploaded:
        payload = json.load(uploaded)
        if st.button("Import uploaded file"):
            quiz = db.import_quiz_json(payload)
            st.success(f"Imported as **{quiz['title']}** (`{quiz['code']}`)")
            st.rerun()

    with st.expander("JSON format reference"):
        st.code(
            """{
  "title": "My Quiz",
  "questions": [
    {
      "question_text": "What does `print(1+1)` output?",
      "options": ["1", "2", "11", "Error"],
      "correct_index": 1
    }
  ]
}""",
            language="json",
        )
