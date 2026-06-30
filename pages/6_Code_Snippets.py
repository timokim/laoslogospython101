from pathlib import Path

import streamlit as st

st.set_page_config(page_title="Code Snippets", page_icon="📋", layout="wide")

THONNY_DIR = Path(__file__).resolve().parent.parent / "data" / "code_snippets"

SNIPPETS = [
    {
        "tab": "🐢 Graphics — Laos Flag",
        "file": "laos_flag_turtle.py",
        "blurb": "Red · blue · red stripes with a white circle in the center.",
        "tip": "Width = 1.5 × height (2:3 ratio). Circle radius = 0.2 × height.",
    },
    {
        "tab": "🐢 Graphics — Fractal",
        "file": "fractal_turtle.py",
        "blurb": "A funky fractal pattern.",
        "tip": "Use the turtle module to draw the fractal.",
    },
    {
        "tab": "🐢 Graphics — Growing Color Spiral",
        "file": "growing_color_spiral.py",
        "blurb": "A growing color spiral.",
        "tip": "Use the turtle module to draw the spiral.",
    },
]

st.title("📋 Code Snippets")
st.markdown(
    "Copy a snippet into **Thonny** and press **Run** (F5). "
    "Files live in `data/thonny/`."
)

tabs = st.tabs([s["tab"] for s in SNIPPETS])

for tab, snippet in zip(tabs, SNIPPETS):
    code = (THONNY_DIR / snippet["file"]).read_text()
    with tab:
        st.subheader(snippet["tab"])
        col_code, col_help = st.columns([3, 2])
        with col_code:
            st.code(code, language="python", line_numbers=True)
        with col_help:
            st.markdown(f"**About:** {snippet['blurb']}")
            st.info(f"**Tip:** {snippet['tip']}")
            st.markdown(f"**File:** `data/thonny/{snippet['file']}`")
