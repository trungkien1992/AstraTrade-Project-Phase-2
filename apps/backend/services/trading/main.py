"""
AstraTrade Trading Service - Containerized Microservice
Handles trade execution, position management, and market operations.
"""

import asyncio
import logging
from datetime import datetime, timezone
from decimal import Decimal
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.responses import JSONResponse

# Import domain logic

from domains.trading.entities import Trade, Position
from domains.trading.services import TradingDomainService
from domains.trading.value_objects import Asset, Money, TradeDirection, TradeStatus, AssetCategory

# Import base service components
from services.base import (
    create_app, 
    config, 
    get_database_session, 
    get_event_bus,
    start_heartbeat,
    metrics_collector,
    track_database_operation,
    track_redis_operation
)

# Import service registration
from services.base.service_registration import (
    create_service_lifespan,
    create_enhanced_health_check,
    get_service_config
)

# Configure logging
logger = logging.getLogger(__name__)

# Get service configuration
service_config = get_service_config()

# Create service lifespan with registration
service_lifespan = create_service_lifespan(
    service_name="trading",
    service_port=service_config["service_port"],
    service_version="1.0.0",
    metadata={
        "domain": "trading",
        "capabilities": [
            "trade_execution",
            "position_management", 
            "market_data",
            "risk_management",
            "trade_history"
        ],
        "dependencies": ["database", "redis", "event_bus"]
    }
)

# Create FastAPI app with enhanced service discovery
app = create_app(
    title="AstraTrade Trading Service",
    description="Microservice for trade execution and position management",
    version="1.0.0",
    lifespan=service_lifespan
)



# Initialize trading service
trading_service = None

@app.on_event("startup")
async def startup_event():
    """Initialize service on startup."""
    global trading_service
    
    logger.info("Starting Trading Service...")
    
    # Initialize trading service
    trading_service = TradingDomainService()
    
    # Store service name in app state for health checks
    app.state.service_name = "trading"
    
    logger.info("Trading Service domain logic initialized")


# Trading Endpoints

@app.post("/api/v1/trading/execute", response_model=dict, tags=["Trading"])
async def execute_trade(
    trade_data: dict,
    request: Request,
    db_session = Depends(get_database_session),
    event_bus = Depends(get_event_bus)
):
    """Execute a trade order."""
    try:
        # Extract trade parameters
        symbol = trade_data.get("symbol", "BTC/USD")
        quantity = float(trade_data.get("quantity", 0.01))
        trade_type = trade_data.get("type", "market")
        user_id = trade_data.get("user_id", "user-default")
        
        if quantity <= 0:
            raise HTTPException(status_code=400, detail="Quantity must be positive")
        
        # Get correlation ID from request
        correlation_id = getattr(request.state, 'correlation_id', None)
        
        # Create trade entity
        trade = Trade(
            user_id=1,  # Mock user ID for now
            asset=Asset(symbol=symbol, name=f"{symbol} Trading Pair", category=AssetCategory.CRYPTO),
            direction=TradeDirection.LONG if trade_type == "buy" else TradeDirection.SHORT,
            amount=Money(amount=Decimal(str(quantity)), currency="USD"),
            entry_price=Money(amount=Decimal("45000.00"), currency="USD")
        )
        
        # Execute trade (in production would integrate with exchange)
        execution_result = {
            "trade_id": trade.trade_id,
            "user_id": trade.user_id,
            "symbol": trade.asset.symbol,
            "quantity": str(trade.amount.amount),
            "price": str(trade.entry_price.amount),
            "type": trade_type,
            "status": trade.status.value,
            "executed_at": trade.created_at.isoformat(),
            "correlation_id": correlation_id
        }
        
        # Publish trade execution event
        await event_bus.publish_event(
            "astra.trading.trade_executed.v1",
            {
                "trade_id": trade.trade_id,
                "user_id": trade.user_id,
                "symbol": trade.asset.symbol,
                "quantity": str(trade.amount.amount),
                "price": str(trade.entry_price.amount),
                "trade_type": trade_type,
                "correlation_id": correlation_id
            }
        )
        
        # Update position event
        await event_bus.publish_event(
            "astra.trading.position_updated.v1",
            {
                "user_id": user_id,
                "symbol": symbol,
                "new_quantity": quantity,
                "average_price": 45000.00,
                "unrealized_pnl": 0.0,
                "correlation_id": correlation_id
            }
        )
        
        # Record business metrics
        metrics_collector.record_business_operation("trade_execution", success=True)
        metrics_collector.record_event_published("TradeExecuted", "astra.trading.trade_executed.v1")
        
        logger.info(f"Trade executed: {trade.trade_id.value} for user {user_id}")
        
        return JSONResponse(
            status_code=200,
            content={
                "message": "Trade executed successfully",
                "trade": execution_result
            }
        )
        
    except Exception as e:
        logger.error(f"Error executing trade: {e}")
        metrics_collector.record_business_operation("trade_execution", success=False)
        
        raise HTTPException(status_code=500, detail=f"Trade execution failed: {str(e)}")


