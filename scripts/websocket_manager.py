from typing import Dict, Set
from fastapi import WebSocket, WebSocketDisconnect
import json
import asyncio
from utils.logging import StructuredLogger

logger = StructuredLogger(__name__)

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, Set[WebSocket]] = {}
        self.user_subscriptions: Dict[int, Set[str]] = {}
    
    async def connect(self, websocket: WebSocket, user_id: int):
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
            self.user_subscriptions[user_id] = set()
        self.active_connections[user_id].add(websocket)
        logger.logger.info(f"User {user_id} connected via WebSocket")
    
    def disconnect(self, websocket: WebSocket, user_id: int):
        if user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
                del self.user_subscriptions[user_id]
        logger.logger.info(f"User {user_id} disconnected from WebSocket")
    
    async def subscribe_to_market(self, user_id: int, market: str):
        if user_id in self.user_subscriptions:
            self.user_subscriptions[user_id].add(market)
    
    async def unsubscribe_from_market(self, user_id: int, market: str):
        if user_id in self.user_subscriptions:
            self.user_subscriptions[user_id].discard(market)
    
    async def send_trade_update(self, user_id: int, trade_data: dict):
        if user_id in self.active_connections:
            message = json.dumps({"type": "trade_update", "data": trade_data})
            disconnected = set()
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_text(message)
                except:
                    disconnected.add(connection)
            # Clean up disconnected sockets
            for conn in disconnected:
                self.active_connections[user_id].discard(conn)
    
    async def broadcast_market_update(self, market: str, data: dict):
        message = json.dumps({"type": "market_update", "market": market, "data": data})
        for user_id, subscriptions in self.user_subscriptions.items():
            if market in subscriptions and user_id in self.active_connections:
                for connection in self.active_connections[user_id]:
                    try:
                        await connection.send_text(message)
                    except:
                        pass

manager = ConnectionManager()
