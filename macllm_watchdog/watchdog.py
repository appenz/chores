"""Webhook watchdog implementation using svix."""

import json
import os
import logging
from pathlib import Path
from typing import Optional

from svix.webhooks import Webhook, WebhookVerificationError

class WebhookWatchdog:
    """Watchdog for monitoring svix webhook events."""
    
    def __init__(self, webhook_secret: str, log_level: int = logging.INFO):
        """Initialize the webhook watchdog.
        
        Args:
            webhook_secret: The svix webhook signing secret
            log_level: Logging level (default: logging.INFO)
        """
        self.webhook = Webhook(webhook_secret)
        self._setup_logging(log_level)

    def _setup_logging(self, log_level: int) -> None:
        """Set up logging to ~/Library/Logs/macLLM/watchdog.log."""
        log_dir = Path.home() / "Library" / "Logs" / "macLLM"
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / "watchdog.log"
        
        self.logger = logging.getLogger("macllm_watchdog")
        self.logger.setLevel(log_level)
        
        # Remove any existing handlers (including console handlers)
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
        
        # Add file handler
        file_handler = logging.FileHandler(log_file)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

    def verify_webhook(self, payload: bytes, headers: dict) -> Optional[dict]:
        """Verify and process a webhook event.
        
        Args:
            payload: Raw webhook payload
            headers: Request headers including svix signature
            
        Returns:
            Parsed webhook payload if valid, None if invalid
        """
        try:
            # Convert header keys to lowercase for consistency
            headers = {k.lower(): v for k, v in headers.items()}
            
            # Verify webhook signature
            self.webhook.verify(payload, headers)
            
            # Parse payload as JSON
            payload_dict = json.loads(payload.decode())
            
            self.logger.info(f"Received valid webhook event: {payload_dict}")
            return payload_dict
            
        except WebhookVerificationError as e:
            self.logger.error(f"Invalid webhook signature: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Error processing webhook: {e}")
            return None
