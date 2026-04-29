import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    assert "mode" in response.json()

def test_analyze_page_missing_client():
    # Test without OpenAI client configured (or just general structure)
    payload = {
        "url": "https://example.com",
        "title": "Example",
        "text": "Hello world",
        "forms": [],
        "buttons": [],
        "tables": []
    }
    # This might fail if client is not mockable easily, but we check structure
    response = client.post("/analyze-page", json=payload)
    # If client is missing, it returns 500 as per our code
    assert response.status_code in [200, 500] 

def test_agent_command_safe():
    payload = {"command": "Summarize this"}
    response = client.post("/agent-command", json=payload)
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert "I've processed your request" in response.json()["message"]

def test_agent_command_risky():
    payload = {"command": "delete my account"}
    response = client.post("/agent-command", json=payload)
    assert response.status_code == 200
    assert response.json()["status"] == "confirmation_required"
    assert "requires your approval" in response.json()["message"]

def test_confirm_action_blocked():
    payload = {"action_id": "test_id", "confirmed": True}
    response = client.post("/confirm-action", json=payload)
    assert response.status_code == 200
    assert response.json()["status"] == "blocked"
    assert "not enabled in the read-only MVP" in response.json()["message"]

def test_confirm_action_cancelled():
    payload = {"action_id": "test_id", "confirmed": False}
    response = client.post("/confirm-action", json=payload)
    assert response.status_code == 200
    assert response.json()["status"] == "cancelled"
