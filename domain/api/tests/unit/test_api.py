from datetime import datetime

from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock

from domain.api.src.main import app

client = TestClient(app)

TS = datetime(2026, 7, 7, 12, 0, 0)


def _row(colour="green", ts=TS):
    return {"colour": colour, "created_at": ts}


@patch("domain.api.src.db.create_colour", new_callable=AsyncMock)
def test_generate_colour_alias(mock_create):
    mock_create.return_value = _row()
    response = client.post("/generate-colour")
    assert response.status_code == 200
    data = response.json()
    assert data["colour"] in ["red", "amber", "green"]
    assert "timestamp" in data
    mock_create.assert_awaited_once()


@patch("domain.api.src.db.create_colour", new_callable=AsyncMock)
def test_create_colour(mock_create):
    mock_create.return_value = _row()
    response = client.post("/colours")
    assert response.status_code == 200
    assert response.json()["colour"] in ["red", "amber", "green"]
    mock_create.assert_awaited_once()


@patch("domain.api.src.db.latest", new_callable=AsyncMock)
def test_latest(mock_latest):
    mock_latest.return_value = _row("amber")
    resp = client.get("/colours/latest")
    assert resp.status_code == 200
    assert resp.json()["colour"] == "amber"


@patch("domain.api.src.db.latest", new_callable=AsyncMock)
def test_latest_empty_404(mock_latest):
    mock_latest.return_value = None
    resp = client.get("/colours/latest")
    assert resp.status_code == 404


@patch("domain.api.src.db.recent", new_callable=AsyncMock)
def test_history(mock_recent):
    mock_recent.return_value = [_row("red"), _row("green")]
    resp = client.get("/colours?limit=5")
    assert resp.status_code == 200
    body = resp.json()
    assert isinstance(body, list)
    assert [r["colour"] for r in body] == ["red", "green"]
