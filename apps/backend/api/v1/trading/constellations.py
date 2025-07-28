from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel, Field

from ...core.database import get_db
from ...models.game_models import (
    Constellation, ConstellationMembership, ConstellationBattle, 
    ConstellationBattleParticipation, User, UserPrestige
)
from ...auth.auth import get_current_active_user as get_current_user
from ...services.clan_trading_service import (
    clan_trading_service, start_battle_monitoring, 
    get_real_time_battle_scores, get_clan_trading_performance
)
from ...tasks.clan_battle_monitor import trigger_battle_update, get_monitor_status

router = APIRouter(prefix="/constellations", tags=["constellations"])


# Pydantic models for request/response
class ConstellationCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = Field(None, max_length=1000)
    constellation_color: str = Field("#7B2CBF", regex=r"^#[0-9A-Fa-f]{6}$")
    constellation_emblem: str = Field("star", max_length=50)
    is_public: bool = True
    max_members: int = Field(50, ge=5, le=200)


class ConstellationUpdate(BaseModel):
    description: Optional[str] = Field(None, max_length=1000)
    constellation_color: Optional[str] = Field(None, regex=r"^#[0-9A-Fa-f]{6}$")
    constellation_emblem: Optional[str] = Field(None, max_length=50)
    is_public: Optional[bool] = None
    max_members: Optional[int] = Field(None, ge=5, le=200)


class ConstellationResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    owner_id: int
    member_count: int
    total_stellar_shards: float
    total_lumina: float
    constellation_level: int
    constellation_color: str
    constellation_emblem: str
    is_public: bool
    max_members: int
    total_battles: int
    battles_won: int
    battle_rating: float
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ConstellationMemberResponse(BaseModel):
    id: int
    user_id: int
    username: str
    role: str
    contribution_score: int
    stellar_shards_contributed: float
    lumina_contributed: float
    battles_participated: int
    joined_at: datetime
    last_active_at: datetime
    
    class Config:
        from_attributes = True


class ConstellationBattleCreate(BaseModel):
    defender_constellation_id: int
    battle_type: str = Field(..., regex=r"^(trading_duel|stellar_supremacy|cosmic_conquest)$")
    duration_hours: int = Field(24, ge=1, le=168)  # 1 hour to 1 week
    prize_pool: float = Field(0.0, ge=0.0)


class ConstellationBattleResponse(BaseModel):
    id: int
    challenger_constellation_id: int
    defender_constellation_id: int
    battle_type: str
    duration_hours: int
    status: str
    winner_constellation_id: Optional[int]
    challenger_score: float
    defender_score: float
    total_participants: int
    prize_pool: float
    winner_reward: float
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    
    class Config:
        from_attributes = True


