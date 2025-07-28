from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import List, Optional
import asyncio

from dependencies import get_current_user, get_trading_service, get_db
from schemas.trade import TradeRequest, TradeResponse, TradeHistoryResponse
from services.trading_service import TradingService
from models.user import User
from core.rate_limiter import RateLimiter
from core.monitoring import metrics

router = APIRouter(prefix="/api/v1/trading", tags=["trading"])

# Rate limiter for trading endpoints
trade_limiter = RateLimiter(
    max_requests=10,
    window_seconds=60
)

@router.post("/execute", response_model=TradeResponse)
@metrics.track_execution_time("trade_execution")
async def execute_trade(
    request: TradeRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    trading_service: TradingService = Depends(get_trading_service),
    db = Depends(get_db)
):
    """
    Execute a trade (mock or real).
    
    Rate limited to 10 trades per minute per user.
    """
    # Check rate limit
    if not await trade_limiter.check_limit(f"trade:{current_user.id}"):
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Please wait before placing another trade."
        )
    
    try:
        # Execute trade
        result = await trading_service.execute_trade(
            user_id=current_user.id,
            request=request
        )
        
        # Track metrics
        metrics.increment("trades_total", tags={
            "status": "success",
            "type": "mock" if request.is_mock else "real"
        })
        
        # Schedule background tasks
        background_tasks.add_task(
            update_user_statistics,
            current_user.id,
            result.trade_id
        )
        
        return TradeResponse(
            success=True,
            trade_id=result.trade_id,
            executed_price=result.executed_price,
            profit_amount=result.profit_amount,
            profit_percentage=result.profit_percentage,
            rewards=result.rewards,
            message="Trade executed successfully"
        )
        
    except ValueError as e:
        metrics.increment("trades_total", tags={"status": "validation_error"})
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        metrics.increment("trades_total", tags={"status": "error"})
        raise HTTPException(status_code=500, detail="Trade execution failed")

@router.get("/history", response_model=List[TradeHistoryResponse])
async def get_trade_history(
    limit: int = 50,
    offset: int = 0,
    asset: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Get user's trade history with pagination and filtering.
    """
    query = db.query(Trade).filter(Trade.user_id == current_user.id)
    
    if asset:
        query = query.filter(Trade.asset == asset)
    
    trades = query.order_by(Trade.created_at.desc()).offset(offset).limit(limit).all()
    
    return [
        TradeHistoryResponse(
            id=trade.id,
            asset=trade.asset,
            direction=trade.direction,
            amount=trade.amount,
            executed_price=trade.executed_price,
            profit_amount=trade.profit_amount,
            profit_percentage=trade.profit_percentage,
            status=trade.status,
            created_at=trade.created_at,
            execution_time=trade.execution_time
        )
        for trade in trades
    ]

@router.get("/statistics")
async def get_trading_statistics(
    current_user: User = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Get detailed trading statistics for the user.
    """
    stats = await calculate_user_statistics(db, current_user.id)
    
    return JSONResponse(content={
        "total_trades": stats['total_trades'],
        "winning_trades": stats['winning_trades'],
        "losing_trades": stats['losing_trades'],
        "win_rate": stats['win_rate'],
        "total_profit": stats['total_profit'],
        "average_profit": stats['average_profit'],
        "best_trade": stats['best_trade'],
        "worst_trade": stats['worst_trade'],
        "favorite_asset": stats['favorite_asset'],
        "current_streak": current_user.current_streak,
        "longest_streak": current_user.longest_streak
    })

@router.ws("/live")
async def trading_websocket(
    websocket: WebSocket,
    current_user: User = Depends(get_current_user)
):
    """
    WebSocket endpoint for live trading updates.
    """
    await websocket.accept()
    
    try:
        # Subscribe to user's trading events
        async with event_bus.subscribe(f"user:{current_user.id}:trades") as subscriber:
            while True:
                # Wait for either a message from client or a trading event
                message_task = asyncio.create_task(websocket.receive_text())
                event_task = asyncio.create_task(subscriber.get())
                
                done, pending = await asyncio.wait(
                    {message_task, event_task},
                    return_when=asyncio.FIRST_COMPLETED
                )
                
                # Cancel pending tasks
                for task in pending:
                    task.cancel()
                
                # Handle completed task
                for task in done:
                    if task == message_task:
                        # Handle client message (e.g., subscribe to specific assets)
                        message = task.result()
                        await handle_client_message(websocket, message)
                    else:
                        # Send trading event to client
                        event = task.result()
                        await websocket.send_json(event.to_dict())
                        
    except WebSocketDisconnect:
        pass
    finally:
        await websocket.close()

# Helper functions
async def update_user_statistics(user_id: int, trade_id: int):
    """Background task to update user statistics."""
    # Implementation details...
    pass

async def calculate_user_statistics(db, user_id: int) -> dict:
    """Calculate comprehensive user trading statistics."""
    # Implementation details...
    pass

async def handle_client_message(websocket: WebSocket, message: str):
    """Handle incoming WebSocket messages from client."""
    # Implementation details...
    pass
