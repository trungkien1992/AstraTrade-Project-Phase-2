from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum

class WebSocketMessageType(Enum):
    """WebSocket message types"""
    # Server to client messages
    INITIAL_STATE = "initial_state"
    LEADERBOARD_UPDATE = "leaderboard_update"
    LIVE_TRADE = "live_trade"
    ACHIEVEMENT_UNLOCKED = "achievement_unlocked"
    TOURNAMENT_EVENT = "tournament_event"
    HEARTBEAT = "heartbeat"
    NEARBY_COMPETITORS = "nearby_competitors"
    AI_TRADER_INFO = "ai_trader_info"
    DETAILED_LEADERBOARD = "detailed_leaderboard"
    AUTHENTICATION_SUCCESS = "authentication_success"
    ERROR = "error"
    
    # Client to server messages
    GET_NEARBY_COMPETITORS = "get_nearby_competitors"
    GET_AI_TRADER_INFO = "get_ai_trader_info"
    GET_DETAILED_LEADERBOARD = "get_detailed_leaderboard"
    AUTHENTICATE = "authenticate"
    HEARTBEAT_RESPONSE = "heartbeat_response"

class ConnectionState(Enum):
    """WebSocket connection states"""
    CONNECTING = "connecting"
    CONNECTED = "connected"
    AUTHENTICATED = "authenticated"
    DISCONNECTED = "disconnected"

# Base message models
class BaseWebSocketMessage(BaseModel):
    """Base WebSocket message structure"""
    type: str
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    
class ClientMessage(BaseWebSocketMessage):
    """Client to server message"""
    data: Optional[Dict[str, Any]] = None

class ServerMessage(BaseWebSocketMessage):
    """Server to client message"""
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

# Tournament data models
class LeaderboardEntry(BaseModel):
    """Tournament leaderboard entry"""
    rank: int
    user_id: str
    username: str
    score: float
    is_ai: bool = False
    avatar: Optional[str] = None
    league: Optional[str] = None
    change_direction: Optional[str] = None  # "up", "down", "same"
    change_amount: Optional[int] = None

class TournamentMetadata(BaseModel):
    """Tournament metadata"""
    tournament_id: str
    status: str  # "active", "ended", "upcoming"
    start_time: str
    end_time: str
    total_participants: int
    total_trades: int
    prize_pool: Optional[float] = None
    entry_fee: Optional[float] = None

class UserTournamentStats(BaseModel):
    """User's tournament statistics"""
    user_id: str
    total_trades: int
    winning_trades: int
    total_profit: float
    total_volume: float
    win_rate: float
    portfolio_value: float
    rank: Optional[int] = None
    percentile: Optional[float] = None

class LiveTrade(BaseModel):
    """Live trade notification"""
    trade_id: str
    user_id: str
    username: str
    symbol: str
    side: str  # "BUY" or "SELL"
    amount: float
    price: Optional[float] = None
    profit: Optional[float] = None
    profit_percentage: Optional[float] = None
    is_ai: bool = False
    ai_strategy: Optional[str] = None
    timestamp: str

class Achievement(BaseModel):
    """Achievement unlocked"""
    achievement_id: str
    user_id: str
    username: str
    title: str
    description: str
    icon: str
    points: int
    rarity: str  # "common", "rare", "epic", "legendary"
    category: str  # "trading", "social", "progression", "special"
    unlocked_at: str

class AITraderInfo(BaseModel):
    """AI Trader detailed information"""
    id: str
    name: str
    title: str
    strategy: str
    backstory: str
    risk_profile: Dict[str, float]
    personality_traits: Dict[str, float]
    preferred_symbols: List[str]
    trading_hours: List[int]
    current_state: Dict[str, Any]
    performance_stats: Optional[Dict[str, Any]] = None

class TournamentEvent(BaseModel):
    """Special tournament events"""
    event_id: str
    event_type: str  # "bonus_round", "market_crash", "volatility_spike", "special_announcement"
    title: str
    description: str
    duration_minutes: Optional[int] = None
    multiplier: Optional[float] = None
    affects_leaderboard: bool = True
    started_at: str
    ends_at: Optional[str] = None