# Constellation CRUD endpoints
@router.post("/", response_model=ConstellationResponse)
async def create_constellation(
    constellation: ConstellationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new constellation"""
    # Check if user already owns a constellation
    existing_constellation = db.query(Constellation).filter(
        Constellation.owner_id == current_user.id
    ).first()
    
    if existing_constellation:
        raise HTTPException(
            status_code=400,
            detail="User already owns a constellation. Each user can only own one constellation."
        )
    
    # Check if constellation name is unique
    name_exists = db.query(Constellation).filter(
        Constellation.name == constellation.name
    ).first()
    
    if name_exists:
        raise HTTPException(
            status_code=400,
            detail="Constellation name already exists. Please choose a different name."
        )
    
    # Create constellation
    db_constellation = Constellation(
        name=constellation.name,
        description=constellation.description,
        owner_id=current_user.id,
        constellation_color=constellation.constellation_color,
        constellation_emblem=constellation.constellation_emblem,
        is_public=constellation.is_public,
        max_members=constellation.max_members,
        member_count=1  # Owner is automatically a member
    )
    
    db.add(db_constellation)
    db.flush()  # Get the constellation ID
    
    # Create owner membership
    owner_membership = ConstellationMembership(
        constellation_id=db_constellation.id,
        user_id=current_user.id,
        role="owner",
        contribution_score=0
    )
    
    db.add(owner_membership)
    db.commit()
    db.refresh(db_constellation)
    
    return db_constellation


@router.get("/", response_model=List[ConstellationResponse])
async def list_constellations(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    search: Optional[str] = Query(None, min_length=1, max_length=100),
    sort_by: str = Query("created_at", regex=r"^(name|member_count|constellation_level|battle_rating|created_at)$"),
    sort_order: str = Query("desc", regex=r"^(asc|desc)$"),
    db: Session = Depends(get_db)
):
    """List all public constellations with search and sorting"""
    query = db.query(Constellation).filter(Constellation.is_public == True)
    
    # Apply search filter
    if search:
        query = query.filter(
            Constellation.name.ilike(f"%{search}%") | 
            Constellation.description.ilike(f"%{search}%")
        )
    
    # Apply sorting
    if sort_order == "asc":
        query = query.order_by(getattr(Constellation, sort_by).asc())
    else:
        query = query.order_by(getattr(Constellation, sort_by).desc())
    
    # Apply pagination
    constellations = query.offset(skip).limit(limit).all()
    
    return constellations


@router.get("/{constellation_id}", response_model=ConstellationResponse)
async def get_constellation(
    constellation_id: int,
    db: Session = Depends(get_db)
):
    """Get constellation details by ID"""
    constellation = db.query(Constellation).filter(
        Constellation.id == constellation_id
    ).first()
    
    if not constellation:
        raise HTTPException(status_code=404, detail="Constellation not found")
    
    if not constellation.is_public:
        raise HTTPException(
            status_code=403,
            detail="This constellation is private"
        )
    
    return constellation


@router.put("/{constellation_id}", response_model=ConstellationResponse)
async def update_constellation(
    constellation_id: int,
    constellation_update: ConstellationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update constellation details (owner only)"""
    constellation = db.query(Constellation).filter(
        Constellation.id == constellation_id
    ).first()
    
    if not constellation:
        raise HTTPException(status_code=404, detail="Constellation not found")
    
    if constellation.owner_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Only the constellation owner can update details"
        )
    
    # Update fields
    update_data = constellation_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(constellation, field, value)
    
    constellation.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(constellation)
    
    return constellation


