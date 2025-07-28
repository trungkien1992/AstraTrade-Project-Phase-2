#!/usr/bin/env python3
"""
Simple backend server for AstraTrade running on port 8000
This provides the health check endpoint and basic API functionality needed by the frontend
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import uvicorn

app = FastAPI(title="AstraTrade Backend API", version="1.0.0")

# CORS middleware to allow frontend connections
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    """Health check endpoint - this is what the frontend is looking for"""
    return {
        "status": "ok", 
        "service": "astratrade-backend",
        "timestamp": datetime.utcnow().isoformat(),
        "port": 8000
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AstraTrade Backend API is running on port 8000!",
        "status": "active",
        "endpoints": {
            "health": "/health",
            "api_docs": "/docs",
            "openapi": "/openapi.json"
        }
    }

@app.get("/api/v1/status")
async def api_status():
    """API status endpoint"""
    return {
        "api_version": "v1",
        "status": "operational",
        "timestamp": datetime.utcnow().isoformat()
    }

if __name__ == "__main__":
    print("🚀 Starting AstraTrade Backend on port 8000...")
    print("📊 Health check available at: http://localhost:8000/health")
    print("📖 API docs available at: http://localhost:8000/docs")
    
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        log_level="info"
    )