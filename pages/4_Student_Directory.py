import streamlit as st

from lib.utils import get_db

st.set_page_config(page_title="Student Directory", page_icon="👥", layout="wide")

db = get_db()

st.title("👥 Computer Major Directory")
st.caption("Everyone who joined via the Photo Capture page.")

students = db.list_students()

if not students:
    st.info("No students yet. Head to **Photo Capture** to be the first!")
    st.stop()

st.metric("Students", len(students))

cols_per_row = 3
for i in range(0, len(students), cols_per_row):
    cols = st.columns(cols_per_row)
    for col, student in zip(cols, students[i : i + cols_per_row]):
        with col:
            with st.container(border=True):
                photo_bytes = db.get_photo_bytes(student["photo_path"])
                if photo_bytes:
                    st.image(photo_bytes, use_container_width=True)
                else:
                    st.warning("Photo unavailable")
                st.markdown(f"**{student['name']}**")
