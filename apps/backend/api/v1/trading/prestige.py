from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel, Field

from ...core.database import get_db
from ...models.game_models import User, UserPrestige, UserGameStats, ConstellationMembership
from ...auth.auth import get_current_active_user as get_current_user

router = APIRouter(prefix="/prestige", tags=["prestige"])


# Pydantic models
class PrestigeResponse(BaseModel):
    id: int
    user_id: int
    is_verified: bool
    verification_tier: int
    verification_date: Optional[datetime]
    spotlight_eligible: bool
    aura_color: str
    custom_title: Optional[str]
    badge_collection: List[str]
    spotlight_count: int
    last_spotlight_date: Optional[datetime]
    spotlight_votes: int
    social_rating: float
    influence_score: float
    community_contributions: int
    
    class Config:
        from_attributes = True


class UserPrestigeProfile(BaseModel):
    user_id: int
    username: str
    level: int
    xp: int
    prestige: Optional[PrestigeResponse]
    stellar_shards: float
    lumina: float
    total_trades: int
    win_rate: float
    constellation_name: Optional[str]
    constellation_role: Optional[str]
    
    class Config:
        from_attributes = True


class LeaderboardEntry(BaseModel):
    rank: int
    user_id: int
    username: str
    level: int
    xp: int
    stellar_shards: float
    lumina: float
    total_trades: int
    win_rate: float
    is_verified: bool
    verification_tier: int
    aura_color: str
    custom_title: Optional[str]
    constellation_name: Optional[str]
    
    class Config:
        from_attributes = True


class VerificationRequest(BaseModel):
    trading_volume_proof: str = Field(..., min_length=10, max_length=500)
    social_media_handle: Optional[str] = Field(None, max_length=100)
    community_contributions: Optional[str] = Field(None, max_length=1000)


class CustomizationUpdate(BaseModel):
    custom_title: Optional[str] = Field(None, max_length=100)
    aura_color: Optional[str] = Field(None, regex=r"^#[0-9A-Fa-f]{6}$")


# Prestige system endpoints
@router.get("/profile/{user_id}", response_model=UserPrestigeProfile)
async def get_user_prestige_profile(
    user_id: int,
    db: Session = Depends(get_db)
):
    """Get user's prestige profile"""
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get user's game stats
    game_stats = db.query(UserGameStats).filter(
        UserGameStats.user_id == user_id
    ).first()
    
    # Get user's prestige info
    prestige = db.query(UserPrestige).filter(
        UserPrestige.user_id == user_id
    ).first()
    
    # Get constellation membership
    constellation_membership = db.query(ConstellationMembership).filter(
        ConstellationMembership.user_id == user_id,
        ConstellationMembership.is_active == True
    ).first()
    
    # Calculate win rate
    win_rate = 0.0
    if game_stats and game_stats.total_trades > 0:
        win_rate = (game_stats.successful_trades / game_stats.total_trades) * 100
    
    # Build response
    return UserPrestigeProfile(
        user_id=user.id,
        username=user.username,
        level=user.level,
        xp=user.xp,
        prestige=prestige,
        stellar_shards=game_stats.stellar_shards if game_stats else 0.0,
        lumina=game_stats.lumina if game_stats else 0.0,
        total_trades=game_stats.total_trades if game_stats else 0,
        win_rate=win_rate,
        constellation_name=constellation_membership.constellation.name if constellation_membership else None,
        constellation_role=constellation_membership.role if constellation_membership else None
    )


