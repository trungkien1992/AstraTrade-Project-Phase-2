"""
AstraTrade User Service - Containerized Microservice
Handles user management, authentication, and profile operations.
"""

import asyncio
import logging
from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import JSONResponse

# Import domain logic

from domains.user.entities import User
from domains.user.services import (
    UserManagementService, UserAuthenticationService,
    UserRepositoryInterface, SessionRepositoryInterface, PasswordServiceInterface
)
from domains.user.value_objects import Email, Username
# from domains.shared.events import UserRegistered, UserProfileUpdated  # TODO: Add specific user events

# Import base service components
from services.base import (
    create_app, 
    config, 
    get_database_session, 
    get_event_bus,
    start_heartbeat,
    metrics_collector,
    track_database_operation
)

# Configure logging
logger = logging.getLogger(__name__)

# Create FastAPI app
app = create_app(
    title="AstraTrade User Service",
    description="Microservice for user management and authentication",
    version="1.0.0"
)

# Simple mock implementations for MVP
class MockUserRepository(UserRepositoryInterface):
    def __init__(self):
        self.users = {}
    
    async def save(self, user): 
        self.users[str(user.user_id)] = user
        return user
    
    async def find_by_id(self, user_id):
        return self.users.get(str(user_id))
    
    async def find_by_email(self, email):
        for user in self.users.values():
            if user.profile.email == email:
                return user
        return None
    
    async def find_by_username(self, username):
        for user in self.users.values():
            if user.profile.username == username:
                return user
        return None
    
    async def delete(self, user_id):
        if str(user_id) in self.users:
            del self.users[str(user_id)]

class MockSessionRepository(SessionRepositoryInterface):
    def __init__(self):
        self.sessions = {}
    
    async def save(self, session):
        self.sessions[str(session.session_id)] = session
        return session
    
    async def find_by_id(self, session_id):
        return self.sessions.get(str(session_id))
    
    async def find_active_sessions(self, user_id):
        return [s for s in self.sessions.values() if s.user_id == user_id and s.is_active()]
    
    async def delete(self, session_id):
        if str(session_id) in self.sessions:
            del self.sessions[str(session_id)]

class MockPasswordService(PasswordServiceInterface):
    async def hash_password(self, password: str) -> str:
        return f"hashed_{password}"  # Simple mock hashing
    
    async def verify_password(self, password: str, hashed: str) -> bool:
        return hashed == f"hashed_{password}"

# User service instances
user_management_service = None
user_auth_service = None


@app.on_event("startup")
async def startup_event():
    """Initialize service on startup."""
    global user_management_service, user_auth_service
    
    logger.info("Starting User Service...")
    
    # Initialize repositories and services
    user_repo = MockUserRepository()
    session_repo = MockSessionRepository()
    password_service = MockPasswordService()
    
    # Initialize user services with dependencies
    user_management_service = UserManagementService(
        user_repository=user_repo,
        password_service=password_service
    )
    user_auth_service = UserAuthenticationService(
        user_repository=user_repo,
        session_repository=session_repo,
        password_service=password_service
    )
    
    # Start service registration heartbeat
    asyncio.create_task(start_heartbeat())
    
    logger.info("User Service started successfully")


# User Management Endpoints

@app.post("/api/v1/users/register", response_model=dict, tags=["Users"])
async def register_user(
    user_data: dict,
    db_session = Depends(get_database_session),
    event_bus = Depends(get_event_bus)
):
    """Register a new user."""
    try:
        # Extract user data
        username = user_data.get("username")
        email = user_data.get("email")
        password = user_data.get("password", "default_password")  # In production, would be hashed
        
        if not username or not email:
            raise HTTPException(status_code=400, detail="Username and email are required")
        
        # Create user entity
        user = User(
            username=Username(username),
            security_credentials=SecurityCredentials(hashed_password=password),
            email=Email(email)
        )
        
        # Register user (in production would interact with database)
        user_dict = {
            "id": user.user_id,
            "username": user.username.value,
            "email": user.email.address,
            "created_at": user.created_at.isoformat(),
            "is_active": user.is_active()
        }
        
        # Publish user registration event
        await event_bus.publish_event(
            "astra.user.user_registered.v1", 
            {
                "user_id": user.user_id,
                "username": user.username.value,
                "email": user.email.address,
                "registration_data": user_data
            }
        )
        
        # Record business metric
        metrics_collector.record_business_operation("user_registration", success=True)
        
        logger.info(f"User registered: {username}")
        
        return JSONResponse(
            status_code=201,
            content={
                "message": "User registered successfully",
                "user": user_dict
            }
        )
        
    except Exception as e:
        logger.error(f"Error registering user: {e}")
        metrics_collector.record_business_operation("user_registration", success=False)
        
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")


