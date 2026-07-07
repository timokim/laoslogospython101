import streamlit as st

from lib.utils import get_db

LOGOS_IMAGE = "assets/logos_institute.png"

st.title("Logos Institute - Python Summer Course - 2026")

col_text, col_img = st.columns([3, 2])
with col_text:
    st.markdown(
        """
Welcome to the Python Summer Course portal at
**[Logos Institute of Foreign Language](https://logos.edu.la/)**.

Use the sidebar to navigate:

- **Instructor — Quizzes** — create, deploy, and review quiz results
- **Take Quiz** — enter a quiz code and your name
- **Take Midterm** — enter a midterm or final test code
- **Photo Capture** — add your photo (best on a phone)
- **Student Directory** — browse everyone's name and photo
"""
    )
    st.link_button("Visit logos.edu.la", "https://logos.edu.la/", type="primary")

with col_img:
    st.image(LOGOS_IMAGE, caption="Logos Institute", use_container_width=True)

db = get_db()

col1, col2, col3 = st.columns(3)
with col1:
    st.info("**Quizzes**\n\nMultiple choice with code blocks. Deploy a link code for students.")
with col2:
    st.info("**Photo booth**\n\nSnap a photo on your phone and join the directory.")
with col3:
    st.success(f"**Backend:** {db.backend_name}")
