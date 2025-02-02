# macllm_watchdog

A simple watchdog tool that monitors a webhook endpoint and logs events.

## Features

- Monitors a webhook endpoint by polling at configurable intervals
- Logs events to both console and file
- Log files are stored in the user's directory at `~/Library/Logs/macllm_watchdog/watchdog.log`
- Handles network errors and invalid responses gracefully

## Usage

You can run the watchdog tool directly from the command line:

```bash
python -m macllm_watchdog.watchdog https://your-webhook-url --interval 60
```

Or use it in your Python code:

```python
from macllm_watchdog import WebhookWatchdog

# Create and start the watchdog
watchdog = WebhookWatchdog("https://your-webhook-url", poll_interval=60)
watchdog.run()
```

## Configuration

- `webhook_url`: The URL to monitor for webhook events
- `poll_interval`: How often to check for new events (in seconds, default: 60)

## Logs

Logs are written to:
- Console (stdout)
- `~/Library/Logs/macllm_watchdog/watchdog.log`