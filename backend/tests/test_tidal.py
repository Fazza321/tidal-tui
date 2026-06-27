from unittest.mock import MagicMock, patch

from services.tidal import _paged, _paged_one_at_a_time, _serialise, tidal_service


def make_mock_track(id=1, name="song", artist="artist", album="album"):
    track = MagicMock()
    track.id = id
    track.name = name
    track.artist.name = artist
    track.album.name = album
    track.duration = 200
    track.explicit = False
    track.audio_quality = "LOSSLESS"
    track.isrc = "TEST123"
    track.available = True
    track.date_added = "2024-01-01"
    return track


def make_mock_playlist(id="pl1", name="playlist"):
    playlist = MagicMock()
    playlist.id = id
    playlist.name = name
    return playlist


# _serialise


def test_serialise_extracts_all_fields():
    result = _serialise(make_mock_track())
    assert result["id"] == 1
    assert result["name"] == "song"
    assert result["artist"] == "artist"
    assert result["album"] == "album"
    assert result["duration"] == 200
    assert result["explicit"] is False
    assert result["isrc"] == "TEST123"
    assert result["available"] is True


def test_serialise_handles_none_artist():
    track = make_mock_track()
    track.artist = None
    assert _serialise(track)["artist"] == ""


def test_serialise_handles_none_album():
    track = make_mock_track()
    track.album = None
    assert _serialise(track)["album"] == ""


def test_serialise_casts_id_to_int():
    track = make_mock_track()
    track.id = "42"
    assert _serialise(track)["id"] == 42


# _paged


def test_paged_returns_single_page():
    fetch = MagicMock(return_value=["a", "b"])
    assert _paged(fetch) == ["a", "b"]
    fetch.assert_called_once()


def test_paged_fetches_multiple_pages():
    # first page is full (100 items), second page is partial — should fetch both
    def fetch(limit, offset):
        return list(range(100)) if offset == 0 else ["last"]

    result = _paged(fetch)
    assert len(result) == 101


def test_paged_returns_empty_on_no_results():
    fetch = MagicMock(return_value=[])
    assert _paged(fetch) == []


def test_paged_skips_bad_track_and_continues():
    # simulates one unparseable track at position 1 in a 3-track playlist
    def fetch(limit, offset):
        if limit == 1 and offset == 1:
            raise TypeError("null artist")
        if limit == 1:
            return [f"track_{offset}"] if offset < 3 else []
        raise TypeError("bulk fetch fails")

    result = _paged(fetch, page_size=3)
    assert "track_0" in result
    assert "track_2" in result
    assert len(result) == 2


def test_paged_continues_past_bad_page_to_next():
    # 150 tracks: bulk fetch of first 100 fails due to bad track at position 5
    # one-at-a-time fallback should check all 100 positions, then continue to next page
    def fetch(limit, offset):
        if limit == 100 and offset == 0:
            raise TypeError("bad track in first page")
        if limit == 1 and offset == 5:
            raise TypeError("bad track")
        if limit == 1 and offset < 100:
            return [f"t{offset}"]
        if limit == 100 and offset == 100:
            return ["next_page_track"]
        return []

    result = _paged(fetch)
    assert "next_page_track" in result
    assert "t0" in result
    assert len(result) == 100  # 99 from first batch (pos 5 skipped) + 1 from second


# _paged_one_at_a_time

def test_paged_one_at_a_time_returns_all_good_tracks():
    def fetch(limit, offset):
        return [f"t{offset}"]

    items, end = _paged_one_at_a_time(fetch, start=0, count=3)
    assert items == ["t0", "t1", "t2"]
    assert end is False


def test_paged_one_at_a_time_skips_bad_tracks():
    def fetch(limit, offset):
        if offset == 1:
            raise TypeError
        return [f"t{offset}"]

    items, end = _paged_one_at_a_time(fetch, start=0, count=3)
    assert items == ["t0", "t2"]


def test_paged_one_at_a_time_stops_at_empty():
    def fetch(limit, offset):
        return [f"t{offset}"] if offset < 2 else []

    items, end = _paged_one_at_a_time(fetch, start=0, count=5)
    assert items == ["t0", "t1"]
    assert end is True


# sync


def test_sync_skips_when_not_logged_in():
    with patch.object(tidal_service.session, "check_login", return_value=False):
        result = tidal_service.sync()
    assert result["status"] == "skipped"


def test_sync_returns_ok():
    with patch.object(
        tidal_service.session, "check_login", return_value=True
    ), patch.object(
        tidal_service, "_get_playlists", return_value=[make_mock_playlist()]
    ), patch.object(
        tidal_service, "_get_playlist_tracks", return_value=[]
    ), patch(
        "services.tidal._paged", return_value=[]
    ), patch(
        "services.tidal.upsert_playlists"
    ), patch(
        "services.tidal.upsert_tracks"
    ), patch(
        "services.tidal.SessionLocal"
    ):
        result = tidal_service.sync()
    assert result["status"] == "ok"


def test_sync_reports_playlist_count():
    playlists = [make_mock_playlist("pl1"), make_mock_playlist("pl2")]
    with patch.object(
        tidal_service.session, "check_login", return_value=True
    ), patch.object(
        tidal_service, "_get_playlists", return_value=playlists
    ), patch.object(
        tidal_service, "_get_playlist_tracks", return_value=[]
    ), patch(
        "services.tidal._paged", return_value=[]
    ), patch(
        "services.tidal.upsert_playlists"
    ), patch(
        "services.tidal.upsert_tracks"
    ), patch(
        "services.tidal.SessionLocal"
    ):
        result = tidal_service.sync()
    assert result["playlists_seen"] == 2


def test_sync_counts_playlist_tracks():
    tracks = [make_mock_track(i) for i in range(3)]
    with patch.object(
        tidal_service.session, "check_login", return_value=True
    ), patch.object(
        tidal_service, "_get_playlists", return_value=[make_mock_playlist()]
    ), patch.object(
        tidal_service, "_get_playlist_tracks", return_value=tracks
    ), patch(
        "services.tidal._paged", return_value=[]
    ), patch(
        "services.tidal.upsert_playlists"
    ), patch(
        "services.tidal.upsert_tracks"
    ), patch(
        "services.tidal.SessionLocal"
    ):
        result = tidal_service.sync()
    assert result["tracks_seen"] == 3


def test_sync_counts_collection_tracks():
    collection = [make_mock_track(i) for i in range(5)]
    with patch.object(
        tidal_service.session, "check_login", return_value=True
    ), patch.object(tidal_service, "_get_playlists", return_value=[]), patch(
        "services.tidal._paged", return_value=collection
    ), patch(
        "services.tidal.upsert_playlists"
    ), patch(
        "services.tidal.upsert_tracks"
    ), patch(
        "services.tidal.SessionLocal"
    ):
        result = tidal_service.sync()
    assert result["tracks_seen"] == 5