@router.get("/leaderboard/dual", response_model=List[LeaderboardEntry])
async def get_dual_leaderboard(
    leaderboard_type: str = Query("stellar_shards", regex=r"^(stellar_shards|lumina)$"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    verified_only: bool = Query(False),
    db: Session = Depends(get_db)
):
    """Get dual leaderboard (Stellar Shards or Lumina)"""
    # Base query joining necessary tables
    query = db.query(
        User, UserGameStats, UserPrestige, ConstellationMembership
    ).join(
        UserGameStats, User.id == UserGameStats.user_id
    ).outerjoin(
        UserPrestige, User.id == UserPrestige.user_id
    ).outerjoin(
        ConstellationMembership, 
        (User.id == ConstellationMembership.user_id) & 
        (ConstellationMembership.is_active == True)
    )
    
    # Filter verified users only if requested
    if verified_only:
        query = query.filter(UserPrestige.is_verified == True)
    
    # Sort by the requested metric
    if leaderboard_type == "stellar_shards":
        query = query.order_by(UserGameStats.stellar_shards.desc())
    else:  # lumina
        query = query.order_by(UserGameStats.lumina.desc())
    
    # Apply pagination
    results = query.offset(offset).limit(limit).all()
    
    # Build leaderboard entries
    leaderboard = []
    for rank, (user, game_stats, prestige, constellation_membership) in enumerate(results, start=offset + 1):
        win_rate = 0.0
        if game_stats.total_trades > 0:
            win_rate = (game_stats.successful_trades / game_stats.total_trades) * 100
        
        leaderboard.append(LeaderboardEntry(
            rank=rank,
            user_id=user.id,
            username=user.username,
            level=user.level,
            xp=user.xp,
            stellar_shards=game_stats.stellar_shards,
            lumina=game_stats.lumina,
            total_trades=game_stats.total_trades,
            win_rate=win_rate,
            is_verified=prestige.is_verified if prestige else False,
            verification_tier=prestige.verification_tier if prestige else 0,
            aura_color=prestige.aura_color if prestige else "#FFFFFF",
            custom_title=prestige.custom_title if prestige else None,
            constellation_name=constellation_membership.constellation.name if constellation_membership else None
        ))
    
    return leaderboard


@router.get("/spotlight", response_model=List[UserPrestigeProfile])
async def get_spotlight_users(
    limit: int = Query(10, ge=1, le=20),
    db: Session = Depends(get_db)
):
    """Get users currently in spotlight"""
    # Get users eligible for spotlight, prioritizing by various factors
    query = db.query(User, UserPrestige, UserGameStats).join(
        UserPrestige, User.id == UserPrestige.user_id
    ).join(
        UserGameStats, User.id == UserGameStats.user_id
    ).filter(
        UserPrestige.spotlight_eligible == True,
        UserPrestige.is_verified == True
    )
    
    # Complex sorting for spotlight worthiness
    # Priority: recent activity, high social rating, community contributions
    query = query.order_by(
        UserPrestige.social_rating.desc(),
        UserPrestige.influence_score.desc(),
        UserPrestige.community_contributions.desc(),
        UserGameStats.stellar_shards.desc()
    )
    
    results = query.limit(limit).all()
    
    # Build spotlight profiles
    spotlight_users = []
    for user, prestige, game_stats in results:
        constellation_membership = db.query(ConstellationMembership).filter(
            ConstellationMembership.user_id == user.id,
            ConstellationMembership.is_active == True
        ).first()
        
        win_rate = 0.0
        if game_stats.total_trades > 0:
            win_rate = (game_stats.successful_trades / game_stats.total_trades) * 100
        
        spotlight_users.append(UserPrestigeProfile(
            user_id=user.id,
            username=user.username,
            level=user.level,
            xp=user.xp,
            prestige=prestige,
            stellar_shards=game_stats.stellar_shards,
            lumina=game_stats.lumina,
            total_trades=game_stats.total_trades,
            win_rate=win_rate,
            constellation_name=constellation_membership.constellation.name if constellation_membership else None,
            constellation_role=constellation_membership.role if constellation_membership else None
        ))
    
    return spotlight_users


@router.post("/verify")
async def request_verification(
    verification_request: VerificationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Request user verification"""
    # Check if user already has prestige record
    prestige = db.query(UserPrestige).filter(
        UserPrestige.user_id == current_user.id
    ).first()
    
    if not prestige:
        # Create prestige record
        prestige = UserPrestige(
            user_id=current_user.id,
            is_verified=False,
            verification_tier=0
        )
        db.add(prestige)
        db.flush()
    
    if prestige.is_verified:
        raise HTTPException(
            status_code=400,
            detail="User is already verified"
        )
    
    # Get user's game stats for verification eligibility
    game_stats = db.query(UserGameStats).filter(
        UserGameStats.user_id == current_user.id
    ).first()
    
    if not game_stats:
        raise HTTPException(
            status_code=400,
            detail="No trading history found. Complete some trades first."
        )
    
    # Check minimum requirements for verification
    min_trades = 50
    min_stellar_shards = 10000
    min_win_rate = 0.6
    
    win_rate = game_stats.successful_trades / game_stats.total_trades if game_stats.total_trades > 0 else 0
    
    if (game_stats.total_trades < min_trades or 
        game_stats.stellar_shards < min_stellar_shards or 
        win_rate < min_win_rate):
        raise HTTPException(
            status_code=400,
            detail=f"Minimum requirements not met. Need: {min_trades} trades, {min_stellar_shards} SS, {min_win_rate*100}% win rate"
        )
    
    # Determine verification tier based on achievements
    verification_tier = 1  # Bronze
    if game_stats.total_trades >= 200 and game_stats.stellar_shards >= 50000:
        verification_tier = 2  # Silver
    if game_stats.total_trades >= 500 and game_stats.stellar_shards >= 100000 and win_rate >= 0.75:
        verification_tier = 3  # Gold
    
    # Update prestige record
    prestige.is_verified = True
    prestige.verification_tier = verification_tier
    prestige.verification_date = datetime.utcnow()
    prestige.spotlight_eligible = True
    
    # Set tier-specific aura colors
    aura_colors = {1: "#CD7F32", 2: "#C0C0C0", 3: "#FFD700"}  # Bronze, Silver, Gold
    prestige.aura_color = aura_colors.get(verification_tier, "#FFFFFF")
    
    # Calculate initial social rating
    prestige.social_rating = min(100.0, (win_rate * 50) + (game_stats.total_trades / 10))
    
    db.commit()
    
    return {
        "message": "Verification successful",
        "verification_tier": verification_tier,
        "aura_color": prestige.aura_color
    }


@router.post("/customize")
async def customize_profile(
    customization: CustomizationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Customize user profile appearance"""
    prestige = db.query(UserPrestige).filter(
        UserPrestige.user_id == current_user.id
    ).first()
    
    if not prestige:
        raise HTTPException(
            status_code=404,
            detail="User prestige profile not found. Complete verification first."
        )
    
    if not prestige.is_verified:
        raise HTTPException(
            status_code=403,
            detail="Only verified users can customize their profile"
        )
    
    # Update customization options
    if customization.custom_title is not None:
        prestige.custom_title = customization.custom_title
    
    if customization.aura_color is not None:
        # Only allow color changes for Gold tier users
        if prestige.verification_tier >= 3:
            prestige.aura_color = customization.aura_color
        else:
            raise HTTPException(
                status_code=403,
                detail="Only Gold tier verified users can customize aura color"
            )
    
    prestige.updated_at = datetime.utcnow()
    db.commit()
    
    return {"message": "Profile customization updated successfully"}


@router.post("/spotlight/vote/{user_id}")
async def vote_for_spotlight(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Vote for a user to be in spotlight"""
    if user_id == current_user.id:
        raise HTTPException(
            status_code=400,
            detail="Cannot vote for yourself"
        )
    
    target_prestige = db.query(UserPrestige).filter(
        UserPrestige.user_id == user_id
    ).first()
    
    if not target_prestige:
        raise HTTPException(
            status_code=404,
            detail="User prestige profile not found"
        )
    
    if not target_prestige.is_verified:
        raise HTTPException(
            status_code=400,
            detail="Can only vote for verified users"
        )
    
    # Check if voter is verified (verified users' votes count more)
    voter_prestige = db.query(UserPrestige).filter(
        UserPrestige.user_id == current_user.id
    ).first()
    
    vote_weight = 2 if voter_prestige and voter_prestige.is_verified else 1
    
    # Add vote
    target_prestige.spotlight_votes += vote_weight
    target_prestige.social_rating += 0.5 * vote_weight
    
    # Update spotlight eligibility based on votes
    if target_prestige.spotlight_votes >= 10:
        target_prestige.spotlight_eligible = True
    
    db.commit()
    
    return {"message": "Vote recorded successfully", "new_vote_count": target_prestige.spotlight_votes}


@router.get("/badges")
async def get_available_badges(
    db: Session = Depends(get_db)
):
    """Get list of available achievement badges"""
    badges = [
        {
            "id": "trading_novice",
            "name": "Trading Novice",
            "description": "Complete 10 trades",
            "requirements": {"total_trades": 10}
        },
        {
            "id": "stellar_collector",
            "name": "Stellar Collector",
            "description": "Accumulate 50,000 Stellar Shards",
            "requirements": {"stellar_shards": 50000}
        },
        {
            "id": "lumina_master",
            "name": "Lumina Master",
            "description": "Accumulate 10,000 Lumina",
            "requirements": {"lumina": 10000}
        },
        {
            "id": "win_streak_legend",
            "name": "Win Streak Legend",
            "description": "Achieve a 20-trade winning streak",
            "requirements": {"best_streak": 20}
        },
        {
            "id": "constellation_leader",
            "name": "Constellation Leader",
            "description": "Successfully lead a constellation",
            "requirements": {"constellation_owner": True}
        },
        {
            "id": "battle_champion",
            "name": "Battle Champion",
            "description": "Win 5 constellation battles",
            "requirements": {"battles_won": 5}
        },
        {
            "id": "social_influencer",
            "name": "Social Influencer",
            "description": "Achieve 75+ social rating",
            "requirements": {"social_rating": 75}
        },
        {
            "id": "verified_trader",
            "name": "Verified Trader",
            "description": "Achieve verified status",
            "requirements": {"is_verified": True}
        }
    ]
    
    return badges


@router.post("/update-social-metrics")
async def update_social_metrics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update user's social metrics based on recent activity"""
    prestige = db.query(UserPrestige).filter(
        UserPrestige.user_id == current_user.id
    ).first()
    
    if not prestige:
        # Create prestige record if it doesn't exist
        prestige = UserPrestige(user_id=current_user.id)
        db.add(prestige)
        db.flush()
    
    # Get recent activity data
    game_stats = db.query(UserGameStats).filter(
        UserGameStats.user_id == current_user.id
    ).first()
    
    if not game_stats:
        return {"message": "No game statistics found"}
    
    # Calculate influence score based on various factors
    influence_factors = {
        "trading_volume": min(50, game_stats.stellar_shards / 1000),
        "win_rate": (game_stats.successful_trades / max(1, game_stats.total_trades)) * 30,
        "consistency": min(20, game_stats.current_streak * 2),
        "verification_bonus": 10 if prestige.is_verified else 0
    }
    
    new_influence_score = sum(influence_factors.values())
    
    # Update metrics
    prestige.influence_score = new_influence_score
    prestige.social_rating = min(100.0, prestige.social_rating + (new_influence_score - prestige.influence_score) * 0.1)
    prestige.updated_at = datetime.utcnow()
    
    # Check for spotlight eligibility
    if prestige.social_rating >= 80 and prestige.is_verified:
        prestige.spotlight_eligible = True
    
    db.commit()
    
    return {
        "message": "Social metrics updated",
        "influence_score": prestige.influence_score,
        "social_rating": prestige.social_rating,
        "spotlight_eligible": prestige.spotlight_eligible
    }