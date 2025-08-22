from fastapi.testclient import TestClient

import pytest
from unittest.mock import patch, AsyncMock
from behaviour.src.main import app

client = TestClient(app)


@patch("behaviour.src.main.publish_cloudevent", new_callable=AsyncMock)
def test_generate_colour(mock_publish):
    response = client.post("/generate-colour")
    assert response.status_code == 200
    data = response.json()
    assert data["colour"] in ["red", "amber", "green"]
    assert "timestamp" in data
    mock_publish.assert_awaited_once()