@app.get("/api/v1/trading/positions/{user_id}", response_model=dict, tags=["Trading"])
@track_database_operation("get_positions")
async def get_user_positions(
    user_id: str,
    db_session = Depends(get_database_session)
):
    """Get user's trading positions."""
    try:
        # In production, would query database
        positions = [
            {
                "symbol": "BTC/USD",
                "quantity": 0.05,
                "average_price": 44500.00,
                "current_price": 45000.00,
                "unrealized_pnl": 25.00,
                "side": "long"
            },
            {
                "symbol": "ETH/USD", 
                "quantity": 1.2,
                "average_price": 2800.00,
                "current_price": 2850.00,
                "unrealized_pnl": 60.00,
                "side": "long"
            }
        ]
        
        metrics_collector.record_business_operation("get_positions", success=True)
        
        return {
            "user_id": user_id,
            "positions": positions,
            "total_unrealized_pnl": sum(pos["unrealized_pnl"] for pos in positions)
        }
        
    except Exception as e:
        logger.error(f"Error getting positions for user {user_id}: {e}")
        metrics_collector.record_business_operation("get_positions", success=False)
        
        raise HTTPException(status_code=500, detail="Failed to get positions")


@app.get("/api/v1/trading/history/{user_id}", response_model=dict, tags=["Trading"])
@track_database_operation("get_trade_history")
async def get_trade_history(
    user_id: str,
    limit: int = 50,
    offset: int = 0,
    db_session = Depends(get_database_session)
):
    """Get user's trade history."""
    try:
        # In production, would query database with pagination
        trades = []
        for i in range(offset, min(offset + limit, offset + 10)):  # Mock 10 trades
            trades.append({
                "trade_id": f"trade-{i:06d}",
                "symbol": "BTC/USD" if i % 2 == 0 else "ETH/USD",
                "quantity": 0.01 * (i + 1),
                "price": 45000.00 - (i * 100),
                "type": "market",
                "side": "buy" if i % 2 == 0 else "sell",
                "status": "executed",
                "executed_at": f"2025-08-0{(i % 2) + 1}T{10 + (i % 12):02d}:00:00Z"
            })
        
        metrics_collector.record_business_operation("get_trade_history", success=True)
        
        return {
            "user_id": user_id,
            "trades": trades,
            "total": 100,  # Mock total
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        logger.error(f"Error getting trade history for user {user_id}: {e}")
        metrics_collector.record_business_operation("get_trade_history", success=False)
        
        raise HTTPException(status_code=500, detail="Failed to get trade history")


# Market Data Endpoints

@app.get("/api/v1/trading/markets", response_model=dict, tags=["Market Data"])
@track_redis_operation("get_market_data")
async def get_market_data(
    symbols: str = "BTC/USD,ETH/USD",
    redis_client = Depends(lambda: None)  # Mock dependency
):
    """Get current market data."""
    try:
        symbol_list = symbols.split(",")
        
        # In production, would fetch from Redis cache or external API
        market_data = {}
        base_prices = {"BTC/USD": 45000.00, "ETH/USD": 2850.00, "SOL/USD": 180.00}
        
        for symbol in symbol_list:
            base_price = base_prices.get(symbol, 100.00)
            market_data[symbol] = {
                "price": base_price,
                "volume_24h": base_price * 1000,
                "change_24h": f"{((hash(symbol) % 1000) / 100 - 5):.2f}%",
                "high_24h": base_price * 1.05,
                "low_24h": base_price * 0.95,
                "last_updated": datetime.now(timezone.utc).isoformat()
            }
        
        metrics_collector.record_business_operation("get_market_data", success=True)
        
        return {
            "markets": market_data,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting market data: {e}")
        metrics_collector.record_business_operation("get_market_data", success=False)
        
        raise HTTPException(status_code=500, detail="Failed to get market data")


# Risk Management Endpoints

@app.post("/api/v1/trading/risk/check", response_model=dict, tags=["Risk Management"])
async def check_trade_risk(
    risk_params: dict,
    event_bus = Depends(get_event_bus)
):
    """Check trade risk before execution."""
    try:
        user_id = risk_params.get("user_id")
        symbol = risk_params.get("symbol")
        quantity = float(risk_params.get("quantity", 0))
        
        # Mock risk calculation
        portfolio_value = 10000.00  # Mock portfolio value
        trade_value = quantity * 45000.00  # Mock calculation
        risk_percentage = (trade_value / portfolio_value) * 100
        
        risk_assessment = {
            "user_id": user_id,
            "symbol": symbol,
            "quantity": quantity,
            "trade_value": trade_value,
            "portfolio_value": portfolio_value,
            "risk_percentage": risk_percentage,
            "risk_level": "high" if risk_percentage > 10 else "medium" if risk_percentage > 5 else "low",
            "approved": risk_percentage <= 15,  # Max 15% risk
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        # Publish risk alert if high risk
        if risk_percentage > 10:
            await event_bus.publish_event(
                "astra.trading.risk_alert.v1",
                {
                    "user_id": user_id,
                    "alert_type": "high_risk_trade",
                    "symbol": symbol,
                    "risk_level": risk_percentage,
                    "message": f"High risk trade: {risk_percentage:.1f}% of portfolio"
                }
            )
        
        metrics_collector.record_business_operation("risk_check", success=True)
        
        return risk_assessment
        
    except Exception as e:
        logger.error(f"Error checking trade risk: {e}")
        metrics_collector.record_business_operation("risk_check", success=False)
        
        raise HTTPException(status_code=500, detail="Risk check failed")


# Enhanced health check with service discovery integration
async def check_trading_service_health():
    """Check trading service specific health."""
    # Check if trading service is initialized
    if trading_service is None:
        raise Exception("Trading service not initialized")
    
    # Could add more specific health checks here
    return {
        "trading_service_initialized": True,
        "capabilities_count": 5,
        "last_trade_time": datetime.now(timezone.utc).isoformat()
    }

enhanced_health_check = create_enhanced_health_check({
    "trading_service": check_trading_service_health,
    "database": lambda: "connected",  # Would check actual DB connection
    "event_bus": lambda: "connected"  # Would check actual event bus
})

# Register enhanced health endpoint
@app.get("/health", tags=["Health"])
async def health_check(request: Request):
    """Enhanced health check with service discovery."""
    return await enhanced_health_check(request)

# Service-specific health endpoint (legacy)
@app.get("/api/v1/trading/health", tags=["Health"])
async def trading_service_health():
    """Trading service specific health check."""
    return {
        "status": "healthy",
        "service": "trading",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": service_config.get("service_version", "1.0.0"),
        "capabilities": [
            "trade_execution",
            "position_management",
            "market_data",
            "risk_management",
            "trade_history"
        ],
        "external_dependencies": [
            "database",
            "redis",
            "event_bus"
        ]
    }


if __name__ == "__main__":
    import uvicorn
    
    # Use service config for server settings
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=service_config["service_port"],
        reload=service_config["environment"] == "development",
        log_level=service_config["log_level"].lower()
    )