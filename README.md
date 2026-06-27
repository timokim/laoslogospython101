# Laos Mission Portal

Streamlit portal for the Laos Python mission trip: quizzes, student photo directory, and instructor tools.

## Features

- **Quizzes** — instructors create/deploy multiple-choice quizzes (with markdown code blocks); students take them by code
- **Photo directory** — students capture a photo on mobile; everyone appears on the directory page
- **Dual backend** — local SQLite for dev; Supabase for production (Streamlit Community Cloud)

## Quick start (local)

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Optional: copy secrets example (defaults work for local SQLite)
cp .streamlit/secrets.toml.example .streamlit/secrets.toml

streamlit run app.py
```

Open http://localhost:8501

**Default instructor PIN:** `laos2026` (change in `.streamlit/secrets.toml`)

## Try the flow

1. **Instructor — Quizzes** → unlock with PIN → import `sample_python_basics.json` → **Deploy**
2. **Take Quiz** → enter the quiz code and your name
3. **Photo Capture** → add name + photo
4. **Student Directory** → see the gallery

## Supabase (production)

1. Create a Supabase project (pick a region near your users, e.g. Singapore)
2. Run **`supabase/schema.sql`** in the SQL editor (tables + row-level security policies)
3. Create a Storage bucket named `student-photos` (public read recommended for directory)
4. Run the **storage policy** section at the bottom of `schema.sql` again if the bucket was created after step 2
5. Add to `.streamlit/secrets.toml` (or Streamlit Cloud secrets):

```toml
supabase_url = "https://YOUR_PROJECT.supabase.co"
supabase_key = "YOUR_ANON_KEY"
instructor_pin = "your-secret-pin"
```

**RLS error when creating a quiz?** Supabase blocks writes until policies exist. Run the “Row level security” section at the bottom of `supabase/schema.sql` in the SQL editor. Or use the `service_role` key instead of `anon` in Streamlit secrets (server-side only).

## Deploy to Streamlit Community Cloud

1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io) → **New app**
3. Point at `app.py`, paste secrets in **Advanced settings**
4. Share the `.streamlit.app` URL with students

## Quiz JSON format

Edit files in `data/quizzes/` or upload JSON from the instructor page:

```json
{
  "title": "My Quiz",
  "questions": [
    {
      "question_text": "What does this print?\n\n```python\nprint(2+2)\n```",
      "options": ["3", "4", "22", "Error"],
      "correct_index": 1
    }
  ]
}
```

## Project layout

```
app.py                      # Home
pages/
  1_Instructor_Quizzes.py   # Create, deploy, results
  2_Take_Quiz.py            # Student quiz
  3_Photo_Capture.py        # Mobile-friendly photo upload
  4_Student_Directory.py    # Photo gallery
lib/database.py             # SQLite + Supabase backends
data/quizzes/               # Quiz definitions (edit in code)
supabase/schema.sql         # Production DB schema
```
