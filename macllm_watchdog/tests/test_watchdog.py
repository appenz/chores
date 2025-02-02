"""
Tests for the webhook watchdog implementation.
"""

import json
import tempfile
import requests
from pathlib import Path
from unittest import TestCase, mock
from macllm_watchdog.watchdog import WebhookWatchdog

class TestWebhookWatchdog(TestCase):
    """Test cases for WebhookWatchdog class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Mock home directory for logs
        self.temp_dir = tempfile.mkdtemp()
        self.home_patcher = mock.patch('pathlib.Path.home')
        self.mock_home = self.home_patcher.start()
        self.mock_home.return_value = Path(self.temp_dir)
        
        self.webhook_url = "https://example.com/webhook"
        self.watchdog = WebhookWatchdog(self.webhook_url)

    def tearDown(self):
        """Clean up test fixtures."""
        self.home_patcher.stop()

    @mock.patch('requests.get')
    def test_successful_webhook_check(self, mock_get):
        """Test successful webhook check with valid JSON response."""
        expected_data = {"event": "test", "data": "example"}
        mock_response = mock.Mock()
        mock_response.json.return_value = expected_data
        mock_get.return_value = mock_response
        
        result = self.watchdog.check_webhook()
        
        self.assertEqual(result, expected_data)
        mock_get.assert_called_once_with(self.webhook_url, timeout=30)

    @mock.patch('requests.get')
    def test_failed_webhook_check(self, mock_get):
        """Test webhook check with network error."""
        mock_get.side_effect = requests.RequestException("Network error")
        
        result = self.watchdog.check_webhook()
        
        self.assertIsNone(result)
        mock_get.assert_called_once_with(self.webhook_url, timeout=30)

    @mock.patch('requests.get')
    def test_invalid_json_response(self, mock_get):
        """Test webhook check with invalid JSON response."""
        mock_response = mock.Mock()
        mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
        mock_get.return_value = mock_response
        
        result = self.watchdog.check_webhook()
        
        self.assertIsNone(result)
        mock_get.assert_called_once_with(self.webhook_url, timeout=30)

    def test_log_file_creation(self):
        """Test that log file is created in user's directory."""
        expected_log_dir = Path(self.temp_dir) / "Library/Logs/macllm_watchdog"
        expected_log_file = expected_log_dir / "watchdog.log"
        
        self.assertTrue(expected_log_dir.exists())
        self.assertTrue(expected_log_file.exists())
