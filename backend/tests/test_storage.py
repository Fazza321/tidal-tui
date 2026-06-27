from models import Playlist, Track
from services.storage import upsert_playlists, upsert_tracks

TRACK = {
    "id": 1,
    "name": "test track",
    "artist": "test artist",
    "album": "test album",
    "duration": 200,
    "explicit": False,
    "audio_quality": "LOSSLESS",
    "isrc": "TEST123",
    "available": True,
    "date_added": "2024-01-01",
}

PLAYLIST = {"id": "pl1", "name": "my playlist"}


# upsert_tracks


def test_upsert_tracks_inserts_new_track(db):
    upsert_tracks([TRACK], "playlist", db)
    db.commit()
    track = db.get(Track, 1)
    assert track is not None
    assert track.name == "test track"
    assert track.artist == "test artist"


def test_upsert_tracks_updates_existing_track(db):
    upsert_tracks([TRACK], "playlist", db)
    db.commit()
    upsert_tracks([{**TRACK, "name": "updated name"}], "playlist", db)
    db.commit()
    assert db.get(Track, 1).name == "updated name"


def test_upsert_tracks_does_not_overwrite_first_seen_at(db):
    # first_seen_at is set on insert and never updated
    upsert_tracks([TRACK], "playlist", db)
    db.commit()
    first_seen = db.get(Track, 1).first_seen_at
    upsert_tracks([TRACK], "playlist", db)
    db.commit()
    assert db.get(Track, 1).first_seen_at == first_seen


def test_upsert_tracks_updates_last_seen_at(db):
    upsert_tracks([TRACK], "playlist", db)
    db.commit()
    first_last_seen = db.get(Track, 1).last_seen_at
    upsert_tracks([TRACK], "playlist", db)
    db.commit()
    assert db.get(Track, 1).last_seen_at >= first_last_seen


def test_upsert_tracks_marks_favourite(db):
    upsert_tracks([TRACK], "favorites", db)
    db.commit()
    assert db.get(Track, 1).favorite is True


def test_upsert_tracks_does_not_mark_favourite_for_playlist_source(db):
    upsert_tracks([TRACK], "playlist", db)
    db.commit()
    assert not db.get(Track, 1).favorite


def test_upsert_tracks_links_to_playlist(db):
    upsert_playlists([PLAYLIST], db)
    db.commit()
    upsert_tracks([TRACK], "playlist", db, playlist_id="pl1")
    db.commit()
    playlist = db.get(Playlist, "pl1")
    assert len(playlist.tracks) == 1
    assert playlist.tracks[0].id == 1


def test_upsert_tracks_does_not_duplicate_playlist_link(db):
    # upserting the same track twice should'nt create two junction rows
    upsert_playlists([PLAYLIST], db)
    db.commit()
    upsert_tracks([TRACK], "playlist", db, playlist_id="pl1")
    db.commit()
    upsert_tracks([TRACK], "playlist", db, playlist_id="pl1")
    db.commit()
    assert len(db.get(Playlist, "pl1").tracks) == 1


# upsert_playlists


def test_upsert_playlists_inserts_new_playlist(db):
    upsert_playlists([PLAYLIST], db)
    db.commit()
    playlist = db.get(Playlist, "pl1")
    assert playlist is not None
    assert playlist.name == "my playlist"


def test_upsert_playlists_updates_name(db):
    upsert_playlists([PLAYLIST], db)
    db.commit()
    upsert_playlists([{**PLAYLIST, "name": "renamed"}], db)
    db.commit()
    assert db.get(Playlist, "pl1").name == "renamed"


def test_upsert_playlists_does_not_overwrite_first_seen_at(db):
    # first_seen_at is set on insert and never updated
    upsert_playlists([PLAYLIST], db)
    db.commit()
    first_seen = db.get(Playlist, "pl1").first_seen_at
    upsert_playlists([PLAYLIST], db)
    db.commit()
    assert db.get(Playlist, "pl1").first_seen_at == first_seen
