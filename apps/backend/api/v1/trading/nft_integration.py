from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
import json
import hashlib
import secrets

from ...core.database import get_db
from ...models.game_models import (
    User, Artifact, UserGameStats, ConstellationMembership, ViralContent
)
from ...auth.auth import get_current_active_user as get_current_user

router = APIRouter(prefix="/nft", tags=["nft_integration"])


# Pydantic models
class GenesisNFTRequest(BaseModel):
    achievement_type: str = Field(..., regex=r"^(first_trade|level_milestone|constellation_founder|viral_legend|trading_master)$")
    milestone_data: Dict[str, Any]


class GenesisNFTResponse(BaseModel):
    nft_id: str
    token_id: int
    achievement_type: str
    rarity: str
    points_earned: int
    metadata: Dict[str, Any]
    minting_transaction: Optional[str]
    minting_status: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class NFTMarketplaceItem(BaseModel):
    nft_id: str
    token_id: int
    owner_address: str
    owner_username: str
    price: float
    currency: str  # 'stellar_shards' or 'lumina'
    rarity: str
    achievement_type: str
    metadata: Dict[str, Any]
    listed_at: datetime
    is_featured: bool = False


class ShareableNFTRequest(BaseModel):
    nft_id: str
    share_platforms: List[str] = Field(..., min_items=1)
    custom_message: Optional[str] = Field(None, max_length=280)


class NFTCollectionResponse(BaseModel):
    user_id: int
    total_nfts: int
    unique_achievements: int
    total_rarity_score: float
    featured_nft: Optional[GenesisNFTResponse]
    recent_nfts: List[GenesisNFTResponse]
    collection_value: Dict[str, float]  # estimated value in different currencies
    
    class Config:
        from_attributes = True


