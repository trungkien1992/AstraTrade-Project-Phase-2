"""
AstraTrade Gamification Service - Containerized Microservice
Handles XP, achievements, leaderboards, and game mechanics.
"""

import asyncio
import logging
from datetime import datetime, timezone
from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import JSONResponse


from base import (
    create_app, config, get_database_session, get_event_bus,
    start_heartbeat, metrics_collector, track_database_operation
)

logger = logging.getLogger(__name__)

app = create_app(
    title="AstraTrade Gamification Service",
    description="Microservice for XP, achievements, and leaderboards",
    version="1.0.0"
)

@app.on_event("startup")
async def startup_event():
    logger.info("Starting Gamification Service...")
    
    # Start event consumer for trading events
    asyncio.create_task(start_event_consumer())
    asyncio.create_task(start_heartbeat())
    
    logger.info("Gamification Service started successfully")

async def start_event_consumer():
    """Start consuming trading events to award XP."""
    event_bus = None  # Would get from dependencies
    
    # Mock event consumer - in production would listen to Redis Streams
    logger.info("Started gamification event consumer")

@app.get("/api/v1/gamification/user/{user_id}/xp", tags=["XP"])
@track_database_operation("get_user_xp")
async def get_user_xp(user_id: str, db_session = Depends(get_database_session)):
    """Get user XP and level."""
    try:
        # Mock XP calculation
        base_xp = hash(user_id) % 10000
        xp_data = {
            "user_id": user_id,
            "total_xp": base_xp,
            "level": base_xp // 500 + 1,
            "xp_to_next_level": 500 - (base_xp % 500),
            "last_updated": datetime.now(timezone.utc).isoformat()
        }
        
        metrics_collector.record_business_operation("get_user_xp", success=True)
        return xp_data
        
    except Exception as e:
        logger.error(f"Error getting XP for user {user_id}: {e}")
        metrics_collector.record_business_operation("get_user_xp", success=False)
        raise HTTPException(status_code=500, detail="Failed to get XP")

@app.get("/api/v1/gamification/leaderboard", tags=["Leaderboard"])
@track_database_operation("get_leaderboard")
async def get_leaderboard(limit: int = 10, db_session = Depends(get_database_session)):
    """Get XP leaderboard."""
    try:
        leaderboard = []
        for i in range(limit):
            leaderboard.append({
                "rank": i + 1,
                "user_id": f"user-{i:04d}",
                "username": f"trader_{i:04d}",
                "total_xp": 10000 - (i * 200),
                "level": (10000 - (i * 200)) // 500 + 1
            })
        
        metrics_collector.record_business_operation("get_leaderboard", success=True)
        return {"leaderboard": leaderboard, "timestamp": datetime.now(timezone.utc).isoformat()}
        
    except Exception as e:
        logger.error(f"Error getting leaderboard: {e}")
        metrics_collector.record_business_operation("get_leaderboard", success=False)
        raise HTTPException(status_code=500, detail="Failed to get leaderboard")

@app.get("/api/v1/gamification/health", tags=["Health"])
async def gamification_service_health():
    return {
        "status": "healthy",
        "service": "gamification",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": config.service_version,
        "capabilities": ["xp_management", "leaderboards", "achievements"]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=config.service_host, port=config.service_port)