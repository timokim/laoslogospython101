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
        # st.Page("pages/2_Take_Quiz.py", title="Take Quiz", icon="✏️"),
        st.Page("pages/7_Take_Midterm.py", title="Take Midterm", icon="🧪"),
        st.Page("pages/3_Photo_Capture.py", title="Photo Capture", icon="📸"),
        st.Page("pages/4_Student_Directory.py", title="Student Directory", icon="👥"),
        st.Page("pages/5_Asteroid_Dodge.py", title="Asteroid Dodge", icon="🚀"),
        st.Page("pages/6_Code_Snippets.py", title="Code Snippets", icon="📋"),
    ]
)
pg.run()
