import os
import webbrowser
from pathlib import Path

import tidalapi
from services.storage import upsert_playlists, upsert_tracks
from utils.database import SessionLocal
from utils.helpers import now_iso
from utils.static import session_file


# converts track object into dict
def _serialise(track):
    artist = getattr(track, "artist", None)
    album = getattr(track, "album", None)
    return {
        "id": int(track.id),
        "name": track.name,
        "artist": getattr(artist, "name", "") if artist else "",
        "album": getattr(album, "name", "") if album else "",
        "duration": getattr(track, "duration", None),
        "explicit": getattr(track, "explicit", None),
        "audio_quality": str(getattr(track, "audio_quality", "") or ""),
        "isrc": getattr(track, "isrc", None),
        "available": getattr(track, "available", None),
        "date_added": str(getattr(track, "date_added", "") or ""),
    }


# gets all pages from endpoint
def _paged(fetch_page, page_size=100):
    items, offset = [], 0

    # continually fetch pages until reaching a non-full one, i.e. the end
    while True:
        try:
            page = fetch_page(page_size, offset)
            end = len(page) < page_size
        except TypeError:
            # track failed to parse
            page, end = _paged_one_at_a_time(fetch_page, offset, page_size)

        if not page:
            break
        items.extend(page)
        if end:
            break
        offset += page_size
    return items


# used when a page contains broken track
def _paged_one_at_a_time(fetch_page, start, count):
    items = []
    for i in range(count):
        try:
            result = fetch_page(1, start + i)
            if not result:
                return items, True
            items.extend(result)
        except TypeError:
            pass  # skip track
    return items, False


class TidalService:
    def __init__(self):
        self.session = tidalapi.Session()
        self._authenticate()

    # gets playlists and collection from tidal
    # writes to the database
    def sync(self):
        if not self.session.check_login():  # ensure logged in
            return {"status": "skipped", "reason": "Invalid TIDAL session"}

        started_at = now_iso()
        playlists = self._get_playlists()

        with SessionLocal() as db:
            upsert_playlists([{"id": str(p.id), "name": p.name} for p in playlists], db)

            track_count = 0
            for playlist in playlists:
                tracks = self._get_playlist_tracks(playlist)
                upsert_tracks(
                    [_serialise(t) for t in tracks],
                    "playlist",
                    db,
                    playlist_id=str(playlist.id),
                )
                track_count += len(tracks)

            collection = _paged(
                lambda limit, offset: self.session.user.favorites.tracks(
                    limit=limit, offset=offset
                )
            )
            upsert_tracks([_serialise(t) for t in collection], "favorites", db)
            track_count += len(collection)

            db.commit()

        return {
            "status": "ok",
            "started_at": started_at,
            "finished_at": now_iso(),
            "playlists_seen": len(playlists),
            "tracks_seen": track_count,
        }

    # get all playlist names
    def _get_playlists(self):
        try:
            return _paged(
                lambda limit, offset: self.session.user.playlists(
                    limit=limit, offset=offset
                )
            )
        except TypeError:
            return self.session.user.playlists()

    # get all tracks in a playlist
    def _get_playlist_tracks(self, playlist):
        return _paged(lambda limit, offset: playlist.tracks(limit=limit, offset=offset))

    # save login session cookies to file
    def _save_session(self):
        try:
            os.makedirs(os.path.dirname(session_file), exist_ok=True)
            self.session.save_session_to_file(Path(session_file))
        except Exception as e:
            print(f"Failed to save session: {e}")

    # load saved session or prompt for login
    def _authenticate(self):
        if os.environ.get("TIDAL_TUI_SKIP_AUTH") == "1":
            return

        if os.path.exists(session_file):
            try:
                if (
                    self.session.load_session_from_file(Path(session_file))
                    and self.session.check_login()
                ):
                    print("Stored session found")
                    return
                print("Stored session invalid, re-authenticating")
            except Exception as e:
                print(f"Failed to load session: {e}")

        login, future = self.session.login_oauth()
        url = f"https://{login.verification_uri_complete}"
        webbrowser.open(url)
        print(f"Login at: {url}")
        future.result()
        self._save_session()


tidal_service = TidalService()
