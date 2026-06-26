import os
import webbrowser
from pathlib import Path

import tidalapi
from fastapi import FastAPI

session_file = os.path.expanduser("~/.tidal-tui/session.json")
session = tidalapi.Session()


def save_current_session():
    try:
        os.makedirs(os.path.dirname(session_file), exist_ok=True)
        session.save_session_to_file(Path(session_file))
    except Exception as e:
        print(f"Failed to save session: {e}")


def authenticate_session():
    if os.path.exists(session_file):
        try:
            if (
                session.load_session_from_file(Path(session_file))
                and session.check_login()
            ):
                print("Stored session found")
                return
            print("No session found")
        except Exception as e:
            print(f"Failed to load session: {e}")

    login, future = session.login_oauth()
    login_url = f"https://{login.verification_uri_complete}"
    print(f"Opening TIDAL login URL: {login_url}")
    webbrowser.open(login_url)
    print(f"If the browser did not open, visit {login_url}")
    future.result()
    save_current_session()


app = FastAPI()
authenticate_session()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
