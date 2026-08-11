"""WebSocket connection manager for real-time events."""

from typing import Dict, List
from fastapi import WebSocket


class ConnectionManager:
    """Manages active WebSocket connections grouped by session code."""

    def __init__(self) -> None:
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, session_code: str, websocket: WebSocket) -> None:
        """Accepts a WebSocket connection and registers it."""
        await websocket.accept()
        if session_code not in self.active_connections:
            self.active_connections[session_code] = []
        self.active_connections[session_code].append(websocket)

    def disconnect(self, session_code: str, websocket: WebSocket) -> None:
        """Removes a WebSocket connection from the registry."""
        if session_code in self.active_connections:
            if websocket in self.active_connections[session_code]:
                self.active_connections[session_code].remove(websocket)
            if not self.active_connections[session_code]:
                del self.active_connections[session_code]

    async def broadcast(self, session_code: str, message: dict) -> None:
        """Broadcasts a JSON message to all clients in a session."""
        if session_code in self.active_connections:
            for connection in self.active_connections[session_code]:
                try:
                    await connection.send_json(message)
                except Exception:
                    # Handled on connection close/disconnect
                    pass


# Shared ConnectionManager instance
manager = ConnectionManager()