# Constellation membership endpoints
@router.post("/{constellation_id}/join")
async def join_constellation(
    constellation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Join a constellation"""
    constellation = db.query(Constellation).filter(
        Constellation.id == constellation_id
    ).first()
    
    if not constellation:
        raise HTTPException(status_code=404, detail="Constellation not found")
    
    if not constellation.is_public:
        raise HTTPException(
            status_code=403,
            detail="This constellation is private and requires an invitation"
        )
    
    # Check if user is already a member
    existing_membership = db.query(ConstellationMembership).filter(
        ConstellationMembership.constellation_id == constellation_id,
        ConstellationMembership.user_id == current_user.id,
        ConstellationMembership.is_active == True
    ).first()
    
    if existing_membership:
        raise HTTPException(
            status_code=400,
            detail="User is already a member of this constellation"
        )
    
    # Check if constellation is full
    if constellation.member_count >= constellation.max_members:
        raise HTTPException(
            status_code=400,
            detail="Constellation is full. Cannot join at this time."
        )
    
    # Check if user is already in another constellation
    current_membership = db.query(ConstellationMembership).filter(
        ConstellationMembership.user_id == current_user.id,
        ConstellationMembership.is_active == True
    ).first()
    
    if current_membership:
        raise HTTPException(
            status_code=400,
            detail="User is already a member of another constellation. Leave current constellation first."
        )
    
    # Create membership
    membership = ConstellationMembership(
        constellation_id=constellation_id,
        user_id=current_user.id,
        role="member"
    )
    
    db.add(membership)
    
    # Update constellation member count
    constellation.member_count += 1
    constellation.updated_at = datetime.utcnow()
    
    db.commit()
    
    return {"message": "Successfully joined constellation", "constellation_id": constellation_id}


@router.post("/{constellation_id}/leave")
async def leave_constellation(
    constellation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Leave a constellation"""
    membership = db.query(ConstellationMembership).filter(
        ConstellationMembership.constellation_id == constellation_id,
        ConstellationMembership.user_id == current_user.id,
        ConstellationMembership.is_active == True
    ).first()
    
    if not membership:
        raise HTTPException(
            status_code=404,
            detail="User is not a member of this constellation"
        )
    
    constellation = db.query(Constellation).filter(
        Constellation.id == constellation_id
    ).first()
    
    if membership.role == "owner":
        raise HTTPException(
            status_code=400,
            detail="Constellation owner cannot leave. Transfer ownership or delete constellation first."
        )
    
    # Deactivate membership
    membership.is_active = False
    
    # Update constellation member count
    constellation.member_count -= 1
    constellation.updated_at = datetime.utcnow()
    
    db.commit()
    
    return {"message": "Successfully left constellation"}


@router.get("/{constellation_id}/members", response_model=List[ConstellationMemberResponse])
async def get_constellation_members(
    constellation_id: int,
    db: Session = Depends(get_db)
):
    """Get all members of a constellation"""
    constellation = db.query(Constellation).filter(
        Constellation.id == constellation_id
    ).first()
    
    if not constellation:
        raise HTTPException(status_code=404, detail="Constellation not found")
    
    if not constellation.is_public:
        raise HTTPException(
            status_code=403,
            detail="This constellation is private"
        )
    
    members = db.query(ConstellationMembership, User).join(
        User, ConstellationMembership.user_id == User.id
    ).filter(
        ConstellationMembership.constellation_id == constellation_id,
        ConstellationMembership.is_active == True
    ).all()
    
    # Format response
    member_responses = []
    for membership, user in members:
        member_responses.append(ConstellationMemberResponse(
            id=membership.id,
            user_id=user.id,
            username=user.username,
            role=membership.role,
            contribution_score=membership.contribution_score,
            stellar_shards_contributed=membership.stellar_shards_contributed,
            lumina_contributed=membership.lumina_contributed,
            battles_participated=membership.battles_participated,
            joined_at=membership.joined_at,
            last_active_at=membership.last_active_at
        ))
    
    return member_responses


# Constellation battle endpoints
@router.post("/{constellation_id}/battles", response_model=ConstellationBattleResponse)
async def create_constellation_battle(
    constellation_id: int,
    battle: ConstellationBattleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new constellation battle (challenge another constellation)"""
    # Verify user is member of challenger constellation
    challenger_membership = db.query(ConstellationMembership).filter(
        ConstellationMembership.constellation_id == constellation_id,
        ConstellationMembership.user_id == current_user.id,
        ConstellationMembership.is_active == True
    ).first()
    
    if not challenger_membership:
        raise HTTPException(
            status_code=403,
            detail="User is not a member of this constellation"
        )
    
    if challenger_membership.role not in ["owner", "admin"]:
        raise HTTPException(
            status_code=403,
            detail="Only constellation owners and admins can create battles"
        )
    
    # Verify defender constellation exists
    defender_constellation = db.query(Constellation).filter(
        Constellation.id == battle.defender_constellation_id
    ).first()
    
    if not defender_constellation:
        raise HTTPException(
            status_code=404,
            detail="Defender constellation not found"
        )
    
    if battle.defender_constellation_id == constellation_id:
        raise HTTPException(
            status_code=400,
            detail="Cannot challenge your own constellation"
        )
    
    # Check for existing active battles
    existing_battle = db.query(ConstellationBattle).filter(
        ConstellationBattle.challenger_constellation_id == constellation_id,
        ConstellationBattle.defender_constellation_id == battle.defender_constellation_id,
        ConstellationBattle.status.in_(["pending", "active"])
    ).first()
    
    if existing_battle:
        raise HTTPException(
            status_code=400,
            detail="There is already an active battle between these constellations"
        )
    
    # Create battle
    db_battle = ConstellationBattle(
        challenger_constellation_id=constellation_id,
        defender_constellation_id=battle.defender_constellation_id,
        battle_type=battle.battle_type,
        duration_hours=battle.duration_hours,
        prize_pool=battle.prize_pool
    )
    
    db.add(db_battle)
    db.commit()
    db.refresh(db_battle)
    
    return db_battle


@router.get("/{constellation_id}/battles", response_model=List[ConstellationBattleResponse])
async def get_constellation_battles(
    constellation_id: int,
    status: Optional[str] = Query(None, regex=r"^(pending|active|completed|cancelled)$"),
    db: Session = Depends(get_db)
):
    """Get battles for a constellation"""
    constellation = db.query(Constellation).filter(
        Constellation.id == constellation_id
    ).first()
    
    if not constellation:
        raise HTTPException(status_code=404, detail="Constellation not found")
    
    query = db.query(ConstellationBattle).filter(
        (ConstellationBattle.challenger_constellation_id == constellation_id) |
        (ConstellationBattle.defender_constellation_id == constellation_id)
    )
    
    if status:
        query = query.filter(ConstellationBattle.status == status)
    
    battles = query.order_by(ConstellationBattle.created_at.desc()).all()
    
    return battles


@router.post("/battles/{battle_id}/join")
async def join_constellation_battle(
    battle_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Join a constellation battle"""
    battle = db.query(ConstellationBattle).filter(
        ConstellationBattle.id == battle_id
    ).first()
    
    if not battle:
        raise HTTPException(status_code=404, detail="Battle not found")
    
    if battle.status != "active":
        raise HTTPException(
            status_code=400,
            detail="Battle is not active. Cannot join at this time."
        )
    
    # Check if user is member of either constellation
    membership = db.query(ConstellationMembership).filter(
        ConstellationMembership.user_id == current_user.id,
        ConstellationMembership.constellation_id.in_([
            battle.challenger_constellation_id,
            battle.defender_constellation_id
        ]),
        ConstellationMembership.is_active == True
    ).first()
    
    if not membership:
        raise HTTPException(
            status_code=403,
            detail="User is not a member of either constellation in this battle"
        )
    
    # Check if user is already participating
    existing_participation = db.query(ConstellationBattleParticipation).filter(
        ConstellationBattleParticipation.battle_id == battle_id,
        ConstellationBattleParticipation.user_id == current_user.id
    ).first()
    
    if existing_participation:
        raise HTTPException(
            status_code=400,
            detail="User is already participating in this battle"
        )
    
    # Create participation
    participation = ConstellationBattleParticipation(
        battle_id=battle_id,
        user_id=current_user.id,
        constellation_id=membership.constellation_id
    )
    
    db.add(participation)
    
    # Update battle participant count
    battle.total_participants += 1
    
    db.commit()
    
    return {"message": "Successfully joined battle", "battle_id": battle_id}


@router.post("/battles/{battle_id}/start")
async def start_constellation_battle(
    battle_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Start a constellation battle (defender must accept)"""
    battle = db.query(ConstellationBattle).filter(
        ConstellationBattle.id == battle_id
    ).first()
    
    if not battle:
        raise HTTPException(status_code=404, detail="Battle not found")
    
    if battle.status != "pending":
        raise HTTPException(
            status_code=400,
            detail="Battle cannot be started. Current status: " + battle.status
        )
    
    # Check if user is admin/owner of defender constellation
    defender_membership = db.query(ConstellationMembership).filter(
        ConstellationMembership.constellation_id == battle.defender_constellation_id,
        ConstellationMembership.user_id == current_user.id,
        ConstellationMembership.role.in_(["owner", "admin"]),
        ConstellationMembership.is_active == True
    ).first()
    
    if not defender_membership:
        raise HTTPException(
            status_code=403,
            detail="Only defender constellation owners/admins can start battles"
        )
    
    # Start the battle
    battle.status = "active"
    battle.started_at = datetime.utcnow()
    
    db.commit()
    
    return {"message": "Battle started successfully", "battle_id": battle_id}


@router.post("/battles/{battle_id}/update-score")
async def update_battle_score(
    battle_id: int,
    trading_score: float,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update user's battle score based on trading activity"""
    battle = db.query(ConstellationBattle).filter(
        ConstellationBattle.id == battle_id
    ).first()
    
    if not battle:
        raise HTTPException(status_code=404, detail="Battle not found")
    
    if battle.status != "active":
        raise HTTPException(
            status_code=400,
            detail="Battle is not active. Cannot update scores."
        )
    
    # Check if battle has ended due to time
    if battle.started_at:
        end_time = battle.started_at + timedelta(hours=battle.duration_hours)
        if datetime.utcnow() > end_time:
            # Auto-complete the battle
            await _complete_battle(battle, db)
            raise HTTPException(
                status_code=400,
                detail="Battle has ended. Cannot update scores."
            )
    
    # Get user participation
    participation = db.query(ConstellationBattleParticipation).filter(
        ConstellationBattleParticipation.battle_id == battle_id,
        ConstellationBattleParticipation.user_id == current_user.id
    ).first()
    
    if not participation:
        raise HTTPException(
            status_code=403,
            detail="User is not participating in this battle"
        )
    
    # Update participation score
    participation.individual_score += trading_score
    participation.trades_completed += 1
    participation.stellar_shards_earned += trading_score * 0.1  # 10% conversion
    participation.last_activity_at = datetime.utcnow()
    
    # Update constellation scores
    if participation.constellation_id == battle.challenger_constellation_id:
        battle.challenger_score += trading_score
    else:
        battle.defender_score += trading_score
    
    db.commit()
    
    return {
        "message": "Score updated successfully", 
        "new_individual_score": participation.individual_score,
        "new_constellation_score": battle.challenger_score if participation.constellation_id == battle.challenger_constellation_id else battle.defender_score
    }


@router.post("/battles/{battle_id}/complete")
async def complete_constellation_battle(
    battle_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Manually complete a constellation battle (admin only)"""
    battle = db.query(ConstellationBattle).filter(
        ConstellationBattle.id == battle_id
    ).first()
    
    if not battle:
        raise HTTPException(status_code=404, detail="Battle not found")
    
    if battle.status != "active":
        raise HTTPException(
            status_code=400,
            detail="Battle is not active. Cannot complete."
        )
    
    # Check if user is admin/owner of either constellation
    membership = db.query(ConstellationMembership).filter(
        ConstellationMembership.user_id == current_user.id,
        ConstellationMembership.constellation_id.in_([
            battle.challenger_constellation_id,
            battle.defender_constellation_id
        ]),
        ConstellationMembership.role.in_(["owner", "admin"]),
        ConstellationMembership.is_active == True
    ).first()
    
    if not membership:
        raise HTTPException(
            status_code=403,
            detail="Only constellation owners/admins can complete battles"
        )
    
    # Complete the battle
    await _complete_battle(battle, db)
    
    return {"message": "Battle completed successfully", "winner_id": battle.winner_constellation_id}


async def _complete_battle(battle: ConstellationBattle, db: Session):
    """Internal function to complete a battle and distribute rewards"""
    # Determine winner
    if battle.challenger_score > battle.defender_score:
        battle.winner_constellation_id = battle.challenger_constellation_id
    elif battle.defender_score > battle.challenger_score:
        battle.winner_constellation_id = battle.defender_constellation_id
    # If tied, no winner
    
    battle.status = "completed"
    battle.completed_at = datetime.utcnow()
    
    # Calculate rewards
    if battle.winner_constellation_id:
        battle.winner_reward = battle.prize_pool * 0.8  # 80% to winner
        loser_reward = battle.prize_pool * 0.2  # 20% to loser
    else:
        battle.winner_reward = battle.prize_pool * 0.5  # 50% each if tied
        loser_reward = battle.prize_pool * 0.5
    
    # Update constellation battle statistics
    challenger_constellation = db.query(Constellation).filter(
        Constellation.id == battle.challenger_constellation_id
    ).first()
    defender_constellation = db.query(Constellation).filter(
        Constellation.id == battle.defender_constellation_id
    ).first()
    
    if challenger_constellation:
        challenger_constellation.total_battles += 1
        if battle.winner_constellation_id == challenger_constellation.id:
            challenger_constellation.battles_won += 1
        # Update battle rating (simplified ELO-like system)
        rating_change = 20 if battle.winner_constellation_id == challenger_constellation.id else -10
        challenger_constellation.battle_rating = max(1000, challenger_constellation.battle_rating + rating_change)
    
    if defender_constellation:
        defender_constellation.total_battles += 1
        if battle.winner_constellation_id == defender_constellation.id:
            defender_constellation.battles_won += 1
        # Update battle rating
        rating_change = 20 if battle.winner_constellation_id == defender_constellation.id else -10
        defender_constellation.battle_rating = max(1000, defender_constellation.battle_rating + rating_change)
    
    # Distribute individual rewards to participants
    participations = db.query(ConstellationBattleParticipation).filter(
        ConstellationBattleParticipation.battle_id == battle.id
    ).all()
    
    # Calculate total score for each constellation
    challenger_total_score = sum(p.individual_score for p in participations 
                                if p.constellation_id == battle.challenger_constellation_id)
    defender_total_score = sum(p.individual_score for p in participations 
                              if p.constellation_id == battle.defender_constellation_id)
    
    for participation in participations:
        # Calculate contribution percentage
        constellation_total = (challenger_total_score if participation.constellation_id == battle.challenger_constellation_id 
                              else defender_total_score)
        if constellation_total > 0:
            participation.contribution_percentage = (participation.individual_score / constellation_total) * 100
        else:
            participation.contribution_percentage = 0
        
        # Calculate individual reward
        is_winner = participation.constellation_id == battle.winner_constellation_id
        constellation_reward = battle.winner_reward if is_winner else loser_reward
        participation.individual_reward = constellation_reward * (participation.contribution_percentage / 100)
        
        # Bonus XP for participation
        base_xp = 100
        performance_multiplier = min(2.0, participation.individual_score / 1000)  # Max 2x multiplier
        participation.bonus_xp = int(base_xp * performance_multiplier)
        if is_winner:
            participation.bonus_xp = int(participation.bonus_xp * 1.5)  # 50% bonus for winners
        
        # Update constellation membership stats
        membership = db.query(ConstellationMembership).filter(
            ConstellationMembership.constellation_id == participation.constellation_id,
            ConstellationMembership.user_id == participation.user_id
        ).first()
        
        if membership:
            membership.battles_participated += 1
            membership.stellar_shards_contributed += participation.stellar_shards_earned
            membership.contribution_score += int(participation.individual_score * 0.1)
    
    db.commit()


# Real Trading Integration Endpoints
@router.post("/battles/{battle_id}/start-trading")
async def start_battle_trading_integration(
    battle_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Start real trading integration for a battle."""
    battle = db.query(ConstellationBattle).filter(
        ConstellationBattle.id == battle_id
    ).first()
    
    if not battle:
        raise HTTPException(status_code=404, detail="Battle not found")
    
    if battle.status != "active":
        raise HTTPException(
            status_code=400,
            detail="Battle must be active to start trading integration"
        )
    
    # Check if user is admin/owner of either constellation
    membership = db.query(ConstellationMembership).filter(
        ConstellationMembership.user_id == current_user.id,
        ConstellationMembership.constellation_id.in_([
            battle.challenger_constellation_id,
            battle.defender_constellation_id
        ]),
        ConstellationMembership.role.in_(["owner", "admin"]),
        ConstellationMembership.is_active == True
    ).first()
    
    if not membership:
        raise HTTPException(
            status_code=403,
            detail="Only constellation owners/admins can start trading integration"
        )
    
    try:
        result = await start_battle_monitoring(battle_id, db)
        return {
            "message": "Trading integration started successfully",
            "battle_id": battle_id,
            "initial_scores": result
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start trading integration: {str(e)}"
        )


@router.get("/battles/{battle_id}/real-time-scores")
async def get_battle_real_time_scores(
    battle_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get real-time battle scores based on actual trading performance."""
    battle = db.query(ConstellationBattle).filter(
        ConstellationBattle.id == battle_id
    ).first()
    
    if not battle:
        raise HTTPException(status_code=404, detail="Battle not found")
    
    # Check if user is member of either constellation
    membership = db.query(ConstellationMembership).filter(
        ConstellationMembership.user_id == current_user.id,
        ConstellationMembership.constellation_id.in_([
            battle.challenger_constellation_id,
            battle.defender_constellation_id
        ]),
        ConstellationMembership.is_active == True
    ).first()
    
    if not membership:
        raise HTTPException(
            status_code=403,
            detail="Only constellation members can view battle scores"
        )
    
    try:
        scores = await get_real_time_battle_scores(battle_id, db)
        return scores
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get real-time scores: {str(e)}"
        )


@router.get("/{constellation_id}/trading-performance")
async def get_constellation_trading_performance(
    constellation_id: int,
    period_days: int = Query(7, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get comprehensive trading performance for a constellation."""
    constellation = db.query(Constellation).filter(
        Constellation.id == constellation_id
    ).first()
    
    if not constellation:
        raise HTTPException(status_code=404, detail="Constellation not found")
    
    # Check if user is member of the constellation or constellation is public
    if not constellation.is_public:
        membership = db.query(ConstellationMembership).filter(
            ConstellationMembership.constellation_id == constellation_id,
            ConstellationMembership.user_id == current_user.id,
            ConstellationMembership.is_active == True
        ).first()
        
        if not membership:
            raise HTTPException(
                status_code=403,
                detail="Access denied to private constellation"
            )
    
    try:
        performance = await get_clan_trading_performance(constellation_id, db)
        return performance
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get trading performance: {str(e)}"
        )


@router.get("/{constellation_id}/trading-leaderboard")
async def get_constellation_trading_leaderboard(
    constellation_id: int,
    period_days: int = Query(7, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get trading leaderboard for constellation members."""
    constellation = db.query(Constellation).filter(
        Constellation.id == constellation_id
    ).first()
    
    if not constellation:
        raise HTTPException(status_code=404, detail="Constellation not found")
    
    # Check if user is member of the constellation or constellation is public
    if not constellation.is_public:
        membership = db.query(ConstellationMembership).filter(
            ConstellationMembership.constellation_id == constellation_id,
            ConstellationMembership.user_id == current_user.id,
            ConstellationMembership.is_active == True
        ).first()
        
        if not membership:
            raise HTTPException(
                status_code=403,
                detail="Access denied to private constellation"
            )
    
    try:
        leaderboard = await clan_trading_service.get_clan_trading_leaderboard(
            constellation_id=constellation_id,
            period_days=period_days,
            db=db
        )
        
        return {
            "constellation_id": constellation_id,
            "period_days": period_days,
            "leaderboard": leaderboard,
            "last_updated": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get trading leaderboard: {str(e)}"
        )


@router.post("/{constellation_id}/copy-trading/follow")
async def follow_trader(
    constellation_id: int,
    target_user_id: int,
    allocation_percentage: float = Field(..., ge=1.0, le=50.0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Follow a successful trader within the constellation (social trading)."""
    # Check if user is member of the constellation
    membership = db.query(ConstellationMembership).filter(
        ConstellationMembership.constellation_id == constellation_id,
        ConstellationMembership.user_id == current_user.id,
        ConstellationMembership.is_active == True
    ).first()
    
    if not membership:
        raise HTTPException(
            status_code=403,
            detail="Only constellation members can use copy trading"
        )
    
    # Check if target user is also a member
    target_membership = db.query(ConstellationMembership).filter(
        ConstellationMembership.constellation_id == constellation_id,
        ConstellationMembership.user_id == target_user_id,
        ConstellationMembership.is_active == True
    ).first()
    
    if not target_membership:
        raise HTTPException(
            status_code=404,
            detail="Target trader is not a member of this constellation"
        )
    
    if target_user_id == current_user.id:
        raise HTTPException(
            status_code=400,
            detail="Cannot follow yourself"
        )
    
    # For now, return success message
    # In full implementation, this would create a copy trading relationship
    return {
        "message": f"Successfully started following trader {target_user_id}",
        "constellation_id": constellation_id,
        "follower_id": current_user.id,
        "target_trader_id": target_user_id,
        "allocation_percentage": allocation_percentage,
        "status": "active",
        "started_at": datetime.utcnow().isoformat()
    }


# Battle Monitoring Control Endpoints
@router.post("/battles/{battle_id}/force-update")
async def force_battle_update(
    battle_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Force an immediate battle score update (admin only)."""
    battle = db.query(ConstellationBattle).filter(
        ConstellationBattle.id == battle_id
    ).first()
    
    if not battle:
        raise HTTPException(status_code=404, detail="Battle not found")
    
    # Check if user is admin/owner of either constellation
    membership = db.query(ConstellationMembership).filter(
        ConstellationMembership.user_id == current_user.id,
        ConstellationMembership.constellation_id.in_([
            battle.challenger_constellation_id,
            battle.defender_constellation_id
        ]),
        ConstellationMembership.role.in_(["owner", "admin"]),
        ConstellationMembership.is_active == True
    ).first()
    
    if not membership:
        raise HTTPException(
            status_code=403,
            detail="Only constellation owners/admins can force updates"
        )
    
    try:
        results = await trigger_battle_update(battle_id)
        return {
            "message": "Battle update completed",
            "battle_id": battle_id,
            "results": results
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to force update: {str(e)}"
        )


@router.get("/battles/monitor-status")
async def get_battle_monitor_status(
    current_user: User = Depends(get_current_user)
):
    """Get the status of the battle monitoring service."""
    try:
        status = await get_monitor_status()
        return status
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get monitor status: {str(e)}"
        )


@router.post("/battles/trigger-all-updates")
async def trigger_all_battle_updates(
    current_user: User = Depends(get_current_user)
):
    """Trigger updates for all active battles (system admin only)."""
    # For now, allow any authenticated user to trigger updates
    # In production, you might want to restrict this to system admins
    
    try:
        results = await trigger_battle_update()  # No battle_id = update all
        return {
            "message": "All battle updates completed",
            "results": results,
            "battles_updated": len(results)
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to trigger updates: {str(e)}"
        )