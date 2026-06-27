import streamlit as st

from lib.utils import get_db

st.set_page_config(
    page_title="Laos Mission Portal",
    page_icon="🇱🇦",
    layout="wide",
)

db = get_db()

st.title("🇱🇦 Laos Mission Portal")
st.markdown(
    """
Welcome! This portal supports our Python teaching mission trip.

Use the sidebar to navigate:

- **Instructor — Quizzes** — create, deploy, and review quiz results
- **Take Quiz** — students enter a quiz code and their name
- **Photo Capture** — students add their photo (best on a phone)
- **Student Directory** — browse everyone's name and photo
"""
)

col1, col2, col3 = st.columns(3)
with col1:
    st.info("**Quizzes**\n\nMultiple choice with code blocks. Deploy a link code for students.")
with col2:
    st.info("**Photo booth**\n\nSnap a photo on your phone and join the directory.")
with col3:
    st.success(f"**Backend:** {db.backend_name}")

st.divider()
st.caption(
    "Local dev uses SQLite automatically. Add Supabase credentials to `.streamlit/secrets.toml` for production."
)
