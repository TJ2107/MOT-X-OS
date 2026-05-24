from fastapi.testclient import TestClient

from src.motx_os_bridge.api.server_v2 import app

client = TestClient(app)


def test_api_v2_health_returns_healthy():
    response = client.get("/api/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "healthy"
    assert payload["service"] == "MOT-X v2"
    assert "components" in payload


def test_api_v2_config_returns_features():
    response = client.get("/api/config")
    assert response.status_code == 200
    payload = response.json()
    assert payload["name"] == "MOT-X"
    assert "cognitive_emergence" in payload["features"]


def test_api_v2_status_returns_engine_and_agents():
    response = client.get("/api/status")
    assert response.status_code == 200
    payload = response.json()
    assert "engine" in payload
    assert "agents" in payload
    assert "analytics" in payload
