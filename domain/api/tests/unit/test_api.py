from fastapi.testclient import TestClient

import pytest
from unittest.mock import patch, AsyncMock
from domain.api.src.main import app

client = TestClient(app)


@patch("domain.api.src.main.publish_cloudevent", new_callable=AsyncMock)
def test_generate_colour_alias(mock_publish):
    response = client.post("/generate-colour")
    assert response.status_code == 200
    data = response.json()
    assert data["colour"] in ["red", "amber", "green"]
    assert "timestamp" in data
    mock_publish.assert_awaited_once()


@patch("domain.api.src.main.publish_cloudevent", new_callable=AsyncMock)
def test_create_colour(mock_publish):
    response = client.post("/colours")
    assert response.status_code == 200
    assert response.json()["colour"] in ["red", "amber", "green"]
    mock_publish.assert_awaited_once()


@patch("domain.api.src.main.publish_cloudevent", new_callable=AsyncMock)
def test_latest_and_history(mock_publish):
    created = client.post("/colours").json()

    latest = client.get("/colours/latest")
    assert latest.status_code == 200
    assert latest.json() == created

    history = client.get("/colours?limit=5")
    assert history.status_code == 200
    body = history.json()
    assert isinstance(body, list)
    assert len(body) <= 5
    # Most recent first
    assert body[0] == created
