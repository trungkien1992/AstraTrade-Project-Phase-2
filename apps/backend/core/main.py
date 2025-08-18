from fastapi import FastAPI, HTTPException, status, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import timedelta, datetime
from sqlalchemy.orm import Session

from .database import (
    get_db,
    create_tables,
    User as DBUser,
    Trade as DBTrade,
)
from ..models import game_models
from ..auth.auth import (
    authenticate_user,
    create_access_token,
    get_current_active_user,
    get_password_hash,
)
from ..services.trading_service import trading_service
from .config import settings
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from utils.logging import StructuredLogger
import time
import sentry_sdk
from prometheus_fastapi_instrumentator import Instrumentator

from contextlib import asynccontextmanager
from ..services.extended_exchange_client import ExtendedExchangeError

# Import Phase 3 API routers
from ..api.v1.constellations import router as constellations_router
from ..api.v1.prestige import router as prestige_router
from ..api.v1.viral_content import router as viral_content_router
from ..api.v1.nft_integration import router as nft_router

# Import Blockchain Domain API routers (Phase 1)
from ..api.v1.blockchain.wallets import router as blockchain_wallets_router
from ..api.v1.blockchain.transactions import router as blockchain_transactions_router
from ..api.v1.blockchain.gasless import router as blockchain_gasless_router

# Import Phase 3.5 Signing API router
from ..api.v1.blockchain.signing import router as blockchain_signing_router

# Import clan battle monitor
from ..tasks.clan_battle_monitor import start_battle_monitor, stop_battle_monitor


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
    # Start clan battle monitoring
    await start_battle_monitor()
    logger.log_structured(
        level="INFO", 
        event="app_startup", 
        message="Clan battle monitor started"
    )
    yield
    # Stop clan battle monitoring
    await stop_battle_monitor()
    logger.log_structured(
        level="INFO", 
        event="app_shutdown", 
        message="Clan battle monitor stopped"
    )


app = FastAPI(title="AstraTrade Backend API", version="1.0.0", lifespan=lifespan)

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Initialize Sentry (replace the DSN with your real value in production)
sentry_sdk.init(
    dsn=settings.sentry_dsn,  # Get DSN from settings
    traces_sample_rate=1.0,  # Adjust in production
    environment=settings.environment,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if settings.environment == "production":
    app.add_middleware(
        TrustedHostMiddleware, allowed_hosts=["yourdomain.com", "www.yourdomain.com"]
    )
else:
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])

logger = StructuredLogger("AstraTradeAPI")

# Include Phase 3 API routers
app.include_router(constellations_router, prefix="/api/v1")
app.include_router(prestige_router, prefix="/api/v1")
app.include_router(viral_content_router, prefix="/api/v1")
app.include_router(nft_router, prefix="/api/v1")

# Blockchain Domain API routes (Phase 1)
app.include_router(blockchain_wallets_router, prefix="/api/v1/blockchain")
app.include_router(blockchain_transactions_router, prefix="/api/v1/blockchain")
app.include_router(blockchain_gasless_router, prefix="/api/v1/blockchain")

# Phase 3.5 Signing API routes
app.include_router(blockchain_signing_router, prefix="/api/v1/blockchain")


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration_ms = (time.time() - start_time) * 1000
    logger.log_api_call(
        endpoint=str(request.url.path),
        method=request.method,
        status_code=response.status_code,
        duration_ms=duration_ms,
    )
    return response


@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["Strict-Transport-Security"] = (
        "max-age=63072000; includeSubDomains; preload"
    )
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "same-origin"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=()"
    return response


# --- Pydantic Models ---
class UserResponse(BaseModel):
    id: int
    username: str
    email: Optional[str] = None
    xp: int = 0
    level: int = 1
    wallet_address: Optional[str] = None
    is_active: bool = True

    model_config = {"from_attributes": True}


class UserRegisterRequest(BaseModel):
    username: str
    email: Optional[str] = None
    password: str
    wallet_address: Optional[str] = None


