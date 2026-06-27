from models import Playlist, Track
from utils.helpers import now_iso


# insert or update tracks
def upsert_tracks(tracks, source, db, playlist_id=None):
    seen_at = now_iso()
    for data in tracks:
        track = db.get(Track, data["id"])

        # no track stored, insert
        if track is None:
            track = Track(
                id=data["id"],
                name=data.get("name"),
                artist=data.get("artist"),
                album=data.get("album"),
                duration=data.get("duration"),
                explicit=data.get("explicit"),
                audio_quality=data.get("audio_quality"),
                isrc=data.get("isrc"),
                available=data.get("available"),
                date_added=data.get("date_added"),
                first_seen_at=seen_at,
                last_seen_at=seen_at,
            )
            db.add(track)

        else:  # track stored, update fields
            for field in (
                "name",
                "artist",
                "album",
                "duration",
                "explicit",
                "audio_quality",
                "isrc",
                "available",
                "date_added",
            ):
                value = data.get(field)
                if value is not None:
                    setattr(track, field, value)
            track.last_seen_at = seen_at

        if source == "favorites":
            track.favorite = True

        # link to playlist if specified
        if playlist_id:
            playlist = db.get(Playlist, playlist_id)
            if playlist and track not in playlist.tracks:
                playlist.tracks.append(track)


# insert or update playlists
def upsert_playlists(playlists, db):
    seen_at = now_iso()
    for data in playlists:
        playlist = db.get(Playlist, data["id"])

        # playlist not stored, insert
        if playlist is None:
            db.add(Playlist(
                id=data["id"],
                name=data["name"],
                first_seen_at=seen_at,
                last_seen_at=seen_at,
            ))

        # playlist stored, update name
        else:
            playlist.name = data["name"]
            playlist.last_seen_at = seen_at