# Server to Client message data models
class InitialStateData(BaseModel):
    """Initial state data sent on connection"""
    tournament_id: str
    leaderboard: List[LeaderboardEntry]
    user_rank: Optional[int] = None
    user_score: Optional[float] = None
    user_stats: Optional[UserTournamentStats] = None
    active_connections: int
    tournament_meta: TournamentMetadata
    server_time: float
    ai_traders_count: int
    recent_trades: List[LiveTrade] = []

class LeaderboardUpdateData(BaseModel):
    """Leaderboard position change update"""
    user_id: str
    username: str
    old_rank: Optional[int] = None
    new_rank: int
    old_score: Optional[float] = None
    new_score: float
    rank_change: int = 0  # Positive = moved up, negative = moved down
    score_change: float = 0.0
    is_ai: bool = False

class NearbyCompetitorsData(BaseModel):
    """Nearby competitors response"""
    competitors: List[LeaderboardEntry]
    user_rank: int
    radius: int
    total_participants: int

class DetailedLeaderboardData(BaseModel):
    """Detailed leaderboard with stats"""
    leaderboard: List[Dict[str, Any]]  # Enhanced leaderboard entries with stats
    start: int
    limit: int
    total_participants: int
    user_rank: Optional[int] = None

class AuthenticationData(BaseModel):
    """Authentication success response"""
    user_id: str
    username: Optional[str] = None
    authenticated: bool = True
    permissions: List[str] = []

class HeartbeatData(BaseModel):
    """Heartbeat message data"""
    server_time: float
    connection_id: Optional[str] = None
    uptime_seconds: Optional[float] = None

class ErrorData(BaseModel):
    """Error message data"""
    error_code: str
    error_message: str
    details: Optional[Dict[str, Any]] = None
    retry_after: Optional[int] = None

# Client to Server message data models
class GetNearbyCompetitorsRequest(BaseModel):
    """Request nearby competitors"""
    radius: int = Field(default=5, ge=1, le=20)
    
class GetAITraderInfoRequest(BaseModel):
    """Request AI trader information"""
    ai_id: str

class GetDetailedLeaderboardRequest(BaseModel):
    """Request detailed leaderboard"""
    start: int = Field(default=0, ge=0)
    limit: int = Field(default=50, ge=1, le=100)

class AuthenticateRequest(BaseModel):
    """Authentication request"""
    token: str
    refresh_token: Optional[str] = None

class HeartbeatResponseRequest(BaseModel):
    """Heartbeat response from client"""
    received_at: float
    client_time: float

# Complete message type definitions
class InitialStateMessage(ServerMessage):
    """Initial state message"""
    type: str = WebSocketMessageType.INITIAL_STATE.value
    data: InitialStateData

class LeaderboardUpdateMessage(ServerMessage):
    """Leaderboard update message"""
    type: str = WebSocketMessageType.LEADERBOARD_UPDATE.value
    data: LeaderboardUpdateData

class LiveTradeMessage(ServerMessage):
    """Live trade message"""
    type: str = WebSocketMessageType.LIVE_TRADE.value
    data: LiveTrade

class AchievementUnlockedMessage(ServerMessage):
    """Achievement unlocked message"""
    type: str = WebSocketMessageType.ACHIEVEMENT_UNLOCKED.value
    data: Achievement

class TournamentEventMessage(ServerMessage):
    """Tournament event message"""
    type: str = WebSocketMessageType.TOURNAMENT_EVENT.value
    data: TournamentEvent

class HeartbeatMessage(ServerMessage):
    """Heartbeat message"""
    type: str = WebSocketMessageType.HEARTBEAT.value
    data: HeartbeatData

class NearbyCompetitorsMessage(ServerMessage):
    """Nearby competitors message"""
    type: str = WebSocketMessageType.NEARBY_COMPETITORS.value
    data: NearbyCompetitorsData

class AITraderInfoMessage(ServerMessage):
    """AI trader info message"""
    type: str = WebSocketMessageType.AI_TRADER_INFO.value
    data: AITraderInfo

class DetailedLeaderboardMessage(ServerMessage):
    """Detailed leaderboard message"""
    type: str = WebSocketMessageType.DETAILED_LEADERBOARD.value
    data: DetailedLeaderboardData

class AuthenticationSuccessMessage(ServerMessage):
    """Authentication success message"""
    type: str = WebSocketMessageType.AUTHENTICATION_SUCCESS.value
    data: AuthenticationData

class ErrorMessage(ServerMessage):
    """Error message"""
    type: str = WebSocketMessageType.ERROR.value
    data: ErrorData

