from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from datetime import datetime, timedelta
import asyncio
import json
import random
import time

app = FastAPI(title="AstraTrade Backend API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class LeaderboardEntry(BaseModel):
    user_id: int
    username: str
    xp: int
    level: int

class CandleData(BaseModel):
    timestamp: int
    open: float
    high: float
    low: float
    close: float
    volume: float

class TickerData(BaseModel):
    symbol: str
    price: float
    change_24h: float
    change_percent_24h: float
    volume_24h: float
    high_24h: float
    low_24h: float

# Mock data for testing
MOCK_USERS = [
    {"user_id": 1, "username": "CryptoTrader", "xp": 2500, "level": 25},
    {"user_id": 2, "username": "DeFiMaster", "xp": 2200, "level": 22},
    {"user_id": 3, "username": "StellarPilot", "xp": 1800, "level": 18},
    {"user_id": 4, "username": "CosmicVoyager", "xp": 1500, "level": 15},
    {"user_id": 5, "username": "QuantumTrader", "xp": 1200, "level": 12},
]

# Mock trading pairs with realistic crypto prices
TRADING_PAIRS = {
    "BTCUSD": {"base_price": 43250.0, "name": "Bitcoin"},
    "ETHUSD": {"base_price": 2580.0, "name": "Ethereum"},
    "SOLUSD": {"base_price": 98.5, "name": "Solana"},
    "ADAUSD": {"base_price": 0.485, "name": "Cardano"},
    "MATICUSD": {"base_price": 0.952, "name": "Polygon"},
    "LINKUSD": {"base_price": 14.75, "name": "Chainlink"},
}

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                # Remove stale connections
                self.active_connections.remove(connection)

manager = ConnectionManager()

def generate_realistic_candle_data(symbol: str, intervals: int = 100) -> List[CandleData]:
    """Generate realistic candlestick data for a trading pair"""
    if symbol not in TRADING_PAIRS:
        symbol = "BTCUSD"  # Default fallback
    
    base_price = TRADING_PAIRS[symbol]["base_price"]
    candles = []
    current_time = int(time.time()) - (intervals * 60)  # 1-minute candles
    current_price = base_price
    
    for i in range(intervals):
        # Generate realistic price movement
        volatility = 0.002  # 0.2% volatility per minute
        price_change = random.uniform(-volatility, volatility)
        
        open_price = current_price
        close_price = open_price * (1 + price_change)
        
        # High and low with some randomness
        high_price = max(open_price, close_price) * (1 + random.uniform(0, volatility/2))
        low_price = min(open_price, close_price) * (1 - random.uniform(0, volatility/2))
        
        # Random volume
        volume = random.uniform(100, 1000)
        
        candles.append(CandleData(
            timestamp=(current_time + i * 60) * 1000,  # Convert to milliseconds
            open=round(open_price, 2),
            high=round(high_price, 2),
            low=round(low_price, 2),
            close=round(close_price, 2),
            volume=round(volume, 2)
        ))
        
        current_price = close_price
    
    return candles

def generate_current_ticker(symbol: str) -> TickerData:
    """Generate current ticker data for a symbol"""
    if symbol not in TRADING_PAIRS:
        symbol = "BTCUSD"
    
    base_price = TRADING_PAIRS[symbol]["base_price"]
    # Add some random movement
    current_price = base_price * (1 + random.uniform(-0.05, 0.05))
    change_24h = random.uniform(-1000, 1000)
    change_percent = (change_24h / current_price) * 100
    
    return TickerData(
        symbol=symbol,
        price=round(current_price, 2),
        change_24h=round(change_24h, 2),
        change_percent_24h=round(change_percent, 2),
        volume_24h=round(random.uniform(100000, 500000), 2),
        high_24h=round(current_price * 1.08, 2),
        low_24h=round(current_price * 0.92, 2)
    )

async def price_feed_generator():
    """Generate continuous price updates for WebSocket"""
    while True:
        for symbol in TRADING_PAIRS.keys():
            ticker = generate_current_ticker(symbol)
            message = {
                "type": "ticker",
                "data": ticker.model_dump()
            }
            await manager.broadcast(json.dumps(message))
        
        await asyncio.sleep(1)  # Update every second

@app.get("/health")
async def health_check():
    return {"status": "ok", "timestamp": datetime.utcnow()}

@app.get("/leaderboard", response_model=List[LeaderboardEntry])
async def get_leaderboard():
    return [LeaderboardEntry(**user) for user in MOCK_USERS]

@app.get("/")
async def root():
    return {"message": "AstraTrade Backend API is running!", "status": "active"}

# Trading API endpoints
@app.get("/trading/pairs")
async def get_trading_pairs():
    """Get list of available trading pairs"""
    pairs = []
    for symbol, info in TRADING_PAIRS.items():
        ticker = generate_current_ticker(symbol)
        pairs.append({
            "symbol": symbol,
            "name": info["name"],
            "price": ticker.price,
            "change_24h": ticker.change_24h,
            "change_percent_24h": ticker.change_percent_24h
        })
    return {"pairs": pairs}

@app.get("/trading/ticker/{symbol}", response_model=TickerData)
async def get_ticker(symbol: str):
    """Get current ticker data for a symbol"""
    return generate_current_ticker(symbol.upper())

@app.get("/trading/candles/{symbol}")
async def get_candles(symbol: str, interval: str = "1m", limit: int = 100):
    """Get candlestick data for a symbol"""
    candles = generate_realistic_candle_data(symbol.upper(), limit)
    return {
        "symbol": symbol.upper(),
        "interval": interval,
        "candles": [candle.model_dump() for candle in candles]
    }

class TradeRequest(BaseModel):
    user_id: int
    asset: str = "ETH"
    amount: float = 100.0
    direction: str = "long"

class TradeResult(BaseModel):
    outcome: str
    profit_percentage: float  # Changed to snake_case to match frontend expectation
    message: str  # Changed from outcomeMessage to message
    xp_gained: int  # Changed from stellarShardsGained to xp_gained

@app.post("/trade")
async def execute_trade(trade_request: TradeRequest):
    """Execute a quick trade for the game"""
    try:
        # Simulate trade logic
        success_rate = 0.6  # 60% success rate for demo
        is_profitable = random.random() < success_rate
        is_critical = random.random() < 0.1  # 10% chance for critical forge
        
        if is_profitable:
            profit_percentage = random.uniform(1.0, 5.0)
            stellar_shards = int(random.uniform(10, 50))
            lumina = int(random.uniform(5, 15)) if is_critical else int(random.uniform(1, 8))
            outcome = "profit"
            message = f"🎉 Trade successful! +{profit_percentage:.1f}% profit"
            if is_critical:
                message += " ⚡ CRITICAL FORGE!"
        else:
            profit_percentage = -random.uniform(0.5, 3.0)
            stellar_shards = int(random.uniform(-20, -5))
            lumina = 0
            outcome = "loss"
            message = f"📉 Trade closed at {profit_percentage:.1f}% loss"
        
        return TradeResult(
            outcome=outcome,
            profit_percentage=profit_percentage,
            message=message,
            xp_gained=stellar_shards  # Using stellar_shards as XP for compatibility
        )
    except Exception as e:
        return {"error": str(e), "status": "failed"}

@app.websocket("/ws/trading")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time trading data"""
    await manager.connect(websocket)
    try:
        # Send initial data
        for symbol in TRADING_PAIRS.keys():
            ticker = generate_current_ticker(symbol)
            welcome_message = {
                "type": "ticker",
                "data": ticker.model_dump()
            }
            await websocket.send_text(json.dumps(welcome_message))
        
        # Keep connection alive and handle messages
        while True:
            try:
                data = await websocket.receive_text()
                # Echo back for now, can add more functionality later
                await websocket.send_text(f"Received: {data}")
            except WebSocketDisconnect:
                break
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# Start price feed in background
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(price_feed_generator())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)