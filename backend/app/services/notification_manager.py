from fastapi import WebSocket
from typing import List

class NotificationConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        """Accepts incoming browser websocket upgrade requests."""
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        """Removes disconnected browser connections safely."""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast_alert(self, title: str, status: str, rank: int):
        """Transmits an anomaly event data payload instantly to all active frontend clients."""
        payload = {
            "type": "ANOMALY_ALERT",
            "title": title,
            "status": status,
            "rank": f"{rank}%"
        }
        for connection in self.active_connections:
            try:
                await connection.send_json(payload)
            except Exception:
                pass

notification_manager = NotificationConnectionManager()