from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
import json
import base64
from io import BytesIO
from PIL import Image
import random

from ...core.database import get_db
from ...models.game_models import (
    User, ViralContent, FOMOEvent, FOMOEventParticipation, 
    UserGameStats, ConstellationMembership
)
from ...auth.auth import get_current_active_user as get_current_user

router = APIRouter(prefix="/viral", tags=["viral_content"])


# Pydantic models
class ViralContentResponse(BaseModel):
    id: int
    user_id: int
    content_type: str
    content_title: str
    content_description: Optional[str]
    content_data: Dict[str, Any]
    share_count: int
    viral_score: int
    engagement_rate: float
    platform_shares: Dict[str, int]
    template_id: Optional[str]
    trading_context: Optional[Dict[str, Any]]
    achievement_context: Optional[Dict[str, Any]]
    is_public: bool
    is_featured: bool
    moderation_status: str
    created_at: datetime
    last_shared_at: datetime
    
    class Config:
        from_attributes = True


class MemeGenerationRequest(BaseModel):
    meme_type: str = Field(..., regex=r"^(trading_win|trading_loss|milestone|streak|constellation|nft)$")
    template_id: Optional[str] = None
    custom_text: Optional[str] = Field(None, max_length=200)
    trading_data: Optional[Dict[str, Any]] = None
    achievement_data: Optional[Dict[str, Any]] = None


class ShareContentRequest(BaseModel):
    content_id: int
    platforms: List[str] = Field(..., min_items=1)
    custom_message: Optional[str] = Field(None, max_length=280)


class FOMOEventResponse(BaseModel):
    id: int
    event_name: str
    event_type: str
    description: str
    max_participants: Optional[int]
    participation_requirements: Dict[str, Any]
    reward_type: str
    reward_data: Dict[str, Any]
    start_time: datetime
    end_time: datetime
    urgency_level: int
    current_participants: int
    completion_threshold: Optional[int]
    is_active: bool
    is_completed: bool
    
    class Config:
        from_attributes = True


class FOMOEventParticipationResponse(BaseModel):
    id: int
    event_id: int
    user_id: int
    participation_score: float
    requirements_met: Dict[str, Any]
    reward_earned: bool
    reward_claimed: bool
    reward_data: Optional[Dict[str, Any]]
    joined_at: datetime
    completed_at: Optional[datetime]
    
    class Config:
        from_attributes = True


