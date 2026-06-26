import webbrowser

import tidalapi
from fastapi import FastAPI

session = tidalapi.Session()


def authenticate_session():
    login, future = session.login_oauth()
    login_url = f"https://{login.verification_uri_complete}"
    print(f"Opening TIDAL login URL: {login_url}")
    webbrowser.open(login_url)
    print(f"If the browser did not open, visit {login_url}")
    future.result()


app = FastAPI()
authenticate_session()