# Message parsing and validation
class MessageParser:
    """Utility class for parsing and validating WebSocket messages"""
    
    @staticmethod
    def parse_client_message(data: Dict[str, Any]) -> Optional[BaseModel]:
        """Parse incoming client message"""
        try:
            msg_type = data.get('type')
            
            if msg_type == WebSocketMessageType.GET_NEARBY_COMPETITORS.value:
                return GetNearbyCompetitorsRequest(**data.get('data', {}))
            elif msg_type == WebSocketMessageType.GET_AI_TRADER_INFO.value:
                return GetAITraderInfoRequest(**data.get('data', {}))
            elif msg_type == WebSocketMessageType.GET_DETAILED_LEADERBOARD.value:
                return GetDetailedLeaderboardRequest(**data.get('data', {}))
            elif msg_type == WebSocketMessageType.AUTHENTICATE.value:
                return AuthenticateRequest(**data.get('data', {}))
            elif msg_type == WebSocketMessageType.HEARTBEAT_RESPONSE.value:
                return HeartbeatResponseRequest(**data.get('data', {}))
            
            return None
        except Exception:
            return None
    
    @staticmethod
    def create_server_message(msg_type: WebSocketMessageType, data: Any, error: str = None) -> Dict[str, Any]:
        """Create server message dict"""
        message = {
            'type': msg_type.value,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        if error:
            message['error'] = error
        else:
            message['data'] = data.dict() if hasattr(data, 'dict') else data
            
        return message

# Connection statistics models
class ConnectionStats(BaseModel):
    """WebSocket connection statistics"""
    total_connections: int
    peak_concurrent: int
    messages_sent: int
    messages_received: int
    reconnections: int
    current_connections: int
    active_tournaments: int
    tournament_breakdown: Dict[str, int]

class TournamentConnectionInfo(BaseModel):
    """Tournament connection information"""
    tournament_id: str
    active_connections: int
    authenticated_users: int
    anonymous_users: int
    peak_connections: int
    total_messages_sent: int
    total_messages_received: int
    average_session_duration: Optional[float] = None

# Rate limiting models
class RateLimitInfo(BaseModel):
    """Rate limiting information"""
    limit_per_minute: int
    current_usage: int
    reset_time: str
    blocked_until: Optional[str] = None

# Health check models
class WebSocketHealthCheck(BaseModel):
    """WebSocket health check response"""
    status: str  # "healthy", "degraded", "unhealthy"
    active_connections: int
    active_tournaments: int
    redis_connected: bool
    pubsub_channels: int
    last_heartbeat: str
    uptime_seconds: float
    memory_usage_mb: Optional[float] = None
    cpu_usage_percent: Optional[float] = None

# Tournament phase models
class TournamentPhase(Enum):
    """Tournament phases"""
    REGISTRATION = "registration"
    STARTING = "starting"
    ACTIVE = "active"
    CLOSING = "closing"
    ENDED = "ended"
    ARCHIVED = "archived"

class TournamentStatusUpdate(BaseModel):
    """Tournament status update"""
    tournament_id: str
    old_phase: TournamentPhase
    new_phase: TournamentPhase
    phase_start_time: str
    phase_end_time: Optional[str] = None
    participant_count: int
    total_trades: int
    message: Optional[str] = None

# Leaderboard snapshot models
class LeaderboardSnapshot(BaseModel):
    """Leaderboard snapshot for historical data"""
    tournament_id: str
    snapshot_time: str
    top_performers: List[LeaderboardEntry]
    total_participants: int
    snapshot_type: str  # "hourly", "daily", "final"
    
# Market condition models (for AI trading context)
class MarketConditionsUpdate(BaseModel):
    """Market conditions update for AI trading"""
    timestamp: str
    volatility: float
    trend_direction: str  # "UP", "DOWN", "SIDEWAYS"
    trend_strength: float
    volume_profile: Dict[str, Any]
    sentiment_score: float
    major_events: List[str] = []

# Event aggregation models
class EventSummary(BaseModel):
    """Summary of events over time period"""
    time_period: str
    total_trades: int
    unique_traders: int
    ai_trades: int
    human_trades: int
    top_performers: List[str]
    major_movements: List[LeaderboardUpdateData]
    achievements_unlocked: int
    tournament_events: List[TournamentEvent]