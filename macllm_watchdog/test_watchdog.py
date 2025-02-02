"""
Tests for the watchdog module.
"""
import pytest
from fastapi.testclient import TestClient
from .watchdog import app

client = TestClient(app)

def test_webhook_handler_success():
    """Test successful webhook event processing."""
    test_event = {"event": "test", "data": {"key": "value"}}
    response = client.post("/webhook", json=test_event)
    assert response.status_code == 200
    assert response.json()["status"] == "success"

def test_webhook_handler_invalid_json():
    """Test handling of invalid JSON payload."""
    response = client.post("/webhook", data="invalid json")
    assert response.status_code == 200  # FastAPI still returns 200 but with error message
    assert response.json()["status"] == "error"