# Genesis Seed NFT endpoints
@router.post("/genesis/mint", response_model=GenesisNFTResponse)
async def mint_genesis_nft(
    request: GenesisNFTRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mint a Genesis Seed NFT for significant achievements"""
    try:
        # Validate achievement eligibility
        eligibility = await _check_genesis_eligibility(
            current_user.id,
            request.achievement_type,
            request.milestone_data,
            db
        )
        
        if not eligibility["eligible"]:
            raise HTTPException(
                status_code=400,
                detail=f"Not eligible for Genesis NFT: {eligibility['reason']}"
            )
        
        # Generate unique NFT ID
        nft_id = _generate_nft_id(current_user.id, request.achievement_type)
        
        # Determine rarity based on achievement and user stats
        rarity = _calculate_nft_rarity(request.achievement_type, eligibility["stats"])
        
        # Calculate points earned
        points_earned = _calculate_genesis_points(request.achievement_type, rarity)
        
        # Create NFT metadata
        metadata = _create_nft_metadata(
            request.achievement_type,
            rarity,
            request.milestone_data,
            current_user,
            eligibility["stats"]
        )
        
        # Create artifact record (representing the NFT)
        artifact = Artifact(
            user_id=current_user.id,
            artifact_type=f"genesis_{request.achievement_type}",
            rarity=rarity,
            bonus_percentage=_calculate_bonus_percentage(rarity),
            is_equipped=False
        )
        
        db.add(artifact)
        db.flush()  # Get the artifact ID
        
        # Simulate blockchain minting (in production, integrate with actual contract)
        minting_result = await _simulate_blockchain_minting(
            current_user.id,
            artifact.id,
            request.achievement_type,
            rarity,
            points_earned,
            metadata
        )
        
        # Create Genesis NFT response
        genesis_nft = GenesisNFTResponse(
            nft_id=nft_id,
            token_id=artifact.id,
            achievement_type=request.achievement_type,
            rarity=rarity,
            points_earned=points_earned,
            metadata=metadata,
            minting_transaction=minting_result["tx_hash"],
            minting_status="minted",
            created_at=artifact.discovered_at
        )
        
        # Award bonus XP for Genesis NFT
        current_user.xp += points_earned
        
        db.commit()
        
        return genesis_nft
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to mint Genesis NFT: {str(e)}")


@router.get("/genesis/collection/{user_id}", response_model=NFTCollectionResponse)
async def get_genesis_collection(
    user_id: int,
    db: Session = Depends(get_db)
):
    """Get user's Genesis NFT collection"""
    try:
        # Get user's artifacts (representing NFTs)
        artifacts = db.query(Artifact).filter(
            Artifact.user_id == user_id,
            Artifact.artifact_type.like("genesis_%")
        ).all()
        
        if not artifacts:
            return NFTCollectionResponse(
                user_id=user_id,
                total_nfts=0,
                unique_achievements=0,
                total_rarity_score=0.0,
                featured_nft=None,
                recent_nfts=[],
                collection_value={"stellar_shards": 0.0, "lumina": 0.0}
            )
        
        # Calculate collection stats
        unique_achievements = len(set(artifact.artifact_type for artifact in artifacts))
        total_rarity_score = sum(_get_rarity_score(artifact.rarity) for artifact in artifacts)
        
        # Get recent NFTs (last 5)
        recent_artifacts = sorted(artifacts, key=lambda x: x.discovered_at, reverse=True)[:5]
        
        # Find featured NFT (highest rarity)
        featured_artifact = max(artifacts, key=lambda x: _get_rarity_score(x.rarity))
        
        # Calculate collection value
        collection_value = _calculate_collection_value(artifacts)
        
        # Convert artifacts to Genesis NFT responses
        recent_nfts = []
        for artifact in recent_artifacts:
            achievement_type = artifact.artifact_type.replace("genesis_", "")
            nft_id = _generate_nft_id(user_id, achievement_type)
            
            recent_nfts.append(GenesisNFTResponse(
                nft_id=nft_id,
                token_id=artifact.id,
                achievement_type=achievement_type,
                rarity=artifact.rarity,
                points_earned=_calculate_genesis_points(achievement_type, artifact.rarity),
                metadata=_create_nft_metadata(achievement_type, artifact.rarity, {}, None, {}),
                minting_transaction=f"tx_{artifact.id}",
                minting_status="minted",
                created_at=artifact.discovered_at
            ))
        
        # Featured NFT
        featured_achievement_type = featured_artifact.artifact_type.replace("genesis_", "")
        featured_nft = GenesisNFTResponse(
            nft_id=_generate_nft_id(user_id, featured_achievement_type),
            token_id=featured_artifact.id,
            achievement_type=featured_achievement_type,
            rarity=featured_artifact.rarity,
            points_earned=_calculate_genesis_points(featured_achievement_type, featured_artifact.rarity),
            metadata=_create_nft_metadata(featured_achievement_type, featured_artifact.rarity, {}, None, {}),
            minting_transaction=f"tx_{featured_artifact.id}",
            minting_status="minted",
            created_at=featured_artifact.discovered_at
        )
        
        return NFTCollectionResponse(
            user_id=user_id,
            total_nfts=len(artifacts),
            unique_achievements=unique_achievements,
            total_rarity_score=total_rarity_score,
            featured_nft=featured_nft,
            recent_nfts=recent_nfts,
            collection_value=collection_value
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get collection: {str(e)}")


# NFT Marketplace endpoints
@router.get("/marketplace", response_model=List[NFTMarketplaceItem])
async def get_marketplace_listings(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    rarity: Optional[str] = Query(None, regex=r"^(common|rare|epic|legendary)$"),
    achievement_type: Optional[str] = Query(None),
    min_price: Optional[float] = Query(None, ge=0),
    max_price: Optional[float] = Query(None, ge=0),
    currency: Optional[str] = Query("stellar_shards", regex=r"^(stellar_shards|lumina)$"),
    sort_by: str = Query("listed_at", regex=r"^(price|rarity|listed_at)$"),
    sort_order: str = Query("desc", regex=r"^(asc|desc)$"),
    db: Session = Depends(get_db)
):
    """Get NFT marketplace listings with filtering and sorting"""
    try:
        # For now, return mock marketplace data since we don't have a marketplace table
        # In production, this would query a marketplace_listings table
        mock_listings = _get_mock_marketplace_listings()
        
        # Apply filters
        filtered_listings = mock_listings
        
        if rarity:
            filtered_listings = [item for item in filtered_listings if item.rarity == rarity]
        
        if achievement_type:
            filtered_listings = [item for item in filtered_listings if item.achievement_type == achievement_type]
        
        if min_price is not None:
            filtered_listings = [item for item in filtered_listings if item.price >= min_price]
        
        if max_price is not None:
            filtered_listings = [item for item in filtered_listings if item.price <= max_price]
        
        # Apply sorting
        reverse = sort_order == "desc"
        
        if sort_by == "price":
            filtered_listings.sort(key=lambda x: x.price, reverse=reverse)
        elif sort_by == "rarity":
            rarity_order = {"common": 1, "rare": 2, "epic": 3, "legendary": 4}
            filtered_listings.sort(key=lambda x: rarity_order.get(x.rarity, 0), reverse=reverse)
        else:  # listed_at
            filtered_listings.sort(key=lambda x: x.listed_at, reverse=reverse)
        
        # Apply pagination
        start_idx = skip
        end_idx = skip + limit
        paginated_listings = filtered_listings[start_idx:end_idx]
        
        return paginated_listings
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get marketplace listings: {str(e)}")


@router.post("/marketplace/list/{nft_id}")
async def list_nft_for_sale(
    nft_id: str,
    price: float = Query(..., gt=0),
    currency: str = Query("stellar_shards", regex=r"^(stellar_shards|lumina)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List an NFT for sale on the marketplace"""
    try:
        # Parse NFT ID to get artifact ID
        artifact_id = int(nft_id.split("_")[-1]) if "_" in nft_id else int(nft_id)
        
        # Verify user owns the NFT
        artifact = db.query(Artifact).filter(
            Artifact.id == artifact_id,
            Artifact.user_id == current_user.id
        ).first()
        
        if not artifact:
            raise HTTPException(status_code=404, detail="NFT not found or not owned by user")
        
        # Check if already listed (in production, check marketplace_listings table)
        # For now, just simulate the listing
        
        listing_data = {
            "nft_id": nft_id,
            "user_id": current_user.id,
            "artifact_id": artifact_id,
            "price": price,
            "currency": currency,
            "listed_at": datetime.utcnow(),
            "status": "active"
        }
        
        # In production, insert into marketplace_listings table
        # db.add(MarketplaceListing(**listing_data))
        # db.commit()
        
        return {
            "message": "NFT listed successfully",
            "listing_id": f"listing_{artifact_id}",
            "nft_id": nft_id,
            "price": price,
            "currency": currency
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list NFT: {str(e)}")


@router.post("/marketplace/buy/{listing_id}")
async def buy_nft_from_marketplace(
    listing_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Buy an NFT from the marketplace"""
    try:
        # In production, get the actual listing from marketplace_listings table
        # For now, simulate the purchase
        
        # Validate user has enough currency
        # This would check user's stellar_shards or lumina balance
        
        # Mock purchase validation
        mock_price = 1000.0  # stellar_shards
        user_balance = 5000.0  # mock balance
        
        if user_balance < mock_price:
            raise HTTPException(
                status_code=400,
                detail="Insufficient balance to purchase this NFT"
            )
        
        # Transfer ownership (in production)
        # 1. Update artifact ownership
        # 2. Deduct currency from buyer
        # 3. Credit currency to seller (minus marketplace fee)
        # 4. Update marketplace listing status
        # 5. Create transaction record
        
        return {
            "message": "NFT purchased successfully",
            "transaction_id": f"tx_{secrets.token_hex(16)}",
            "listing_id": listing_id,
            "price_paid": mock_price,
            "currency": "stellar_shards"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to purchase NFT: {str(e)}")


@router.delete("/marketplace/unlist/{listing_id}")
async def unlist_nft_from_marketplace(
    listing_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Remove an NFT listing from the marketplace"""
    try:
        # In production, find and update the marketplace listing
        # Verify user owns the listing
        # Update status to 'cancelled'
        
        return {
            "message": "NFT unlisted successfully",
            "listing_id": listing_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to unlist NFT: {str(e)}")


# Shareable NFT content endpoints
@router.post("/share/{nft_id}")
async def create_shareable_nft_content(
    nft_id: str,
    request: ShareableNFTRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create shareable content for an NFT"""
    try:
        # Parse NFT ID to get artifact ID
        artifact_id = int(nft_id.split("_")[-1]) if "_" in nft_id else int(nft_id)
        
        # Verify user owns the NFT
        artifact = db.query(Artifact).filter(
            Artifact.id == artifact_id,
            Artifact.user_id == current_user.id
        ).first()
        
        if not artifact:
            raise HTTPException(status_code=404, detail="NFT not found or not owned by user")
        
        # Generate shareable content
        achievement_type = artifact.artifact_type.replace("genesis_", "")
        
        share_content = {
            "nft_showcase": {
                "title": f"Check out my {artifact.rarity.title()} Genesis NFT!",
                "description": f"Just achieved {achievement_type.replace('_', ' ').title()} in AstraTrade!",
                "image_url": f"https://api.astratrade.com/nft/image/{nft_id}",
                "metadata": {
                    "achievement": achievement_type,
                    "rarity": artifact.rarity,
                    "power_level": artifact.bonus_percentage,
                    "owner": current_user.username
                }
            },
            "platform_content": {}
        }
        
        # Generate platform-specific content
        for platform in request.share_platforms:
            if platform == "twitter":
                share_content["platform_content"]["twitter"] = {
                    "text": f"🌟 Just minted a {artifact.rarity.title()} Genesis NFT in @AstraTrade! {request.custom_message or ''} #NFT #GameFi #Starknet",
                    "image_url": share_content["nft_showcase"]["image_url"]
                }
            elif platform == "discord":
                share_content["platform_content"]["discord"] = {
                    "embed": {
                        "title": share_content["nft_showcase"]["title"],
                        "description": share_content["nft_showcase"]["description"],
                        "image": {"url": share_content["nft_showcase"]["image_url"]},
                        "color": _get_rarity_color(artifact.rarity)
                    }
                }
            elif platform == "instagram":
                share_content["platform_content"]["instagram"] = {
                    "caption": f"{share_content['nft_showcase']['title']} {request.custom_message or ''} #AstraTrade #NFT #Gaming",
                    "image_url": share_content["nft_showcase"]["image_url"]
                }
        
        # Create viral content record for tracking
        viral_content = ViralContent(
            user_id=current_user.id,
            content_type="nft_showcase",
            title=share_content["nft_showcase"]["title"],
            content_data=share_content,
            shares_count=0,
            likes_count=0,
            viral_score=0.0
        )
        
        db.add(viral_content)
        db.commit()
        
        return {
            "share_id": f"share_{viral_content.id}",
            "share_content": share_content,
            "platforms": request.share_platforms,
            "created_at": viral_content.created_at
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create shareable content: {str(e)}")


# Helper functions
async def _check_genesis_eligibility(user_id: int, achievement_type: str, milestone_data: Dict, db: Session) -> Dict:
    """Check if user is eligible for Genesis NFT"""
    user_stats = db.query(UserGameStats).filter(UserGameStats.user_id == user_id).first()
    
    eligibility = {"eligible": False, "reason": "", "stats": {}}
    
    if achievement_type == "first_trade":
        # Check if user has made their first trade
        if user_stats and user_stats.trades_executed > 0:
            eligibility = {"eligible": True, "reason": "First trade completed", "stats": {"trades": user_stats.trades_executed}}
    
    elif achievement_type == "level_milestone":
        required_level = milestone_data.get("level", 10)
        if user_stats and user_stats.current_level >= required_level:
            eligibility = {"eligible": True, "reason": f"Reached level {required_level}", "stats": {"level": user_stats.current_level}}
    
    elif achievement_type == "constellation_founder":
        # Check if user founded a constellation
        membership = db.query(ConstellationMembership).filter(
            ConstellationMembership.user_id == user_id,
            ConstellationMembership.role == "owner"
        ).first()
        if membership:
            eligibility = {"eligible": True, "reason": "Founded a constellation", "stats": {"constellation_id": membership.constellation_id}}
    
    elif achievement_type == "viral_legend":
        # Check viral content performance
        viral_content = db.query(ViralContent).filter(ViralContent.user_id == user_id).all()
        total_viral_score = sum(content.viral_score for content in viral_content)
        if total_viral_score >= 1000:  # Threshold for viral legend
            eligibility = {"eligible": True, "reason": "Achieved viral legend status", "stats": {"viral_score": total_viral_score}}
    
    elif achievement_type == "trading_master":
        # Check trading performance
        if user_stats and user_stats.stellar_shards_earned >= 100000:  # High earning threshold
            eligibility = {"eligible": True, "reason": "Achieved trading master status", "stats": {"earnings": user_stats.stellar_shards_earned}}
    
    if not eligibility["eligible"]:
        eligibility["reason"] = "Achievement requirements not met"
    
    return eligibility


def _generate_nft_id(user_id: int, achievement_type: str) -> str:
    """Generate unique NFT ID"""
    timestamp = int(datetime.utcnow().timestamp())
    data = f"{user_id}_{achievement_type}_{timestamp}"
    hash_obj = hashlib.sha256(data.encode())
    return f"genesis_{achievement_type}_{hash_obj.hexdigest()[:8]}"


def _calculate_nft_rarity(achievement_type: str, stats: Dict) -> str:
    """Calculate NFT rarity based on achievement and user stats"""
    # Base rarity by achievement type
    base_rarities = {
        "first_trade": "common",
        "level_milestone": "rare",
        "constellation_founder": "epic",
        "viral_legend": "legendary",
        "trading_master": "legendary"
    }
    
    base_rarity = base_rarities.get(achievement_type, "common")
    
    # Upgrade rarity based on stats (simplified logic)
    if achievement_type == "level_milestone":
        level = stats.get("level", 0)
        if level >= 50:
            return "legendary"
        elif level >= 25:
            return "epic"
    
    elif achievement_type == "viral_legend":
        viral_score = stats.get("viral_score", 0)
        if viral_score >= 5000:
            return "legendary"
    
    return base_rarity


def _calculate_genesis_points(achievement_type: str, rarity: str) -> int:
    """Calculate points earned for Genesis NFT"""
    base_points = {
        "first_trade": 100,
        "level_milestone": 250,
        "constellation_founder": 500,
        "viral_legend": 750,
        "trading_master": 1000
    }
    
    rarity_multiplier = {
        "common": 1.0,
        "rare": 1.5,
        "epic": 2.0,
        "legendary": 3.0
    }
    
    base = base_points.get(achievement_type, 100)
    multiplier = rarity_multiplier.get(rarity, 1.0)
    
    return int(base * multiplier)


def _calculate_bonus_percentage(rarity: str) -> float:
    """Calculate bonus percentage for artifact"""
    bonus_map = {
        "common": 5.0,
        "rare": 10.0,
        "epic": 20.0,
        "legendary": 35.0
    }
    return bonus_map.get(rarity, 5.0)


def _create_nft_metadata(achievement_type: str, rarity: str, milestone_data: Dict, user: Optional[User], stats: Dict) -> Dict:
    """Create NFT metadata"""
    return {
        "name": f"Genesis {achievement_type.replace('_', ' ').title()}",
        "description": f"A {rarity} Genesis Seed NFT representing {achievement_type.replace('_', ' ')} achievement",
        "image": f"https://api.astratrade.com/nft/image/genesis_{achievement_type}_{rarity}.png",
        "attributes": [
            {"trait_type": "Achievement", "value": achievement_type.replace('_', ' ').title()},
            {"trait_type": "Rarity", "value": rarity.title()},
            {"trait_type": "Power Level", "value": _calculate_bonus_percentage(rarity)},
            {"trait_type": "Minted Date", "value": datetime.utcnow().isoformat()},
        ],
        "external_url": f"https://astratrade.com/nft/genesis/{achievement_type}",
        "background_color": _get_rarity_color(rarity)
    }


async def _simulate_blockchain_minting(user_id: int, artifact_id: int, achievement_type: str, rarity: str, points: int, metadata: Dict) -> Dict:
    """Simulate blockchain minting process"""
    # In production, this would interact with actual Starknet contracts
    tx_hash = f"0x{secrets.token_hex(32)}"
    
    return {
        "tx_hash": tx_hash,
        "block_number": 12345678,
        "gas_used": 150000,
        "status": "success"
    }


def _get_rarity_score(rarity: str) -> float:
    """Get numeric rarity score"""
    scores = {
        "common": 1.0,
        "rare": 2.5,
        "epic": 5.0,
        "legendary": 10.0
    }
    return scores.get(rarity, 1.0)


def _calculate_collection_value(artifacts: List[Artifact]) -> Dict[str, float]:
    """Calculate estimated collection value"""
    total_stellar_shards = 0.0
    total_lumina = 0.0
    
    for artifact in artifacts:
        rarity_multiplier = _get_rarity_score(artifact.rarity)
        base_value = 100.0  # Base value per NFT
        
        stellar_value = base_value * rarity_multiplier
        lumina_value = stellar_value * 0.1  # 10% conversion rate
        
        total_stellar_shards += stellar_value
        total_lumina += lumina_value
    
    return {
        "stellar_shards": total_stellar_shards,
        "lumina": total_lumina
    }


def _get_rarity_color(rarity: str) -> str:
    """Get color code for rarity"""
    colors = {
        "common": "808080",  # Gray
        "rare": "0099FF",    # Blue
        "epic": "9966CC",    # Purple
        "legendary": "FF6600" # Orange
    }
    return colors.get(rarity, "808080")


def _get_mock_marketplace_listings() -> List[NFTMarketplaceItem]:
    """Get mock marketplace listings for development"""
    return [
        NFTMarketplaceItem(
            nft_id="genesis_first_trade_abc123",
            token_id=1,
            owner_address="0x1234567890abcdef",
            owner_username="CosmicTrader",
            price=500.0,
            currency="stellar_shards",
            rarity="common",
            achievement_type="first_trade",
            metadata={"power_level": 5.0},
            listed_at=datetime.utcnow() - timedelta(hours=2),
            is_featured=False
        ),
        NFTMarketplaceItem(
            nft_id="genesis_constellation_founder_def456",
            token_id=2,
            owner_address="0xfedcba0987654321",
            owner_username="StellarPioneer",
            price=2500.0,
            currency="stellar_shards",
            rarity="epic",
            achievement_type="constellation_founder",
            metadata={"power_level": 20.0},
            listed_at=datetime.utcnow() - timedelta(hours=1),
            is_featured=True
        ),
        NFTMarketplaceItem(
            nft_id="genesis_viral_legend_ghi789",
            token_id=3,
            owner_address="0x1122334455667788",
            owner_username="ViralMaster",
            price=5000.0,
            currency="lumina",
            rarity="legendary",
            achievement_type="viral_legend",
            metadata={"power_level": 35.0},
            listed_at=datetime.utcnow() - timedelta(minutes=30),
            is_featured=True
        )
    ]
        
        db.commit()
        
        return genesis_nft
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to mint Genesis NFT: {str(e)}")


@router.get("/genesis/collection", response_model=NFTCollectionResponse)
async def get_user_nft_collection(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user's NFT collection"""
    try:
        # Get user's artifacts (representing NFTs)
        artifacts = db.query(Artifact).filter(
            Artifact.user_id == current_user.id
        ).order_by(Artifact.discovered_at.desc()).all()
        
        # Convert artifacts to Genesis NFTs
        genesis_nfts = []
        total_rarity_score = 0.0
        
        for artifact in artifacts:
            if artifact.artifact_type.startswith("genesis_"):
                achievement_type = artifact.artifact_type.replace("genesis_", "")
                
                nft = GenesisNFTResponse(
                    nft_id=_generate_nft_id(current_user.id, achievement_type),
                    token_id=artifact.id,
                    achievement_type=achievement_type,
                    rarity=artifact.rarity,
                    points_earned=_calculate_genesis_points(achievement_type, artifact.rarity),
                    metadata=_create_artifact_metadata(artifact, current_user),
                    minting_transaction=f"0x{artifact.id:064x}",  # Mock transaction hash
                    minting_status="minted",
                    created_at=artifact.discovered_at
                )
                
                genesis_nfts.append(nft)
                total_rarity_score += _get_rarity_score(artifact.rarity)
        
        # Get collection value
        collection_value = _calculate_collection_value(genesis_nfts)
        
        # Determine featured NFT (highest rarity or most recent)
        featured_nft = None
        if genesis_nfts:
            featured_nft = max(genesis_nfts, key=lambda x: (_get_rarity_score(x.rarity), x.created_at))
        
        return NFTCollectionResponse(
            user_id=current_user.id,
            total_nfts=len(genesis_nfts),
            unique_achievements=len(set(nft.achievement_type for nft in genesis_nfts)),
            total_rarity_score=total_rarity_score,
            featured_nft=featured_nft,
            recent_nfts=genesis_nfts[:5],  # Most recent 5
            collection_value=collection_value
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get NFT collection: {str(e)}")


@router.get("/genesis/eligible-achievements")
async def get_eligible_achievements(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get achievements eligible for Genesis NFT minting"""
    try:
        game_stats = db.query(UserGameStats).filter(
            UserGameStats.user_id == current_user.id
        ).first()
        
        constellation_membership = db.query(ConstellationMembership).filter(
            ConstellationMembership.user_id == current_user.id,
            ConstellationMembership.is_active == True
        ).first()
        
        # Check existing Genesis NFTs
        existing_artifacts = db.query(Artifact).filter(
            Artifact.user_id == current_user.id,
            Artifact.artifact_type.like("genesis_%")
        ).all()
        
        existing_achievements = set(
            artifact.artifact_type.replace("genesis_", "") 
            for artifact in existing_artifacts
        )
        
        eligible_achievements = []
        
        # First Trade Achievement
        if "first_trade" not in existing_achievements and game_stats and game_stats.total_trades >= 1:
            eligible_achievements.append({
                "achievement_type": "first_trade",
                "name": "Cosmic Genesis",
                "description": "Your first step into the cosmic trading realm",
                "rarity": "common",
                "requirements_met": True,
                "milestone_data": {"first_trade_date": game_stats.last_trade_date}
            })
        
        # Level Milestone Achievement
        if ("level_milestone" not in existing_achievements and 
            current_user.level >= 25 and current_user.level % 25 == 0):
            eligible_achievements.append({
                "achievement_type": "level_milestone",
                "name": "Stellar Ascension",
                "description": f"Reached the prestigious Level {current_user.level}",
                "rarity": "rare" if current_user.level >= 50 else "uncommon",
                "requirements_met": True,
                "milestone_data": {"level_achieved": current_user.level}
            })
        
        # Constellation Founder Achievement
        if ("constellation_founder" not in existing_achievements and 
            constellation_membership and constellation_membership.role == "owner"):
            eligible_achievements.append({
                "achievement_type": "constellation_founder",
                "name": "Constellation Pioneer",
                "description": "Founded and lead a cosmic constellation",
                "rarity": "epic",
                "requirements_met": True,
                "milestone_data": {
                    "constellation_name": constellation_membership.constellation.name,
                    "member_count": constellation_membership.constellation.member_count
                }
            })
        
        # Trading Master Achievement
        if ("trading_master" not in existing_achievements and game_stats and 
            game_stats.total_trades >= 1000 and 
            (game_stats.successful_trades / game_stats.total_trades) >= 0.8):
            eligible_achievements.append({
                "achievement_type": "trading_master",
                "name": "Cosmic Trading Sage",
                "description": "Mastered the art of cosmic trading",
                "rarity": "legendary",
                "requirements_met": True,
                "milestone_data": {
                    "total_trades": game_stats.total_trades,
                    "win_rate": (game_stats.successful_trades / game_stats.total_trades) * 100
                }
            })
        
        # Viral Legend Achievement
        viral_content_count = db.query(ViralContent).filter(
            ViralContent.user_id == current_user.id,
            ViralContent.viral_score >= 500
        ).count()
        
        if ("viral_legend" not in existing_achievements and viral_content_count >= 5):
            eligible_achievements.append({
                "achievement_type": "viral_legend",
                "name": "Cosmic Influencer",
                "description": "Created legendary viral content",
                "rarity": "epic",
                "requirements_met": True,
                "milestone_data": {
                    "viral_content_count": viral_content_count
                }
            })
        
        return {
            "eligible_achievements": eligible_achievements,
            "total_eligible": len(eligible_achievements),
            "existing_genesis_nfts": len(existing_achievements)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get eligible achievements: {str(e)}")


# NFT Marketplace endpoints
@router.get("/marketplace", response_model=List[NFTMarketplaceItem])
async def get_marketplace_items(
    rarity: Optional[str] = Query(None),
    achievement_type: Optional[str] = Query(None),
    min_price: Optional[float] = Query(None),
    max_price: Optional[float] = Query(None),
    currency: str = Query("stellar_shards"),
    sort_by: str = Query("listed_at", regex=r"^(price|listed_at|rarity)$"),
    sort_order: str = Query("desc", regex=r"^(asc|desc)$"),
    limit: int = Query(20, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Get NFT marketplace listings"""
    try:
        # This would query a marketplace table in production
        # For now, return mock marketplace data
        mock_items = _get_mock_marketplace_items()
        
        # Apply filters
        filtered_items = mock_items
        
        if rarity:
            filtered_items = [item for item in filtered_items if item.rarity == rarity]
        
        if achievement_type:
            filtered_items = [item for item in filtered_items if item.achievement_type == achievement_type]
        
        if min_price is not None:
            filtered_items = [item for item in filtered_items if item.price >= min_price]
        
        if max_price is not None:
            filtered_items = [item for item in filtered_items if item.price <= max_price]
        
        if currency:
            filtered_items = [item for item in filtered_items if item.currency == currency]
        
        # Apply sorting
        reverse = sort_order == "desc"
        if sort_by == "price":
            filtered_items.sort(key=lambda x: x.price, reverse=reverse)
        elif sort_by == "rarity":
            filtered_items.sort(key=lambda x: _get_rarity_score(x.rarity), reverse=reverse)
        else:  # listed_at
            filtered_items.sort(key=lambda x: x.listed_at, reverse=reverse)
        
        return filtered_items[:limit]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get marketplace items: {str(e)}")


# Shareable NFT content endpoints
@router.post("/share", response_model=Dict[str, Any])
async def create_shareable_nft_content(
    request: ShareableNFTRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create shareable content for an NFT"""
    try:
        # Get user's artifact/NFT
        artifact = db.query(Artifact).filter(
            Artifact.user_id == current_user.id,
            Artifact.id == int(request.nft_id.split('_')[-1])  # Extract ID from nft_id
        ).first()
        
        if not artifact:
            raise HTTPException(status_code=404, detail="NFT not found")
        
        # Create shareable content
        share_data = {
            "nft_id": request.nft_id,
            "owner": current_user.username,
            "achievement_type": artifact.artifact_type.replace("genesis_", ""),
            "rarity": artifact.rarity,
            "minted_date": artifact.discovered_at.isoformat(),
            "share_message": request.custom_message or f"Check out my {artifact.rarity} Genesis NFT!",
            "share_url": f"https://astratrade.app/nft/{request.nft_id}",
            "visual_style": "cosmic_showcase"
        }
        
        # Create viral content for sharing
        viral_content = ViralContent(
            user_id=current_user.id,
            content_type="nft",
            content_title=f"Genesis NFT: {artifact.artifact_type.replace('genesis_', '').title()}",
            content_description=f"{artifact.rarity.title()} rarity NFT owned by {current_user.username}",
            content_data=share_data,
            is_public=True,
            moderation_status="approved"
        )
        
        db.add(viral_content)
        db.commit()
        
        return {
            "message": "Shareable NFT content created",
            "content_id": viral_content.id,
            "share_url": share_data["share_url"],
            "platforms": request.share_platforms,
            "estimated_reach": len(request.share_platforms) * 100  # Mock engagement
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create shareable content: {str(e)}")


@router.get("/stats/global")
async def get_global_nft_stats(
    db: Session = Depends(get_db)
):
    """Get global NFT statistics"""
    try:
        # Get total Genesis NFTs minted
        total_genesis_nfts = db.query(Artifact).filter(
            Artifact.artifact_type.like("genesis_%")
        ).count()
        
        # Get rarity distribution
        rarity_distribution = {}
        rarities = db.query(Artifact.rarity).filter(
            Artifact.artifact_type.like("genesis_%")
        ).all()
        
        for (rarity,) in rarities:
            rarity_distribution[rarity] = rarity_distribution.get(rarity, 0) + 1
        
        # Get most popular achievement types
        achievement_types = {}
        artifacts = db.query(Artifact.artifact_type).filter(
            Artifact.artifact_type.like("genesis_%")
        ).all()
        
        for (artifact_type,) in artifacts:
            achievement_type = artifact_type.replace("genesis_", "")
            achievement_types[achievement_type] = achievement_types.get(achievement_type, 0) + 1
        
        return {
            "total_genesis_nfts": total_genesis_nfts,
            "unique_holders": db.query(Artifact.user_id).filter(
                Artifact.artifact_type.like("genesis_%")
            ).distinct().count(),
            "rarity_distribution": rarity_distribution,
            "popular_achievements": dict(sorted(achievement_types.items(), key=lambda x: x[1], reverse=True)),
            "average_collection_size": total_genesis_nfts / max(1, len(set(artifact.user_id for artifact in artifacts))),
            "daily_mints": _get_daily_mint_stats(db)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get global NFT stats: {str(e)}")


# Helper functions
async def _check_genesis_eligibility(
    user_id: int,
    achievement_type: str,
    milestone_data: Dict[str, Any],
    db: Session
) -> Dict[str, Any]:
    """Check if user is eligible for Genesis NFT"""
    
    user = db.query(User).filter(User.id == user_id).first()
    game_stats = db.query(UserGameStats).filter(
        UserGameStats.user_id == user_id
    ).first()
    
    # Check if user already has this Genesis NFT type
    existing = db.query(Artifact).filter(
        Artifact.user_id == user_id,
        Artifact.artifact_type == f"genesis_{achievement_type}"
    ).first()
    
    if existing:
        return {"eligible": False, "reason": "Genesis NFT already minted for this achievement"}
    
    eligibility_checks = {
        "first_trade": lambda: game_stats and game_stats.total_trades >= 1,
        "level_milestone": lambda: user.level >= 25,
        "constellation_founder": lambda: _check_constellation_founder(user_id, db),
        "viral_legend": lambda: _check_viral_legend(user_id, db),
        "trading_master": lambda: (game_stats and 
                                 game_stats.total_trades >= 1000 and
                                 (game_stats.successful_trades / game_stats.total_trades) >= 0.8)
    }
    
    check_function = eligibility_checks.get(achievement_type)
    if not check_function or not check_function():
        return {"eligible": False, "reason": "Achievement requirements not met"}
    
    return {
        "eligible": True,
        "stats": {
            "user_level": user.level,
            "total_trades": game_stats.total_trades if game_stats else 0,
            "win_rate": (game_stats.successful_trades / game_stats.total_trades) if game_stats and game_stats.total_trades > 0 else 0
        }
    }


def _generate_nft_id(user_id: int, achievement_type: str) -> str:
    """Generate unique NFT ID"""
    timestamp = int(datetime.utcnow().timestamp())
    unique_string = f"{user_id}_{achievement_type}_{timestamp}"
    hash_object = hashlib.sha256(unique_string.encode())
    return f"GENESIS_{hash_object.hexdigest()[:12].upper()}"


def _calculate_nft_rarity(achievement_type: str, user_stats: Dict[str, Any]) -> str:
    """Calculate NFT rarity based on achievement and user stats"""
    rarity_factors = {
        "first_trade": "common",
        "level_milestone": "rare" if user_stats.get("user_level", 0) >= 50 else "uncommon",
        "constellation_founder": "epic",
        "viral_legend": "epic",
        "trading_master": "legendary"
    }
    
    return rarity_factors.get(achievement_type, "common")


def _calculate_genesis_points(achievement_type: str, rarity: str) -> int:
    """Calculate points earned for Genesis NFT"""
    base_points = {
        "common": 100,
        "uncommon": 250,
        "rare": 500,
        "epic": 1000,
        "legendary": 2500
    }
    
    multipliers = {
        "first_trade": 1.0,
        "level_milestone": 1.5,
        "constellation_founder": 2.0,
        "viral_legend": 1.8,
        "trading_master": 3.0
    }
    
    base = base_points.get(rarity, 100)
    multiplier = multipliers.get(achievement_type, 1.0)
    
    return int(base * multiplier)


def _create_nft_metadata(
    achievement_type: str,
    rarity: str,
    milestone_data: Dict[str, Any],
    user: User,
    stats: Dict[str, Any]
) -> Dict[str, Any]:
    """Create NFT metadata"""
    return {
        "name": f"Genesis {achievement_type.replace('_', ' ').title()}",
        "description": f"A {rarity} Genesis Seed NFT commemorating {achievement_type.replace('_', ' ')}",
        "image": f"https://astratrade.app/nft-images/genesis_{achievement_type}_{rarity}.png",
        "attributes": [
            {"trait_type": "Rarity", "value": rarity.title()},
            {"trait_type": "Achievement", "value": achievement_type.replace("_", " ").title()},
            {"trait_type": "Owner Level", "value": user.level},
            {"trait_type": "Mint Date", "value": datetime.utcnow().strftime("%Y-%m-%d")},
        ],
        "background_color": _get_rarity_color(rarity),
        "external_url": f"https://astratrade.app/nft/{_generate_nft_id(user.id, achievement_type)}",
        "milestone_data": milestone_data,
        "cosmic_properties": {
            "stellar_alignment": _calculate_stellar_alignment(stats),
            "cosmic_resonance": _calculate_cosmic_resonance(rarity),
            "genesis_signature": secrets.token_hex(16)
        }
    }


async def _simulate_blockchain_minting(
    user_id: int,
    token_id: int,
    achievement_type: str,
    rarity: str,
    points: int,
    metadata: Dict[str, Any]
) -> Dict[str, Any]:
    """Simulate blockchain minting process"""
    # In production, this would interact with the actual Starknet contract
    return {
        "tx_hash": f"0x{secrets.token_hex(32)}",
        "block_number": 123456 + token_id,
        "gas_used": 45000,
        "contract_address": "0x1234567890abcdef1234567890abcdef12345678",
        "token_id": token_id,
        "status": "confirmed"
    }


def _get_mock_marketplace_items() -> List[NFTMarketplaceItem]:
    """Get mock marketplace items"""
    return [
        NFTMarketplaceItem(
            nft_id="GENESIS_ABCD1234EFGH",
            token_id=1,
            owner_address="0x1234...5678",
            owner_username="CosmicTrader",
            price=50000.0,
            currency="stellar_shards",
            rarity="epic",
            achievement_type="constellation_founder",
            metadata={"name": "Genesis Constellation Founder"},
            listed_at=datetime.utcnow() - timedelta(hours=2),
            is_featured=True
        ),
        NFTMarketplaceItem(
            nft_id="GENESIS_WXYZ9876STUV",
            token_id=2,
            owner_address="0x9876...3210",
            owner_username="StellarExplorer",
            price=25000.0,
            currency="stellar_shards",
            rarity="rare",
            achievement_type="level_milestone",
            metadata={"name": "Genesis Level Milestone"},
            listed_at=datetime.utcnow() - timedelta(hours=6),
            is_featured=False
        )
    ]


def _get_rarity_score(rarity: str) -> float:
    """Get numerical score for rarity"""
    scores = {
        "common": 1.0,
        "uncommon": 2.5,
        "rare": 5.0,
        "epic": 10.0,
        "legendary": 25.0
    }
    return scores.get(rarity, 1.0)


def _get_rarity_color(rarity: str) -> str:
    """Get color for rarity"""
    colors = {
        "common": "808080",
        "uncommon": "00FF00",
        "rare": "0080FF",
        "epic": "8000FF",
        "legendary": "FF8000"
    }
    return colors.get(rarity, "808080")


def _calculate_collection_value(genesis_nfts: List[GenesisNFTResponse]) -> Dict[str, float]:
    """Calculate collection value"""
    base_values = {
        "common": 1000.0,
        "uncommon": 2500.0,
        "rare": 5000.0,
        "epic": 15000.0,
        "legendary": 50000.0
    }
    
    total_ss = sum(base_values.get(nft.rarity, 1000.0) for nft in genesis_nfts)
    total_lumina = total_ss * 0.2  # 1 LM = 5 SS conversion rate
    
    return {
        "stellar_shards": total_ss,
        "lumina": total_lumina,
        "estimated_usd": total_ss * 0.001  # Mock USD conversion
    }


def _check_constellation_founder(user_id: int, db: Session) -> bool:
    """Check if user is constellation founder"""
    membership = db.query(ConstellationMembership).filter(
        ConstellationMembership.user_id == user_id,
        ConstellationMembership.role == "owner",
        ConstellationMembership.is_active == True
    ).first()
    return membership is not None


def _check_viral_legend(user_id: int, db: Session) -> bool:
    """Check if user qualifies as viral legend"""
    viral_count = db.query(ViralContent).filter(
        ViralContent.user_id == user_id,
        ViralContent.viral_score >= 500
    ).count()
    return viral_count >= 5


def _create_artifact_metadata(artifact: Artifact, user: User) -> Dict[str, Any]:
    """Create metadata for existing artifact"""
    achievement_type = artifact.artifact_type.replace("genesis_", "")
    return _create_nft_metadata(
        achievement_type,
        artifact.rarity,
        {},
        user,
        {"user_level": user.level}
    )


def _calculate_stellar_alignment(stats: Dict[str, Any]) -> float:
    """Calculate stellar alignment score"""
    level = stats.get("user_level", 1)
    trades = stats.get("total_trades", 0)
    win_rate = stats.get("win_rate", 0)
    
    return min(100.0, (level * 2) + (trades / 10) + (win_rate * 0.5))


def _calculate_cosmic_resonance(rarity: str) -> float:
    """Calculate cosmic resonance based on rarity"""
    base_resonance = _get_rarity_score(rarity) * 10
    return base_resonance + (secrets.randbelow(20) - 10)  # Add some randomness


def _get_daily_mint_stats(db: Session) -> List[Dict[str, Any]]:
    """Get daily minting statistics"""
    # Mock daily stats for the past week
    stats = []
    for i in range(7):
        date = datetime.utcnow() - timedelta(days=i)
        stats.append({
            "date": date.strftime("%Y-%m-%d"),
            "mints": secrets.randbelow(20) + 5,  # 5-25 mints per day
            "unique_minters": secrets.randbelow(15) + 3  # 3-18 unique minters
        })
    
    return list(reversed(stats))