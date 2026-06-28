# Asteroid Dodge (Pygame)

Standalone version of the Streamlit mini-game. Pure black background, green triangle ship, white dot asteroids.

## Run

```bash
cd asteroid_dodge_pygame
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

> **Note:** Run `python main.py`, not `pygame main.py`. Pygame is a library imported by the script.

## Controls (menu)

| Key | Action |
|---|---|
| ↑ ↓ | Select Speed or Asteroids row |
| ← → | Change value (Slow/Med/Fast/Very Fast or 4/8/14/28) |
| Enter / Space | Start |
| Arrow keys / WASD | Move ship (in game) |
| R | Back to menu (after game over) |
| ESC | Menu or quit |

## Settings

**Speed:** Slow · Medium · Fast · Very Fast

**Asteroids (pygame):** 4 · 8 · 14 · 28

**Asteroids (web):** slider 1–40

Score = seconds survived.
