from fastapi import FastAPI, HTTPException, status, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import timedelta, datetime
from sqlalchemy.orm import Session

from core.database import (
    get_db,
    create_tables,
    User as DBUser,
    Trade as DBTrade,
)
from auth.auth import (
    authenticate_user,
    create_access_token,
    get_current_active_user,
    get_password_hash,
)
from core.config import settings

app = FastAPI(title="AstraTrade Backend API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create tables on startup
@app.on_event("startup")
async def startup_event():
    create_tables()

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

class LeaderboardEntry(BaseModel):
    user_id: int
    username: str
    xp: int
    level: int

    model_config = {"from_attributes": True}

# --- Endpoints ---
@app.post("/register", summary="Register a new user", response_model=UserResponse)
async def register_user(req: UserRegisterRequest, db: Session = Depends(get_db)):
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

@app.get("/leaderboard", summary="Get leaderboard", response_model=List[LeaderboardEntry])
async def get_leaderboard(db: Session = Depends(get_db)):
    users = db.query(DBUser).order_by(DBUser.xp.desc()).limit(100).all()
    return [
        LeaderboardEntry(
            user_id=user.id, username=user.username, xp=user.xp, level=user.level
        )
        for user in users
    ]

@app.get("/health", summary="Health check endpoint")
async def health_check():
    return {"status": "ok", "timestamp": datetime.utcnow()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)