"""
AstraTrade NFT Service - Containerized Microservice
Handles NFT rewards, marketplace, and blockchain integration.
"""

import asyncio
import logging
from datetime import datetime, timezone
from fastapi import FastAPI, HTTPException, Depends


from base import create_app, config, get_database_session, start_heartbeat, metrics_collector

logger = logging.getLogger(__name__)

app = create_app(
    title="AstraTrade NFT Service",
    description="Microservice for NFT rewards and marketplace",
    version="1.0.0"
)

@app.on_event("startup")
async def startup_event():
    logger.info("Starting NFT Service...")
    asyncio.create_task(start_heartbeat())
    logger.info("NFT Service started successfully")

@app.get("/api/v1/nft/user/{user_id}/rewards", tags=["NFT"])
async def get_user_nft_rewards(user_id: str, db_session = Depends(get_database_session)):
    """Get user's NFT rewards and eligibility."""
    try:
        nft_data = {
            "user_id": user_id,
            "eligible_rewards": [
                {"type": "bronze_trader", "level_required": 5, "earned": True},
                {"type": "silver_trader", "level_required": 10, "earned": False}
            ],
            "owned_nfts": [
                {"id": "nft-001", "type": "bronze_trader", "minted_at": "2025-08-01T10:00:00Z"}
            ],
            "marketplace_value": 150.00,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        metrics_collector.record_business_operation("get_nft_rewards", success=True)
        return nft_data
        
    except Exception as e:
        logger.error(f"Error getting NFT rewards for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get NFT rewards")

@app.get("/api/v1/nft/health", tags=["Health"])
async def nft_service_health():
    return {
        "status": "healthy",
        "service": "nft",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": config.service_version,
        "capabilities": ["nft_rewards", "marketplace", "blockchain_integration"]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=config.service_host, port=config.service_port)