"""Tests for the WebhookWatchdog class."""

import json
import logging
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest
from svix.webhooks import Webhook

from macllm_watchdog import WebhookWatchdog

@pytest.fixture
def mock_home_dir(monkeypatch):
    """Mock home directory for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        monkeypatch.setattr(Path, "home", lambda: Path(temp_dir))
        yield temp_dir

def test_webhook_verification_success(mock_home_dir):
    """Test successful webhook verification."""
    # Create a real svix webhook instance for testing
    secret = "whsec_dGVzdF9zZWNyZXQ="  # base64 encoded "test_secret"
    webhook = Webhook(secret)
    watchdog = WebhookWatchdog(secret)
    
    # Create test payload
    payload = {"type": "test.event", "data": {"foo": "bar"}}
    payload_bytes = json.dumps(payload).encode()
    
    # Generate real svix headers
    timestamp = datetime(2024, 2, 2, tzinfo=timezone.utc)
    msg_id = "msg_test"
    signature = webhook.sign(msg_id, timestamp, payload_bytes)
    headers = {
        "svix-id": msg_id,
        "svix-timestamp": timestamp.isoformat(),
        "svix-signature": signature
    }
    
    # Verify webhook
    result = watchdog.verify_webhook(payload_bytes, headers)
    assert result == payload

def test_webhook_verification_failure(mock_home_dir):
    """Test webhook verification with invalid signature."""
    watchdog = WebhookWatchdog("whsec_dGVzdF9zZWNyZXQ=")
    
    # Invalid headers
    headers = {
        "svix-id": "msg_test",
        "svix-timestamp": "2023-01-01T00:00:00Z",
        "svix-signature": "v1,invalid_signature"
    }
    payload = json.dumps({"type": "test"}).encode()
    
    result = watchdog.verify_webhook(payload, headers)
    assert result is None

def test_logging_setup(mock_home_dir):
    """Test logging setup and file location."""
    watchdog = WebhookWatchdog("whsec_dGVzdF9zZWNyZXQ=")
    
    # Check log file exists in correct location
    log_file = Path(mock_home_dir) / "Library" / "Logs" / "macLLM" / "watchdog.log"
    assert log_file.exists()
    
    # Verify no console handlers
    logger = logging.getLogger("macllm_watchdog")
    assert len(logger.handlers) == 1
    assert isinstance(logger.handlers[0], logging.FileHandler)

def test_logging_content(mock_home_dir):
    """Test log content for webhook events."""
    secret = "whsec_dGVzdF9zZWNyZXQ="  # base64 encoded "test_secret"
    webhook = Webhook(secret)
    watchdog = WebhookWatchdog(secret)
    
    # Create and verify a webhook event
    payload = {"type": "test.event", "data": {"foo": "bar"}}
    payload_bytes = json.dumps(payload).encode()
    timestamp = datetime(2024, 2, 2, tzinfo=timezone.utc)
    msg_id = "msg_test"
    signature = webhook.sign(msg_id, timestamp, payload_bytes)
    headers = {
        "svix-id": msg_id,
        "svix-timestamp": timestamp.isoformat(),
        "svix-signature": signature
    }
    
    watchdog.verify_webhook(payload_bytes, headers)
    
    # Check log file content
    log_file = Path(mock_home_dir) / "Library" / "Logs" / "macLLM" / "watchdog.log"
    log_content = log_file.read_text()
    assert "Received valid webhook event" in log_content
    assert "test.event" in log_content