@app.get("/api/v1/users/{user_id}", response_model=dict, tags=["Users"])
@track_database_operation("get_user")
async def get_user_profile(
    user_id: str,
    db_session = Depends(get_database_session)
):
    """Get user profile by ID."""
    try:
        # In production, would query database
        user_profile = {
            "id": user_id,
            "username": f"user_{user_id[:8]}",
            "email": f"user_{user_id[:8]}@example.com",
            "profile_data": {
                "display_name": f"User {user_id[:8]}",
                "created_at": "2025-08-02T10:00:00Z",
                "last_login": "2025-08-02T12:00:00Z"
            },
            "is_active": True
        }
        
        metrics_collector.record_business_operation("get_user_profile", success=True)
        
        return user_profile
        
    except Exception as e:
        logger.error(f"Error getting user profile {user_id}: {e}")
        metrics_collector.record_business_operation("get_user_profile", success=False)
        
        raise HTTPException(status_code=404, detail="User not found")


@app.put("/api/v1/users/{user_id}", response_model=dict, tags=["Users"])
async def update_user_profile(
    user_id: str,
    profile_data: dict,
    db_session = Depends(get_database_session),
    event_bus = Depends(get_event_bus)
):
    """Update user profile."""
    try:
        # In production, would update database
        updated_profile = {
            "id": user_id,
            "username": profile_data.get("username", f"user_{user_id[:8]}"),
            "email": profile_data.get("email", f"user_{user_id[:8]}@example.com"),
            "profile_data": profile_data,
            "updated_at": "2025-08-02T12:30:00Z"
        }
        
        # Publish profile update event
        await event_bus.publish_event(
            "astra.user.profile_updated.v1",
            {
                "user_id": user_id,
                "updated_fields": list(profile_data.keys()),
                "profile_data": profile_data
            }
        )
        
        metrics_collector.record_business_operation("update_user_profile", success=True)
        
        logger.info(f"User profile updated: {user_id}")
        
        return {
            "message": "Profile updated successfully",
            "user": updated_profile
        }
        
    except Exception as e:
        logger.error(f"Error updating user profile {user_id}: {e}")
        metrics_collector.record_business_operation("update_user_profile", success=False)
        
        raise HTTPException(status_code=500, detail=f"Update failed: {str(e)}")


@app.get("/api/v1/users", response_model=dict, tags=["Users"])
@track_database_operation("list_users")
async def list_users(
    limit: int = 10,
    offset: int = 0,
    db_session = Depends(get_database_session)
):
    """List users with pagination."""
    try:
        # In production, would query database with pagination
        users = []
        for i in range(offset, min(offset + limit, offset + 5)):  # Mock 5 users
            users.append({
                "id": f"user-{i:04d}",
                "username": f"user_{i:04d}",
                "email": f"user_{i:04d}@example.com",
                "is_active": True,
                "created_at": "2025-08-02T10:00:00Z"
            })
        
        metrics_collector.record_business_operation("list_users", success=True)
        
        return {
            "users": users,
            "total": 100,  # Mock total
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        logger.error(f"Error listing users: {e}")
        metrics_collector.record_business_operation("list_users", success=False)
        
        raise HTTPException(status_code=500, detail=f"List failed: {str(e)}")


# User Authentication Endpoints

@app.post("/api/v1/users/login", response_model=dict, tags=["Authentication"])
async def login_user(
    credentials: dict,
    event_bus = Depends(get_event_bus)
):
    """User login."""
    try:
        username = credentials.get("username")
        password = credentials.get("password")
        
        if not username or not password:
            raise HTTPException(status_code=400, detail="Username and password required")
        
        # In production, would validate credentials
        user_session = {
            "user_id": f"user-{username}",
            "username": username,
            "token": f"token-{username}-{hash(password) % 10000:04d}",
            "expires_at": "2025-08-03T12:00:00Z"
        }
        
        # Publish login event
        await event_bus.publish_event(
            "astra.user.user_logged_in.v1",
            {
                "user_id": user_session["user_id"],
                "username": username,
                "login_timestamp": "2025-08-02T12:00:00Z"
            }
        )
        
        metrics_collector.record_business_operation("user_login", success=True)
        
        return {
            "message": "Login successful",
            "session": user_session
        }
        
    except Exception as e:
        logger.error(f"Error during login: {e}")
        metrics_collector.record_business_operation("user_login", success=False)
        
        raise HTTPException(status_code=401, detail="Invalid credentials")


# Service-specific health endpoint
@app.get("/api/v1/users/health", tags=["Health"])
async def user_service_health():
    """User service specific health check."""
    return {
        "status": "healthy",
        "service": "user",
        "timestamp": "2025-08-02T12:00:00Z",
        "version": config.service_version,
        "capabilities": [
            "user_registration",
            "user_authentication", 
            "profile_management",
            "user_listing"
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=config.service_host,
        port=config.service_port,
        reload=config.debug,
        log_level=config.log_level.lower()
    )