# Meme generation endpoints
@router.post("/memes/generate", response_model=ViralContentResponse)
async def generate_meme(
    request: MemeGenerationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate a personalized meme based on user's trading performance"""
    try:
        # Get user's game stats for context
        game_stats = db.query(UserGameStats).filter(
            UserGameStats.user_id == current_user.id
        ).first()
        
        if not game_stats:
            raise HTTPException(
                status_code=400,
                detail="No game statistics found. Complete some trades first."
            )
        
        # Generate meme content based on type
        meme_data = _generate_meme_content(
            request.meme_type,
            game_stats,
            request.trading_data,
            request.achievement_data,
            request.template_id
        )
        
        # Create viral content record
        viral_content = ViralContent(
            user_id=current_user.id,
            content_type="meme",
            content_title=meme_data["title"],
            content_description=meme_data.get("description"),
            content_data=meme_data,
            template_id=request.template_id,
            trading_context=request.trading_data,
            achievement_context=request.achievement_data,
            is_public=True,
            moderation_status="approved"
        )
        
        db.add(viral_content)
        db.commit()
        db.refresh(viral_content)
        
        return viral_content
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate meme: {str(e)}")


@router.get("/memes/templates")
async def get_meme_templates():
    """Get available meme templates"""
    templates = {
        "trading_win": [
            {
                "id": "cosmic_success",
                "name": "Cosmic Success",
                "description": "Celebrate your stellar gains",
                "image_url": "/templates/cosmic_success.png",
                "text_positions": [
                    {"x": 50, "y": 20, "max_length": 30},
                    {"x": 50, "y": 80, "max_length": 40}
                ]
            },
            {
                "id": "profit_explosion",
                "name": "Profit Explosion",
                "description": "When the gains hit different",
                "image_url": "/templates/profit_explosion.png",
                "text_positions": [
                    {"x": 50, "y": 15, "max_length": 25}
                ]
            }
        ],
        "trading_loss": [
            {
                "id": "learning_experience",
                "name": "Learning Experience",
                "description": "Every loss is a lesson",
                "image_url": "/templates/learning_experience.png",
                "text_positions": [
                    {"x": 50, "y": 25, "max_length": 35}
                ]
            }
        ],
        "milestone": [
            {
                "id": "level_up",
                "name": "Level Up",
                "description": "Achievement unlocked!",
                "image_url": "/templates/level_up.png",
                "text_positions": [
                    {"x": 50, "y": 30, "max_length": 20},
                    {"x": 50, "y": 70, "max_length": 30}
                ]
            }
        ],
        "streak": [
            {
                "id": "win_streak",
                "name": "Win Streak",
                "description": "Unstoppable trading machine",
                "image_url": "/templates/win_streak.png",
                "text_positions": [
                    {"x": 50, "y": 40, "max_length": 25}
                ]
            }
        ],
        "constellation": [
            {
                "id": "constellation_victory",
                "name": "Constellation Victory",
                "description": "Battle won!",
                "image_url": "/templates/constellation_victory.png",
                "text_positions": [
                    {"x": 50, "y": 20, "max_length": 30},
                    {"x": 50, "y": 80, "max_length": 35}
                ]
            }
        ]
    }
    
    return templates


@router.post("/memes/{meme_id}/share", response_model=Dict[str, Any])
async def share_meme(
    meme_id: int,
    request: ShareContentRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Share a meme to social platforms"""
    try:
        # Get meme content
        viral_content = db.query(ViralContent).filter(
            ViralContent.id == meme_id,
            ViralContent.user_id == current_user.id
        ).first()
        
        if not viral_content:
            raise HTTPException(status_code=404, detail="Meme not found")
        
        # Update share metrics
        for platform in request.platforms:
            current_shares = viral_content.platform_shares.get(platform, 0)
            viral_content.platform_shares[platform] = current_shares + 1
        
        viral_content.share_count += len(request.platforms)
        viral_content.viral_score += len(request.platforms) * 10  # 10 points per share
        viral_content.last_shared_at = datetime.utcnow()
        
        # Calculate engagement rate
        time_since_creation = datetime.utcnow() - viral_content.created_at
        hours_elapsed = max(1, time_since_creation.total_seconds() / 3600)
        viral_content.engagement_rate = viral_content.share_count / hours_elapsed
        
        db.commit()
        
        return {
            "message": "Meme shared successfully",
            "platforms": request.platforms,
            "new_share_count": viral_content.share_count,
            "viral_score": viral_content.viral_score
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to share meme: {str(e)}")


# Ecosystem snapshot endpoints
@router.post("/snapshots/create", response_model=ViralContentResponse)
async def create_ecosystem_snapshot(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a shareable ecosystem performance snapshot"""
    try:
        # Get user's comprehensive stats
        game_stats = db.query(UserGameStats).filter(
            UserGameStats.user_id == current_user.id
        ).first()
        
        constellation_membership = db.query(ConstellationMembership).filter(
            ConstellationMembership.user_id == current_user.id,
            ConstellationMembership.is_active == True
        ).first()
        
        if not game_stats:
            raise HTTPException(
                status_code=400,
                detail="No game statistics found"
            )
        
        # Create snapshot data
        snapshot_data = {
            "user_stats": {
                "username": current_user.username,
                "level": current_user.level,
                "xp": current_user.xp,
                "stellar_shards": game_stats.stellar_shards,
                "lumina": game_stats.lumina,
                "total_trades": game_stats.total_trades,
                "win_rate": (game_stats.successful_trades / max(1, game_stats.total_trades)) * 100,
                "current_streak": game_stats.current_streak,
                "best_streak": game_stats.best_streak
            },
            "constellation": {
                "name": constellation_membership.constellation.name if constellation_membership else None,
                "role": constellation_membership.role if constellation_membership else None,
                "contribution": constellation_membership.stellar_shards_contributed if constellation_membership else 0
            },
            "achievements": _get_user_achievements(game_stats, current_user),
            "snapshot_timestamp": datetime.utcnow().isoformat(),
            "snapshot_style": "cosmic_dashboard"
        }
        
        # Create viral content record
        viral_content = ViralContent(
            user_id=current_user.id,
            content_type="snapshot",
            content_title=f"{current_user.username}'s Cosmic Performance",
            content_description=f"Level {current_user.level} trader with {game_stats.stellar_shards:,.0f} SS",
            content_data=snapshot_data,
            is_public=True,
            moderation_status="approved"
        )
        
        db.add(viral_content)
        db.commit()
        db.refresh(viral_content)
        
        return viral_content
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create snapshot: {str(e)}")


# FOMO events endpoints
@router.get("/fomo-events", response_model=List[FOMOEventResponse])
async def get_active_fomo_events(
    limit: int = Query(10, ge=1, le=50),
    event_type: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get active FOMO events"""
    try:
        query = db.query(FOMOEvent).filter(
            FOMOEvent.is_active == True,
            FOMOEvent.start_time <= datetime.utcnow(),
            FOMOEvent.end_time > datetime.utcnow()
        )
        
        if event_type:
            query = query.filter(FOMOEvent.event_type == event_type)
        
        events = query.order_by(
            FOMOEvent.urgency_level.desc(),
            FOMOEvent.end_time.asc()
        ).limit(limit).all()
        
        return events
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get FOMO events: {str(e)}")


@router.post("/fomo-events/{event_id}/participate", response_model=FOMOEventParticipationResponse)
async def participate_in_fomo_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Participate in a FOMO event"""
    try:
        # Get event
        event = db.query(FOMOEvent).filter(
            FOMOEvent.id == event_id,
            FOMOEvent.is_active == True
        ).first()
        
        if not event:
            raise HTTPException(status_code=404, detail="FOMO event not found or inactive")
        
        # Check if event is still active
        now = datetime.utcnow()
        if now < event.start_time or now > event.end_time:
            raise HTTPException(status_code=400, detail="Event is not currently active")
        
        # Check if user already participating
        existing_participation = db.query(FOMOEventParticipation).filter(
            FOMOEventParticipation.event_id == event_id,
            FOMOEventParticipation.user_id == current_user.id
        ).first()
        
        if existing_participation:
            return existing_participation
        
        # Check participation requirements
        game_stats = db.query(UserGameStats).filter(
            UserGameStats.user_id == current_user.id
        ).first()
        
        requirements_met = _check_event_requirements(event, current_user, game_stats)
        
        if not requirements_met["eligible"]:
            raise HTTPException(
                status_code=400,
                detail=f"Requirements not met: {requirements_met['missing']}"
            )
        
        # Check max participants
        if event.max_participants and event.current_participants >= event.max_participants:
            raise HTTPException(status_code=400, detail="Event is full")
        
        # Create participation
        participation = FOMOEventParticipation(
            event_id=event_id,
            user_id=current_user.id,
            requirements_met=requirements_met["details"]
        )
        
        db.add(participation)
        
        # Update event participant count
        event.current_participants += 1
        
        db.commit()
        db.refresh(participation)
        
        return participation
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to participate in event: {str(e)}")


@router.get("/fomo-events/{event_id}/leaderboard")
async def get_fomo_event_leaderboard(
    event_id: int,
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get FOMO event participation leaderboard"""
    try:
        participations = db.query(FOMOEventParticipation, User).join(
            User, FOMOEventParticipation.user_id == User.id
        ).filter(
            FOMOEventParticipation.event_id == event_id
        ).order_by(
            FOMOEventParticipation.participation_score.desc()
        ).limit(limit).all()
        
        leaderboard = []
        for rank, (participation, user) in enumerate(participations, start=1):
            leaderboard.append({
                "rank": rank,
                "username": user.username,
                "participation_score": participation.participation_score,
                "reward_earned": participation.reward_earned,
                "joined_at": participation.joined_at
            })
        
        return leaderboard
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get leaderboard: {str(e)}")


# Social proof endpoints
@router.get("/social-proof")
async def get_social_proof_data(
    db: Session = Depends(get_db)
):
    """Get social proof data for viral features"""
    try:
        # Get trending content
        trending_content = db.query(ViralContent).filter(
            ViralContent.is_public == True,
            ViralContent.moderation_status == "approved",
            ViralContent.created_at >= datetime.utcnow() - timedelta(days=7)
        ).order_by(
            ViralContent.viral_score.desc()
        ).limit(10).all()
        
        # Get active FOMO events count
        active_fomo_count = db.query(FOMOEvent).filter(
            FOMOEvent.is_active == True,
            FOMOEvent.start_time <= datetime.utcnow(),
            FOMOEvent.end_time > datetime.utcnow()
        ).count()
        
        # Get recent achievements
        recent_achievements = _get_recent_community_achievements(db)
        
        return {
            "trending_content": [
                {
                    "id": content.id,
                    "title": content.content_title,
                    "viral_score": content.viral_score,
                    "share_count": content.share_count,
                    "content_type": content.content_type
                }
                for content in trending_content
            ],
            "active_fomo_events": active_fomo_count,
            "recent_achievements": recent_achievements,
            "total_shares_today": sum(content.share_count for content in trending_content),
            "viral_momentum": _calculate_viral_momentum(trending_content)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get social proof: {str(e)}")


# Content moderation endpoints
@router.get("/content/user", response_model=List[ViralContentResponse])
async def get_user_viral_content(
    content_type: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user's viral content"""
    try:
        query = db.query(ViralContent).filter(
            ViralContent.user_id == current_user.id
        )
        
        if content_type:
            query = query.filter(ViralContent.content_type == content_type)
        
        content = query.order_by(
            ViralContent.created_at.desc()
        ).limit(limit).all()
        
        return content
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get user content: {str(e)}")


# Helper functions
def _generate_meme_content(
    meme_type: str,
    game_stats: UserGameStats,
    trading_data: Optional[Dict],
    achievement_data: Optional[Dict],
    template_id: Optional[str]
) -> Dict[str, Any]:
    """Generate meme content based on type and user data"""
    
    base_templates = {
        "trading_win": {
            "title": f"Another W in the cosmic books! 📈",
            "description": f"Stellar Shards: +{random.randint(100, 1000)}",
            "template": template_id or "cosmic_success",
            "texts": [
                f"When you nail that perfect trade",
                f"+{game_stats.stellar_shards:,.0f} SS and counting! 🚀"
            ]
        },
        "trading_loss": {
            "title": "Learning experience unlocked 📚",
            "description": "Every loss teaches us something",
            "template": template_id or "learning_experience",
            "texts": [
                "That awkward moment when the market says no",
                "But we're still here, still trading! 💪"
            ]
        },
        "milestone": {
            "title": f"Level {game_stats.level} achieved! 🎯",
            "description": "Cosmic progression continues",
            "template": template_id or "level_up",
            "texts": [
                "LEVEL UP!",
                f"Now at Level {game_stats.level} with {game_stats.xp:,} XP"
            ]
        },
        "streak": {
            "title": f"{game_stats.current_streak} trade win streak! 🔥",
            "description": "Unstoppable trading machine",
            "template": template_id or "win_streak",
            "texts": [
                f"{game_stats.current_streak} wins in a row!"
            ]
        }
    }
    
    meme_content = base_templates.get(meme_type, base_templates["trading_win"])
    
    # Add user-specific data
    meme_content.update({
        "user_level": game_stats.level if game_stats else 1,
        "stellar_shards": game_stats.stellar_shards if game_stats else 0,
        "win_rate": (game_stats.successful_trades / max(1, game_stats.total_trades)) * 100 if game_stats else 0,
        "meme_type": meme_type,
        "generation_timestamp": datetime.utcnow().isoformat()
    })
    
    return meme_content


def _get_user_achievements(game_stats: UserGameStats, user: User) -> List[Dict[str, Any]]:
    """Get user achievements for snapshot"""
    achievements = []
    
    if game_stats.total_trades >= 100:
        achievements.append({"name": "Cosmic Trader", "icon": "star"})
    
    if game_stats.stellar_shards >= 50000:
        achievements.append({"name": "Stellar Collector", "icon": "diamond"})
    
    if game_stats.best_streak >= 10:
        achievements.append({"name": "Win Streak Master", "icon": "fire"})
    
    if user.level >= 25:
        achievements.append({"name": "Cosmic Veteran", "icon": "crown"})
    
    return achievements


def _check_event_requirements(
    event: FOMOEvent,
    user: User,
    game_stats: Optional[UserGameStats]
) -> Dict[str, Any]:
    """Check if user meets event requirements"""
    requirements = event.participation_requirements
    met_requirements = {}
    missing = []
    
    # Check level requirement
    if "min_level" in requirements:
        if user.level >= requirements["min_level"]:
            met_requirements["level"] = True
        else:
            met_requirements["level"] = False
            missing.append(f"Level {requirements['min_level']} required")
    
    # Check trades requirement
    if "min_trades" in requirements and game_stats:
        if game_stats.total_trades >= requirements["min_trades"]:
            met_requirements["trades"] = True
        else:
            met_requirements["trades"] = False
            missing.append(f"{requirements['min_trades']} trades required")
    
    # Check stellar shards requirement
    if "min_stellar_shards" in requirements and game_stats:
        if game_stats.stellar_shards >= requirements["min_stellar_shards"]:
            met_requirements["stellar_shards"] = True
        else:
            met_requirements["stellar_shards"] = False
            missing.append(f"{requirements['min_stellar_shards']} SS required")
    
    return {
        "eligible": len(missing) == 0,
        "details": met_requirements,
        "missing": missing
    }


def _get_recent_community_achievements(db: Session) -> List[Dict[str, Any]]:
    """Get recent community achievements"""
    # This would query recent significant achievements
    # For now, return mock data
    return [
        {
            "username": "CosmicTrader",
            "achievement": "Reached Level 50",
            "timestamp": datetime.utcnow() - timedelta(hours=2)
        },
        {
            "username": "StellarExplorer",
            "achievement": "100 Trade Win Streak",
            "timestamp": datetime.utcnow() - timedelta(hours=4)
        }
    ]


def _calculate_viral_momentum(content_list: List[ViralContent]) -> float:
    """Calculate viral momentum score"""
    if not content_list:
        return 0.0
    
    total_score = sum(content.viral_score for content in content_list)
    time_factor = len(content_list) / 7  # Normalize by week
    
    return min(100.0, total_score * time_factor / 100)