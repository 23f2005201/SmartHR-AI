from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.services.notification_manager import notification_manager

router = APIRouter()

@router.websocket("/stream")
async def websocket_endpoint(websocket: WebSocket):
    """Establishes an active persistent notification payload pipeline for the dashboard interface."""
    await notification_manager.connect(websocket)
    try:
        while True:
            # Keep the channel open and catch heartbeat pings
            await websocket.receive_text()
    except WebSocketDisconnect:
        notification_manager.disconnect(websocket)