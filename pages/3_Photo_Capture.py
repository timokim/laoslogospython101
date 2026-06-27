import streamlit as st

from lib.utils import get_db

st.set_page_config(page_title="Photo Capture", page_icon="📸", layout="centered")

db = get_db()

st.title("📸 Join the Directory")
st.markdown(
    """
**Computer majors, assemble!** Enter your name and take a photo to appear in the class directory.

Tip: On a phone, use the file picker — it usually opens your camera with better quality than the live preview.
"""
)

name = st.text_input("Your name", placeholder="Your full name")

photo = st.file_uploader(
    "Take or upload a photo",
    type=["jpg", "jpeg", "png", "webp"],
    help="On mobile, tap here to open your camera.",
)

if photo and name.strip():
    st.image(photo, caption="Preview", use_container_width=True)
    if st.button("Save to directory", type="primary", use_container_width=True):
        db.add_student(name, photo.getvalue())
        st.success(f"Welcome to the directory, **{name.strip()}**! 🎉")
        st.balloons()
elif photo and not name.strip():
    st.warning("Please enter your name first.")
elif not photo:
    st.info("Add your name, then tap above to take or choose a photo.")
