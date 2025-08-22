from fastapi.testclient import TestClient
from behaviour.src.main import app

client = TestClient(app)

def test_generate_colour():
    response = client.post("/generate-colour")
    assert response.status_code == 200
    data = response.json()
    assert data["colour"] in ["red", "amber", "green"]
    assert "timestamp" in data
