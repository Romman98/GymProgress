
# Gym Tracker (Flask, no CSS)

Simple multi-user gym progress tracker with user groups.

## Features
- Register, login, logout
- Add progress entries (exercise, weight, reps, notes)
- Create/join/leave groups
- View your recent progress
- View recent progress of all members in a group

## Quickstart

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Open http://127.0.0.1:5000

## Notes
- Uses SQLite (`gym.db`) created automatically on first run.
- Default secret key is hardcoded for demo; change `SECRET_KEY` in `app.py` for production.