class UserLoginRequest(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class UserLoginResponse(BaseModel):
    user: UserResponse
    token: Token


class TradeRequest(BaseModel):
    asset: str
    direction: str  # 'long' or 'short'
    amount: float


class TradeResult(BaseModel):
    trade_id: int
    outcome: str  # 'profit', 'loss', 'breakeven'
    profit_percentage: float
    message: str
    xp_gained: int


class LeaderboardEntry(BaseModel):
    user_id: int
    username: str
    xp: int
    level: int

    model_config = {"from_attributes": True}


class PortfolioBalance(BaseModel):
    balances: dict
    total_value_usd: float


class AddXPRequest(BaseModel):
    amount: int


# --- Database-backed endpoints ---


# --- Endpoints ---
@app.post("/register", summary="Register a new user", response_model=UserResponse)
@limiter.limit("5/second")
async def register_user(
    req: UserRegisterRequest, db: Session = Depends(get_db), request: Request = None
):
    # Check if username already exists
    existing_user = db.query(DBUser).filter(DBUser.username == req.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    # Check if email already exists
    if req.email:
        existing_email = db.query(DBUser).filter(DBUser.email == req.email).first()
        if existing_email:
            raise HTTPException(status_code=400, detail="Email already exists")

    # Create new user
    hashed_password = get_password_hash(req.password)
    user = DBUser(
        username=req.username,
        email=req.email,
        hashed_password=hashed_password,
        wallet_address=req.wallet_address,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return UserResponse.model_validate(user)


@app.post("/login", summary="Login a user", response_model=UserLoginResponse)
async def login_user(req: UserLoginRequest, db: Session = Depends(get_db)):
    user = authenticate_user(db, req.username, req.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    return UserLoginResponse(
        user=UserResponse.model_validate(user),
        token=Token(access_token=access_token, token_type="bearer"),
    )


@app.get("/users/me", summary="Get current user", response_model=UserResponse)
async def get_current_user_info(
    current_user: DBUser = Depends(get_current_active_user),
):
    return UserResponse.model_validate(current_user)


@app.get("/users", summary="List all users", response_model=List[UserResponse])
async def get_users(
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_active_user),
):
    users = db.query(DBUser).all()
    return [UserResponse.model_validate(user) for user in users]


@app.post("/trade", summary="Place a trade", response_model=TradeResult)
async def place_trade(
    trade: TradeRequest,
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_active_user),
):
    # Execute trade using the enhanced trading service
    try:
        result = await trading_service.execute_trade(
            db=db,
            user_id=current_user.id,
            asset=trade.asset,
            direction=trade.direction,
            amount=trade.amount,
        )
        return TradeResult(**result)
    except ExtendedExchangeError as e:
        raise HTTPException(status_code=400, detail=f"Exchange error: {e.message}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/trade/mock", summary="Place a mock trade", response_model=TradeResult)
async def place_mock_trade(
    trade: TradeRequest,
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_active_user),
):
    # Execute mock trade (force simulated trading)
    try:
        result = await trading_service.execute_trade(
            db=db,
            user_id=current_user.id,
            asset=trade.asset,
            direction=trade.direction,
            amount=trade.amount,
            api_keys=None,  # Force simulated trading
        )
        return TradeResult(**result)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/trade/real", summary="Place a real trade", response_model=TradeResult)
async def place_real_trade(
    trade: TradeRequest,
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_active_user),
):
    # Execute real trade (requires API configuration)
    try:
        # Get API keys from user's stored credentials
        # For demo purposes, this will fall back to simulation if no API keys configured
        api_keys = getattr(current_user, 'api_credentials', None)
        
        result = await trading_service.execute_trade(
            db=db,
            user_id=current_user.id,
            asset=trade.asset,
            direction=trade.direction,
            amount=trade.amount,
            api_keys=api_keys,
        )
        return TradeResult(**result)
    except ExtendedExchangeError as e:
        raise HTTPException(status_code=400, detail=f"Exchange error: {e.message}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get(
    "/leaderboard", summary="Get leaderboard", response_model=List[LeaderboardEntry]
)
async def get_leaderboard(db: Session = Depends(get_db)):
    users = db.query(DBUser).order_by(DBUser.xp.desc()).limit(100).all()
    return [
        LeaderboardEntry(
            user_id=user.id, username=user.username, xp=user.xp, level=user.level
        )
        for user in users
    ]


@app.post("/xp/add", summary="Add XP to current user")
async def add_xp(
    req: AddXPRequest,
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_active_user),
):
    current_user.xp += req.amount
    current_user.level = 1 + current_user.xp // 100
    db.commit()

    return {"status": "ok", "new_xp": current_user.xp, "new_level": current_user.level}


@app.get(
    "/portfolio/balance",
    summary="Get portfolio balance",
    response_model=PortfolioBalance,
)
async def get_portfolio_balance(
    current_user: DBUser = Depends(get_current_active_user),
):
    balance_data = await trading_service.get_portfolio_balance(current_user.id)
    return PortfolioBalance(
        balances=balance_data, total_value_usd=balance_data.get("total_value_usd", 0.0)
    )


