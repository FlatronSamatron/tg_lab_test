from fastapi import WebSocket

from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[int, list[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, expedition_id: int):
        await websocket.accept()
        if expedition_id not in self.active_connections:
            self.active_connections[expedition_id] = []
        self.active_connections[expedition_id].append(websocket)

    def disconnect(self, websocket: WebSocket, expedition_id: int):
        if expedition_id in self.active_connections:
            self.active_connections[expedition_id].remove(websocket)

    async def broadcast(self, message: dict, expedition_id: int):
        if expedition_id in self.active_connections:
            for connection in self.active_connections[expedition_id]:
                await connection.send_json(message)

manager = ConnectionManager()