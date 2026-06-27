from __future__ import annotations

import io
import secrets
import string

import streamlit as st
from PIL import Image, ImageOps


def get_instructor_pin() -> str:
    try:
        return st.secrets.get("instructor_pin", "laos2026")
    except Exception:
        return "laos2026"


def require_instructor() -> bool:
    pin = get_instructor_pin()
    if st.session_state.get("instructor_authed"):
        return True

    st.subheader("Instructor access")
    entered = st.text_input("Enter instructor PIN", type="password")
    if st.button("Unlock"):
        if entered == pin:
            st.session_state.instructor_authed = True
            st.rerun()
        else:
            st.error("Incorrect PIN.")
    return False


def generate_quiz_code(length: int = 6) -> str:
    alphabet = string.ascii_uppercase + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


def compress_image(image_bytes: bytes, max_width: int = 800) -> bytes:
    img = Image.open(io.BytesIO(image_bytes))
    img = ImageOps.exif_transpose(img)
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")

    if img.width > max_width:
        ratio = max_width / img.width
        new_size = (max_width, int(img.height * ratio))
        img = img.resize(new_size, Image.Resampling.LANCZOS)

    out = io.BytesIO()
    img.save(out, format="JPEG", quality=85, optimize=True)
    return out.getvalue()


def get_db():
    from lib.database import get_database

    return get_database()


def render_markdown(text: str) -> None:
    st.markdown(text)
