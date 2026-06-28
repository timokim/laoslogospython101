import streamlit as st
import streamlit.components.v1 as components
from pathlib import Path

st.set_page_config(page_title="Asteroid Dodge", page_icon="🚀", layout="centered")

GAME_HTML = (Path(__file__).resolve().parent.parent / "lib" / "asteroid_game.html").read_text()

SPEED_OPTIONS = ["Slow", "Medium", "Fast", "Very Fast"]
SPEED_VALUES = {
    "Slow": 1.8,
    "Medium": 2.8,
    "Fast": 4.2,
    "Very Fast": 6.5,
}
ASTEROID_COUNTS = [4, 8, 14, 28]

st.title("🚀 Asteroid Dodge")
st.caption("Tiny green arrow vs white dots. Pure black void.")

speed = st.selectbox("Asteroid speed", SPEED_OPTIONS)
asteroid_count = st.selectbox("Number of asteroids", ASTEROID_COUNTS, index=1)

col1, col2 = st.columns(2)
with col1:
    st.markdown(
        """
**Controls**
- Click the game area
- **Arrow keys** to move
- Survive as long as you can
"""
    )
with col2:
    st.markdown(
        """
**High scores**
- Saved in your browser per speed + asteroid combo
- Clears if you clear site data
"""
    )

if st.button("Launch game", type="primary", use_container_width=True):
    st.session_state.game_launched = True
    st.session_state.game_speed = speed
    st.session_state.game_count = asteroid_count

if st.session_state.get("game_launched"):
    spd_label = st.session_state.get("game_speed", speed)
    count = st.session_state.get("game_count", asteroid_count)
    settings_key = f"{spd_label}-{count}"
    html = (
        GAME_HTML.replace("__SPD__", str(SPEED_VALUES[spd_label]))
        .replace("__COUNT__", str(count))
        .replace("__SPEED_LABEL__", spd_label)
        .replace("__SETTINGS_KEY__", settings_key)
    )
    components.html(html, height=540, scrolling=False)
else:
    st.info("Set speed and asteroid count, then press **Launch game**.")