@app.get("/trades", summary="Get user's trade history")
async def get_trades(
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_active_user),
):
    trades = (
        db.query(DBTrade)
        .filter(DBTrade.user_id == current_user.id)
        .order_by(DBTrade.created_at.desc())
        .all()
    )
    return trades


Instrumentator().instrument(app).expose(app)


@app.get("/health", summary="Health check endpoint")
async def health_check():
    return {"status": "ok", "timestamp": datetime.utcnow()}
# Daily rewards system for mobile gamification
@app.post('/rewards/daily', summary="Award daily rewards to active users")
async def award_daily_rewards(db: Session = Depends(get_db)):
    """
    Award daily rewards to users based on their activity and streaks.
    Mobile-first implementation for gamified trading experience.
    """
    try:
        # Get all users who logged in today
        today = date.today()
        yesterday = today - timedelta(days=1)
        
        # Find users with activity in the last 24 hours
        recent_trades = db.query(DBTrade).filter(
            DBTrade.created_at >= yesterday
        ).all()
        
        active_users = set(trade.user_id for trade in recent_trades)
        
        rewards_awarded = 0
        total_xp_awarded = 0
        
        for user_id in active_users:
            user = db.query(DBUser).filter(DBUser.id == user_id).first()
            if not user:
                continue
                
            # Calculate daily reward based on activity level
            user_trades_today = [t for t in recent_trades if t.user_id == user_id]
            base_daily_xp = 50  # Base daily login bonus
            
            # Activity multiplier based on number of trades
            activity_multiplier = min(1.0 + (len(user_trades_today) * 0.1), 3.0)
            
            # Streak bonus calculation
            current_streak = getattr(user, 'daily_streak', 0)
            streak_bonus = min(current_streak * 5, 100)  # Max 100 XP streak bonus
            
            # Calculate total daily reward
            daily_xp = int(base_daily_xp * activity_multiplier + streak_bonus)
            
            # Award the XP
            user.xp = (user.xp or 0) + daily_xp
            
            # Update streak (simplified - in production would check actual daily activity)
            user.daily_streak = current_streak + 1
            
            # Add daily reward record (if table exists)
            try:
                daily_reward = DailyReward(
                    user_id=user_id,
                    reward_date=today,
                    xp_awarded=daily_xp,
                    streak_bonus=streak_bonus,
                    activity_multiplier=activity_multiplier
                )
                db.add(daily_reward)
            except:
                # Table might not exist, skip record keeping
                pass
            
            rewards_awarded += 1
            total_xp_awarded += daily_xp
        
        # Commit all changes
        db.commit()
        
        return {
            "status": "success",
            "rewards_awarded": rewards_awarded,
            "total_xp_awarded": total_xp_awarded,
            "active_users": len(active_users),
            "reward_date": today.isoformat(),
            "message": f"Daily rewards awarded to {rewards_awarded} active mobile users"
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"Daily rewards error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to award daily rewards: {str(e)}")

# Mobile-specific gamification endpoint
@app.post('/mobile/daily-check-in', summary="Mobile daily check-in for bonus XP")
async def mobile_daily_checkin(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Mobile-optimized daily check-in system for consistent engagement.
    """
    try:
        user_id = current_user.get("id")
        today = date.today()
        
        # Check if user already checked in today
        last_checkin = getattr(current_user, 'last_checkin', None)
        if last_checkin and last_checkin == today:
            return {
                "status": "already_checked_in",
                "message": "Already checked in today!",
                "next_checkin": (today + timedelta(days=1)).isoformat()
            }
        
        # Award check-in bonus
        checkin_xp = 25  # Base daily check-in XP
        consecutive_days = getattr(current_user, 'consecutive_checkins', 0) + 1
        
        # Consecutive day bonus (mobile engagement)
        if consecutive_days >= 7:
            checkin_xp += 50  # Weekly bonus
        elif consecutive_days >= 3:
            checkin_xp += 25  # 3-day bonus
            
        # Update user
        user = db.query(DBUser).filter(DBUser.id == user_id).first()
        if user:
            user.xp = (user.xp or 0) + checkin_xp
            user.last_checkin = today
            user.consecutive_checkins = consecutive_days
            db.commit()
        
        return {
            "status": "success",
            "xp_awarded": checkin_xp,
            "consecutive_days": consecutive_days,
            "total_xp": (user.xp or 0),
            "message": f"Daily check-in complete! +{checkin_xp} XP"
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"Mobile check-in error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Check-in failed: {str(e)}")
