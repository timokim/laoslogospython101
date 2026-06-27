import streamlit as st

st.set_page_config(
    page_title="Logos Institute - Python Summer Course",
    page_icon="🎓",
    layout="wide",
)

pg = st.navigation(
    [
        st.Page("pages/welcome.py", title="Welcome", icon="🏠", default=True),
        st.Page("pages/1_Instructor_Quizzes.py", title="Instructor — Quizzes", icon="📝"),
        st.Page("pages/2_Take_Quiz.py", title="Take Quiz", icon="✏️"),
        st.Page("pages/3_Photo_Capture.py", title="Photo Capture", icon="📸"),
        st.Page("pages/4_Student_Directory.py", title="Student Directory", icon="👥"),
    ]
)
pg.run()
