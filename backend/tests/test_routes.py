from unittest.mock import patch

# POST /library/sync

SYNC_RESULT = {
    "status": "ok",
    "started_at": "2024-01-01T00:00:00+00:00",
    "finished_at": "2024-01-01T00:00:01+00:00",
    "playlists_seen": 2,
    "tracks_seen": 10,
}


def test_sync_endpoint_returns_200(client):
    with patch("routes.library.tidal_service.sync", return_value=SYNC_RESULT):
        response = client.post("/library/sync")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_sync_endpoint_returns_sync_result(client):
    with patch("routes.library.tidal_service.sync", return_value=SYNC_RESULT):
        response = client.post("/library/sync")
    data = response.json()
    assert data["playlists_seen"] == 2
    assert data["tracks_seen"] == 10


def test_sync_endpoint_returns_500_on_error(client):
    with patch(
        "routes.library.tidal_service.sync", side_effect=Exception("tidal error")
    ):
        response = client.post("/library/sync")
    assert response.status_code == 500
