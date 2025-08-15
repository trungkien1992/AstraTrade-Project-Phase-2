"""
AstraTrade Financial Service - Containerized Microservice
Handles revenue tracking, subscriptions, and financial analytics.
"""

import asyncio
import logging
from datetime import datetime, timezone
from fastapi import FastAPI, HTTPException, Depends


from base import create_app, config, get_database_session, start_heartbeat, metrics_collector

logger = logging.getLogger(__name__)

app = create_app(
    title="AstraTrade Financial Service", 
    description="Microservice for financial tracking and analytics",
    version="1.0.0"
)

@app.on_event("startup")
async def startup_event():
    logger.info("Starting Financial Service...")
    asyncio.create_task(start_heartbeat())
    logger.info("Financial Service started successfully")

@app.get("/api/v1/financial/revenue", tags=["Financial"])
async def get_revenue_data(period: str = "daily", db_session = Depends(get_database_session)):
    """Get revenue analytics data."""
    try:
        revenue_data = {
            "period": period,
            "total_revenue": 125000.50,
            "trading_fees": 85000.25,
            "subscription_revenue": 40000.25,
            "growth_rate": 15.5,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        metrics_collector.record_business_operation("get_revenue_data", success=True)
        return revenue_data
        
    except Exception as e:
        logger.error(f"Error getting revenue data: {e}")
        raise HTTPException(status_code=500, detail="Failed to get revenue data")

@app.get("/api/v1/financial/health", tags=["Health"])
async def financial_service_health():
    return {
        "status": "healthy",
        "service": "financial",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": config.service_version,
        "capabilities": ["revenue_tracking", "subscription_management", "financial_analytics"]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=config.service_host, port=config.service_port)