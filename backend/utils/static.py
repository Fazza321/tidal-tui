import os

session_file = os.path.expanduser(
    "~/.tidal-tui/session.json"
)  # location of session cookies
sync_interval_seconds = int(
    os.environ.get("TIDAL_TUI_SYNC_INTERVAL_SECONDS", "3600")
)  # sync interval
_db_path = os.path.expanduser("~/.tidal-tui/library.db")  # location of db
os.makedirs(os.path.dirname(_db_path), exist_ok=True)  # ensure db path exists
DATABASE_URL = f"sqlite:///{_db_path}"  # define database url
