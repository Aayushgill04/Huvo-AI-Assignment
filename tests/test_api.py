"""Integration tests for FastAPI REST API endpoints."""

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["project"] == "Northstar One"

def test_chat_endpoint_discovery():
    response = client.post("/api/chat", json={
        "message": "Hi, what configurations do you have in Northstar One?"
    })
    assert response.status_code == 200
    data = response.json()
    assert "reply" in data
    assert len(data["reply"]) > 0
    assert "session_id" in data
    assert "live_analytics" in data

def test_chat_scenarios_endpoint():
    response = client.get("/api/scenarios")
    assert response.status_code == 200
    data = response.json()
    assert "scenarios" in data
    assert len(data["scenarios"]) >= 7

def test_end_conversation_and_analytics_endpoint():
    # Start session
    chat_res = client.post("/api/chat", json={
        "session_id": "api_test_session_123",
        "message": "I want to buy a 2 BHK in Northstar One. What is the starting price?"
    })
    assert chat_res.status_code == 200
    
    # End conversation
    end_res = client.post("/api/chat/end", json={
        "session_id": "api_test_session_123"
    })
    assert end_res.status_code == 200
    end_data = end_res.json()
    assert end_data["session_id"] == "api_test_session_123"
    assert "analytics" in end_data
    assert end_data["analytics"]["configuration_interest"] == "2 BHK"

def test_simulate_failure_toggle():
    toggle_res = client.post("/api/chat/simulate-failure", json={
        "session_id": "failure_test_session",
        "simulate_failure": True
    })
    assert toggle_res.status_code == 200
    assert toggle_res.json()["simulate_booking_failure"] is True
