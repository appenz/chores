"""
Watchdog implementation for monitoring webhooks.
"""
from typing import Dict, Any
from fastapi import FastAPI, Request
import uvicorn
import logging
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI()

@app.post("/webhook")
async def webhook_handler(request: Request) -> Dict[str, str]:
    """
    Handle incoming webhook events and print them.
    
    Args:
        request: The incoming webhook request
        
    Returns:
        Dict containing status message
    """
    try:
        body = await request.json()
        logger.info("Received webhook event:")
        logger.info(json.dumps(body, indent=2))
        return {"status": "success", "message": "Event received and logged"}
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        return {"status": "error", "message": str(e)}

def start_watchdog(host: str = "0.0.0.0", port: int = 8000) -> None:
    """
    Start the watchdog server.
    
    Args:
        host: Host to bind the server to
        port: Port to listen on
    """
    logger.info(f"Starting watchdog server on {host}:{port}")
    uvicorn.run(app, host=host, port=port)

if __name__ == "__main__":
    start_watchdog()