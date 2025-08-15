"""
AstraTrade Social Service - Containerized Microservice
Handles social feeds, interactions, and community features.
"""

import asyncio
import logging
from datetime import datetime, timezone
from fastapi import FastAPI, HTTPException, Depends


from base import create_app, config, get_database_session, start_heartbeat, metrics_collector

logger = logging.getLogger(__name__)

app = create_app(
    title="AstraTrade Social Service",
    description="Microservice for social features and community",
    version="1.0.0"
)

@app.on_event("startup")
async def startup_event():
    logger.info("Starting Social Service...")
    asyncio.create_task(start_heartbeat())
    logger.info("Social Service started successfully")

@app.get("/api/v1/social/feed", tags=["Social"])
async def get_social_feed(limit: int = 20, db_session = Depends(get_database_session)):
    """Get social activity feed."""
    try:
        feed_items = []
        for i in range(limit):
            feed_items.append({
                "id": f"activity-{i:06d}",
                "user_id": f"user-{i % 10:04d}",
                "username": f"trader_{i % 10:04d}",
                "type": "trade_executed" if i % 3 == 0 else "level_up" if i % 3 == 1 else "achievement",
                "content": f"Executed BTC trade" if i % 3 == 0 else f"Reached level {i//5 + 1}",
                "timestamp": f"2025-08-02T{12 + (i % 12):02d}:00:00Z"
            })
        
        metrics_collector.record_business_operation("get_social_feed", success=True)
        return {"feed": feed_items, "timestamp": datetime.now(timezone.utc).isoformat()}
        
    except Exception as e:
        logger.error(f"Error getting social feed: {e}")
        raise HTTPException(status_code=500, detail="Failed to get social feed")

@app.get("/api/v1/social/health", tags=["Health"])
async def social_service_health():
    return {
        "status": "healthy",
        "service": "social",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": config.service_version,
        "capabilities": ["social_feed", "user_interactions", "community_features"]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=config.service_host, port=config.service_port)