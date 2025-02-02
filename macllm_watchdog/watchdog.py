"""
Webhook watchdog implementation that monitors a webhook endpoint and logs events.
"""

import os
import json
import time
import logging
import requests
from datetime import datetime
from pathlib import Path
from typing import Optional

class WebhookWatchdog:
    """A watchdog that monitors a webhook endpoint and logs events."""
    
    def __init__(self, webhook_url: str, poll_interval: int = 60):
        """
        Initialize the webhook watchdog.
        
        Args:
            webhook_url: The URL to monitor for webhook events
            poll_interval: How often to check for new events in seconds
        """
        self.webhook_url = webhook_url
        self.poll_interval = poll_interval
        
        # Setup logging to user's home directory
        log_dir = Path.home() / "Library/Logs/macllm_watchdog"
        log_dir.mkdir(parents=True, exist_ok=True)
        
        log_file = log_dir / "watchdog.log"
        self.logger = logging.getLogger("macllm_watchdog")
        self.logger.setLevel(logging.INFO)
        
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        
        # File handler
        fh = logging.FileHandler(log_file)
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)
        
        # Console handler
        ch = logging.StreamHandler()
        ch.setFormatter(formatter)
        self.logger.addHandler(ch)
        
        self.logger.info(f"Watchdog initialized. Monitoring {webhook_url}")
        self.logger.info(f"Logs will be written to {log_file}")

    def check_webhook(self) -> Optional[dict]:
        """
        Check the webhook endpoint for new events.
        
        Returns:
            dict: The webhook event data if successful, None otherwise
        """
        try:
            response = requests.get(self.webhook_url, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            self.logger.error(f"Error checking webhook: {str(e)}")
            return None
        except json.JSONDecodeError:
            self.logger.error("Received invalid JSON from webhook")
            return None

    def run(self):
        """Run the watchdog monitoring loop."""
        self.logger.info("Starting webhook monitoring...")
        
        while True:
            event = self.check_webhook()
            if event:
                self.logger.info(f"Received webhook event: {json.dumps(event, indent=2)}")
            time.sleep(self.poll_interval)

def main():
    """Main entry point for the watchdog tool."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Monitor a webhook endpoint for events")
    parser.add_argument("webhook_url", help="URL of the webhook endpoint to monitor")
    parser.add_argument("--interval", type=int, default=60,
                       help="Polling interval in seconds (default: 60)")
    
    args = parser.parse_args()
    
    watchdog = WebhookWatchdog(args.webhook_url, args.interval)
    watchdog.run()

if __name__ == "__main__":
    main()