"""
NFT Domain Value Objects

Value objects for the NFT Domain as defined in ADR-001.
These are immutable objects that describe characteristics of NFT-related concepts.
"""

from datetime import datetime, timezone, timedelta
from decimal import Decimal
from enum import Enum
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
import hashlib
import secrets


class AchievementType(Enum):
    """Types of achievements that can earn Genesis NFTs"""
    FIRST_TRADE = "first_trade"
    LEVEL_MILESTONE = "level_milestone"
    CONSTELLATION_FOUNDER = "constellation_founder"
    VIRAL_LEGEND = "viral_legend"
    TRADING_MASTER = "trading_master"


class RarityLevel(Enum):
    """NFT rarity levels"""
    COMMON = "common"
    UNCOMMON = "uncommon" 
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"


class NFTStatus(Enum):
    """NFT lifecycle status"""
    PENDING_MINT = "pending_mint"
    MINTED = "minted"
    LISTED = "listed"
    SOLD = "sold"
    TRANSFERRED = "transferred"
    BURNED = "burned"


class MarketplaceCurrency(Enum):
    """Supported marketplace currencies"""
    STELLAR_SHARDS = "stellar_shards"
    LUMINA = "lumina"
    STARKNET_ETH = "starknet_eth"


class ListingStatus(Enum):
    """Marketplace listing status"""
    ACTIVE = "active"
    SOLD = "sold"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


@dataclass(frozen=True)
class Rarity:
    """Value object for NFT rarity with scoring and visual properties"""
    level: RarityLevel
    score: Decimal
    color_code: str
    description: str
    
    def __post_init__(self):
        if self.score < 0:
            raise ValueError("Rarity score cannot be negative")
        if not self.color_code or len(self.color_code) != 6:
            raise ValueError("Color code must be a 6-character hex string")
        if not self.description or len(self.description.strip()) == 0:
            raise ValueError("Rarity description cannot be empty")
    
    @classmethod
    def from_level(cls, level: RarityLevel) -> 'Rarity':
        """Create rarity from level with default properties"""
        rarity_configs = {
            RarityLevel.COMMON: {
                "score": Decimal("1.0"),
                "color_code": "808080",
                "description": "Common Genesis NFT with standard cosmic properties"
            },
            RarityLevel.UNCOMMON: {
                "score": Decimal("2.5"),
                "color_code": "00FF00", 
                "description": "Uncommon Genesis NFT with enhanced stellar alignment"
            },
            RarityLevel.RARE: {
                "score": Decimal("5.0"),
                "color_code": "0080FF",
                "description": "Rare Genesis NFT with powerful cosmic resonance"
            },
            RarityLevel.EPIC: {
                "score": Decimal("10.0"),
                "color_code": "8000FF",
                "description": "Epic Genesis NFT with legendary cosmic forces"
            },
            RarityLevel.LEGENDARY: {
                "score": Decimal("25.0"),
                "color_code": "FF8000",
                "description": "Legendary Genesis NFT with ultimate cosmic power"
            }
        }
        
        config = rarity_configs.get(level, rarity_configs[RarityLevel.COMMON])
        return cls(
            level=level,
            score=config["score"],
            color_code=config["color_code"],
            description=config["description"]
        )
    
    def get_bonus_percentage(self) -> Decimal:
        """Calculate bonus percentage for gameplay"""
        bonus_map = {
            RarityLevel.COMMON: Decimal("5.0"),
            RarityLevel.UNCOMMON: Decimal("10.0"),
            RarityLevel.RARE: Decimal("15.0"),
            RarityLevel.EPIC: Decimal("25.0"),
            RarityLevel.LEGENDARY: Decimal("40.0")
        }
        return bonus_map.get(self.level, Decimal("5.0"))
    
    def is_higher_than(self, other: 'Rarity') -> bool:
        """Check if this rarity is higher than another"""
        return self.score > other.score


@dataclass(frozen=True)
class AchievementCriteria:
    """Value object for achievement requirements and validation"""
    achievement_type: AchievementType
    title: str
    description: str
    minimum_requirements: Dict[str, Any]
    bonus_requirements: Dict[str, Any]
    base_rarity: RarityLevel
    points_awarded: int
    
    def __post_init__(self):
        if not self.title or len(self.title.strip()) == 0:
            raise ValueError("Achievement title cannot be empty")
        if not self.description or len(self.description.strip()) == 0:
            raise ValueError("Achievement description cannot be empty")
        if self.points_awarded <= 0:
            raise ValueError("Points awarded must be positive")
        if len(self.minimum_requirements) == 0:
            raise ValueError("Achievement must have minimum requirements")
    
    @classmethod
    def create_first_trade(cls) -> 'AchievementCriteria':
        """Create criteria for first trade achievement"""
        return cls(
            achievement_type=AchievementType.FIRST_TRADE,
            title="Cosmic Genesis",
            description="Your first step into the cosmic trading realm",
            minimum_requirements={"trades_executed": 1},
            bonus_requirements={"profit_percentage": 10.0},
            base_rarity=RarityLevel.COMMON,
            points_awarded=100
        )
    
    @classmethod
    def create_level_milestone(cls, level: int) -> 'AchievementCriteria':
        """Create criteria for level milestone achievement"""
        return cls(
            achievement_type=AchievementType.LEVEL_MILESTONE,
            title=f"Stellar Ascension Level {level}",
            description=f"Reached the prestigious Level {level}",
            minimum_requirements={"user_level": level},
            bonus_requirements={"level_speed_bonus": level >= 50},
            base_rarity=RarityLevel.RARE if level >= 50 else RarityLevel.UNCOMMON,
            points_awarded=250 if level >= 50 else 150
        )
    
    @classmethod
    def create_constellation_founder(cls) -> 'AchievementCriteria':
        """Create criteria for constellation founder achievement"""
        return cls(
            achievement_type=AchievementType.CONSTELLATION_FOUNDER,
            title="Constellation Pioneer",
            description="Founded and lead a cosmic constellation",
            minimum_requirements={"constellation_role": "owner", "is_active": True},
            bonus_requirements={"member_count": 10, "constellation_level": 5},
            base_rarity=RarityLevel.EPIC,
            points_awarded=500
        )
    
    @classmethod
    def create_viral_legend(cls) -> 'AchievementCriteria':
        """Create criteria for viral legend achievement"""
        return cls(
            achievement_type=AchievementType.VIRAL_LEGEND,
            title="Cosmic Influencer",
            description="Created legendary viral content",
            minimum_requirements={"viral_content_count": 5, "min_viral_score": 500},
            bonus_requirements={"total_viral_score": 2000, "cross_platform": True},
            base_rarity=RarityLevel.EPIC,
            points_awarded=750
        )
    
    @classmethod
    def create_trading_master(cls) -> 'AchievementCriteria':
        """Create criteria for trading master achievement"""
        return cls(
            achievement_type=AchievementType.TRADING_MASTER,
            title="Cosmic Trading Sage",
            description="Mastered the art of cosmic trading",
            minimum_requirements={"total_trades": 1000, "win_rate": 0.8},
            bonus_requirements={"profit_amount": 100000, "consecutive_wins": 20},
            base_rarity=RarityLevel.LEGENDARY,
            points_awarded=1000
        )
    
    def calculate_final_rarity(self, user_stats: Dict[str, Any]) -> RarityLevel:
        """Calculate final rarity based on user stats and bonus requirements"""
        base_rarity = self.base_rarity
        
        # Check if user meets bonus requirements for rarity upgrade
        bonus_met = all(
            user_stats.get(key, 0) >= value if isinstance(value, (int, float)) else user_stats.get(key) == value
            for key, value in self.bonus_requirements.items()
        )
        
        if bonus_met:
            # Upgrade rarity by one level if possible
            rarity_order = [RarityLevel.COMMON, RarityLevel.UNCOMMON, RarityLevel.RARE, RarityLevel.EPIC, RarityLevel.LEGENDARY]
            current_index = rarity_order.index(base_rarity)
            if current_index < len(rarity_order) - 1:
                return rarity_order[current_index + 1]
        
        return base_rarity
    
    def is_eligible(self, user_stats: Dict[str, Any]) -> bool:
        """Check if user meets minimum requirements"""
        return all(
            user_stats.get(key, 0) >= value if isinstance(value, (int, float)) else user_stats.get(key) == value
            for key, value in self.minimum_requirements.items()
        )


@dataclass(frozen=True)
class NFTMetadata:
    """Value object for NFT metadata and properties"""
    name: str
    description: str
    image_url: str
    external_url: str
    attributes: List[Dict[str, Any]]
    background_color: str
    cosmic_properties: Dict[str, Any]
    
    def __post_init__(self):
        if not self.name or len(self.name.strip()) == 0:
            raise ValueError("NFT name cannot be empty")
        if not self.description or len(self.description.strip()) == 0:
            raise ValueError("NFT description cannot be empty")
        if not self.image_url or not self._is_valid_url(self.image_url):
            raise ValueError("Invalid image URL")
        if not self.external_url or not self._is_valid_url(self.external_url):
            raise ValueError("Invalid external URL")
        if len(self.attributes) == 0:
            raise ValueError("NFT must have at least one attribute")
        if not self.background_color or len(self.background_color) != 6:
            raise ValueError("Background color must be a 6-character hex string")
    
    def _is_valid_url(self, url: str) -> bool:
        """Basic URL validation"""
        return url.startswith(('http://', 'https://')) and len(url) > 10
    
    @classmethod
    def create_genesis_metadata(
        cls,
        achievement_type: AchievementType,
        rarity: Rarity,
        owner_level: int,
        milestone_data: Dict[str, Any],
        cosmic_signature: str
    ) -> 'NFTMetadata':
        """Create metadata for Genesis NFT"""
        achievement_name = achievement_type.value.replace('_', ' ').title()
        
        attributes = [
            {"trait_type": "Achievement", "value": achievement_name},
            {"trait_type": "Rarity", "value": rarity.level.value.title()},
            {"trait_type": "Power Level", "value": float(rarity.get_bonus_percentage())},
            {"trait_type": "Owner Level", "value": owner_level},
            {"trait_type": "Mint Date", "value": datetime.now(timezone.utc).strftime("%Y-%m-%d")},
            {"trait_type": "Genesis Series", "value": "Phase 1"}
        ]
        
        # Add milestone-specific attributes
        for key, value in milestone_data.items():
            if key not in ["cosmic_signature", "stellar_alignment"]:  # Skip internal data
                attributes.append({"trait_type": key.replace('_', ' ').title(), "value": value})
        
        cosmic_properties = {
            "stellar_alignment": cls._calculate_stellar_alignment(owner_level, milestone_data),
            "cosmic_resonance": cls._calculate_cosmic_resonance(rarity),
            "genesis_signature": cosmic_signature,
            "quantum_entropy": secrets.randbelow(1000) / 10.0  # 0-99.9
        }
        
        return cls(
            name=f"Genesis {achievement_name}",
            description=f"A {rarity.level.value} Genesis Seed NFT representing {achievement_name.lower()} achievement in the cosmic trading realm",
            image_url=f"https://astratrade.app/nft-images/genesis_{achievement_type.value}_{rarity.level.value}.png",
            external_url=f"https://astratrade.app/nft/genesis/{achievement_type.value}",
            attributes=attributes,
            background_color=rarity.color_code,
            cosmic_properties=cosmic_properties
        )
    
    @staticmethod
    def _calculate_stellar_alignment(level: int, milestone_data: Dict[str, Any]) -> float:
        """Calculate stellar alignment score"""
        base_alignment = min(level * 2.0, 100.0)
        trades = milestone_data.get("total_trades", 0)
        win_rate = milestone_data.get("win_rate", 0)
        
        bonus_alignment = min((trades / 100.0) + (win_rate * 20), 50.0)
        return min(base_alignment + bonus_alignment, 150.0)  # Max 150
    
    @staticmethod
    def _calculate_cosmic_resonance(rarity: Rarity) -> float:
        """Calculate cosmic resonance based on rarity"""
        base_resonance = float(rarity.score) * 15.0
        variance = secrets.randbelow(21) - 10  # -10 to +10
        return max(0.0, base_resonance + variance)
    
    def get_attribute_value(self, trait_type: str) -> Any:
        """Get value of specific attribute"""
        for attr in self.attributes:
            if attr.get("trait_type") == trait_type:
                return attr.get("value")
        return None
    
    def get_market_value_estimate(self) -> Decimal:
        """Estimate market value based on attributes and rarity"""
        power_level = self.get_attribute_value("Power Level") or 1.0
        rarity_multiplier = {
            "Common": Decimal("1000"),
            "Uncommon": Decimal("2500"),
            "Rare": Decimal("5000"),
            "Epic": Decimal("15000"),
            "Legendary": Decimal("50000")
        }
        
        rarity_name = self.get_attribute_value("Rarity") or "Common"
        base_value = rarity_multiplier.get(rarity_name, Decimal("1000"))
        
        # Apply power level multiplier
        power_multiplier = Decimal(str(1.0 + (power_level / 100.0)))
        
        return base_value * power_multiplier


@dataclass(frozen=True)
class MarketplaceListing:
    """Value object for NFT marketplace listing details"""
    listing_id: str
    nft_token_id: int
    owner_id: int
    price: Decimal
    currency: MarketplaceCurrency
    status: ListingStatus
    listed_at: datetime
    expires_at: Optional[datetime] = None
    featured: bool = False
    description: Optional[str] = None
    
    def __post_init__(self):
        if not self.listing_id or len(self.listing_id) < 6:
            raise ValueError("Listing ID must be at least 6 characters")
        if self.price <= 0:
            raise ValueError("Listing price must be positive")
        if self.owner_id <= 0:
            raise ValueError("Owner ID must be positive")
        if self.expires_at and self.expires_at <= self.listed_at:
            raise ValueError("Expiry date must be after listing date")
    
    @classmethod
    def create_listing(
        cls,
        nft_token_id: int,
        owner_id: int,
        price: Decimal,
        currency: MarketplaceCurrency,
        duration_days: int = 30,
        featured: bool = False,
        description: Optional[str] = None
    ) -> 'MarketplaceListing':
        """Create a new marketplace listing"""
        now = datetime.now(timezone.utc)
        listing_id = cls._generate_listing_id(nft_token_id, owner_id)
        expires_at = now + timedelta(days=duration_days)
        
        return cls(
            listing_id=listing_id,
            nft_token_id=nft_token_id,
            owner_id=owner_id,
            price=price,
            currency=currency,
            status=ListingStatus.ACTIVE,
            listed_at=now,
            expires_at=expires_at,
            featured=featured,
            description=description
        )
    
    @staticmethod
    def _generate_listing_id(nft_token_id: int, owner_id: int) -> str:
        """Generate unique listing ID"""
        timestamp = int(datetime.now(timezone.utc).timestamp())
        data = f"{nft_token_id}_{owner_id}_{timestamp}"
        hash_obj = hashlib.sha256(data.encode())
        return f"listing_{hash_obj.hexdigest()[:12]}"
    
    def is_active(self) -> bool:
        """Check if listing is currently active"""
        return self.status == ListingStatus.ACTIVE and not self.is_expired()
    
    def is_expired(self) -> bool:
        """Check if listing has expired"""
        if not self.expires_at:
            return False
        
        now = datetime.now(timezone.utc)
        expires = self.expires_at
        if expires.tzinfo is None:
            expires = expires.replace(tzinfo=timezone.utc)
        
        return now > expires
    
    def days_until_expiry(self) -> Optional[int]:
        """Get days until listing expires"""
        if not self.expires_at or self.is_expired():
            return None
        
        now = datetime.now(timezone.utc)
        expires = self.expires_at
        if expires.tzinfo is None:
            expires = expires.replace(tzinfo=timezone.utc)
        
        return (expires - now).days
    
    def get_currency_display_name(self) -> str:
        """Get display name for currency"""
        currency_names = {
            MarketplaceCurrency.STELLAR_SHARDS: "Stellar Shards",
            MarketplaceCurrency.LUMINA: "Lumina",
            MarketplaceCurrency.STARKNET_ETH: "ETH"
        }
        return currency_names.get(self.currency, self.currency.value)


@dataclass(frozen=True)
class CollectionStats:
    """Value object for NFT collection statistics"""
    total_nfts: int
    unique_achievements: int
    rarity_distribution: Dict[str, int]
    total_rarity_score: Decimal
    estimated_value: Dict[str, Decimal]
    completion_percentage: Decimal
    
    def __post_init__(self):
        if self.total_nfts < 0:
            raise ValueError("Total NFTs cannot be negative")
        if self.unique_achievements < 0:
            raise ValueError("Unique achievements cannot be negative")
        if self.total_rarity_score < 0:
            raise ValueError("Total rarity score cannot be negative")
        if not (0 <= self.completion_percentage <= 100):
            raise ValueError("Completion percentage must be between 0 and 100")
    
    @classmethod
    def calculate_from_nfts(cls, nfts: List[Dict[str, Any]]) -> 'CollectionStats':
        """Calculate collection stats from list of NFTs"""
        if not nfts:
            return cls(
                total_nfts=0,
                unique_achievements=0,
                rarity_distribution={},
                total_rarity_score=Decimal("0"),
                estimated_value={"stellar_shards": Decimal("0"), "lumina": Decimal("0")},
                completion_percentage=Decimal("0")
            )
        
        # Count rarities
        rarity_distribution = {}
        total_rarity_score = Decimal("0")
        unique_achievements = set()
        
        for nft in nfts:
            rarity = nft.get("rarity", "common")
            achievement = nft.get("achievement_type", "unknown")
            
            rarity_distribution[rarity] = rarity_distribution.get(rarity, 0) + 1
            unique_achievements.add(achievement)
            
            # Add rarity score
            rarity_scores = {
                "common": Decimal("1.0"),
                "uncommon": Decimal("2.5"),
                "rare": Decimal("5.0"),
                "epic": Decimal("10.0"),
                "legendary": Decimal("25.0")
            }
            total_rarity_score += rarity_scores.get(rarity, Decimal("1.0"))
        
        # Calculate estimated values
        base_values = {
            "common": Decimal("1000"),
            "uncommon": Decimal("2500"),
            "rare": Decimal("5000"),
            "epic": Decimal("15000"),
            "legendary": Decimal("50000")
        }
        
        total_ss_value = Decimal("0")
        for rarity, count in rarity_distribution.items():
            total_ss_value += base_values.get(rarity, Decimal("1000")) * count
        
        total_lumina_value = total_ss_value * Decimal("0.2")  # 1 LM = 5 SS
        
        # Calculate completion percentage (out of 5 possible achievement types)
        completion_percentage = (Decimal(len(unique_achievements)) / Decimal("5")) * Decimal("100")
        
        return cls(
            total_nfts=len(nfts),
            unique_achievements=len(unique_achievements),
            rarity_distribution=rarity_distribution,
            total_rarity_score=total_rarity_score,
            estimated_value={
                "stellar_shards": total_ss_value,
                "lumina": total_lumina_value
            },
            completion_percentage=completion_percentage
        )
    
    def get_average_rarity_score(self) -> Decimal:
        """Get average rarity score per NFT"""
        if self.total_nfts == 0:
            return Decimal("0")
        return self.total_rarity_score / Decimal(self.total_nfts)
    
    def get_dominant_rarity(self) -> str:
        """Get the most common rarity in collection"""
        if not self.rarity_distribution:
            return "common"
        return max(self.rarity_distribution.items(), key=lambda x: x[1])[0]
    
    def get_collection_tier(self) -> str:
        """Determine overall collection tier"""
        avg_score = self.get_average_rarity_score()
        
        if avg_score >= Decimal("15.0"):
            return "legendary"
        elif avg_score >= Decimal("8.0"):
            return "epic"
        elif avg_score >= Decimal("4.0"):
            return "rare"
        elif avg_score >= Decimal("2.0"):
            return "uncommon"
        else:
            return "common"


@dataclass(frozen=True)
class NFTRoyalty:
    """Value object for NFT royalty and fee calculation"""
    platform_fee_percentage: Decimal
    creator_royalty_percentage: Decimal
    transaction_fee: Decimal
    currency: MarketplaceCurrency
    
    def __post_init__(self):
        if self.platform_fee_percentage < 0 or self.platform_fee_percentage > 100:
            raise ValueError("Platform fee percentage must be between 0 and 100")
        if self.creator_royalty_percentage < 0 or self.creator_royalty_percentage > 100:
            raise ValueError("Creator royalty percentage must be between 0 and 100")
        if self.transaction_fee < 0:
            raise ValueError("Transaction fee cannot be negative")
        if (self.platform_fee_percentage + self.creator_royalty_percentage) > 100:
            raise ValueError("Total fees cannot exceed 100%")
    
    @classmethod
    def create_default_royalty(cls, currency: MarketplaceCurrency) -> 'NFTRoyalty':
        """Create default royalty structure"""
        return cls(
            platform_fee_percentage=Decimal("2.5"),  # 2.5% platform fee
            creator_royalty_percentage=Decimal("5.0"),  # 5% creator royalty
            transaction_fee=Decimal("5.0"),  # Fixed transaction fee
            currency=currency
        )
    
    @classmethod
    def create_genesis_royalty(cls, currency: MarketplaceCurrency) -> 'NFTRoyalty':
        """Create royalty structure for Genesis NFTs"""
        return cls(
            platform_fee_percentage=Decimal("2.5"),  # 2.5% platform fee
            creator_royalty_percentage=Decimal("0.0"),  # No creator royalty for Genesis
            transaction_fee=Decimal("5.0"),  # Fixed transaction fee
            currency=currency
        )
    
    def calculate_fees(self, sale_price: Decimal) -> Dict[str, Decimal]:
        """Calculate all fees from sale price"""
        if sale_price <= 0:
            raise ValueError("Sale price must be positive")
        
        platform_fee = sale_price * (self.platform_fee_percentage / Decimal("100"))
        creator_royalty = sale_price * (self.creator_royalty_percentage / Decimal("100"))
        total_fees = platform_fee + creator_royalty + self.transaction_fee
        seller_proceeds = sale_price - total_fees
        
        return {
            "platform_fee": platform_fee,
            "creator_royalty": creator_royalty,
            "transaction_fee": self.transaction_fee,
            "total_fees": total_fees,
            "seller_proceeds": max(Decimal("0"), seller_proceeds),  # Ensure non-negative
            "sale_price": sale_price
        }
    
    def get_total_fee_percentage(self) -> Decimal:
        """Get total percentage-based fees"""
        return self.platform_fee_percentage + self.creator_royalty_percentage
    
    def get_minimum_viable_price(self) -> Decimal:
        """Get minimum price that covers transaction fees"""
        # Minimum price where seller gets at least the transaction fee back
        percentage_fees = self.get_total_fee_percentage() / Decimal("100")
        if percentage_fees >= Decimal("1.0"):
            raise ValueError("Total percentage fees exceed 100%, no viable minimum price")
        
        return self.transaction_fee / (Decimal("1.0") - percentage_fees)


@dataclass(frozen=True)
class NFTAttributes:
    """Value object for NFT attributes and traits management"""
    traits: List[Dict[str, Any]]
    cosmic_properties: Dict[str, Any]
    rarity_boost: Decimal
    special_properties: List[str]
    
    def __post_init__(self):
        if not self.traits:
            raise ValueError("NFT must have at least one trait")
        if self.rarity_boost < 0:
            raise ValueError("Rarity boost cannot be negative")
        
        # Validate trait structure
        for trait in self.traits:
            if not isinstance(trait, dict) or "trait_type" not in trait or "value" not in trait:
                raise ValueError("Each trait must have 'trait_type' and 'value' keys")
    
    @classmethod
    def create_from_achievement(
        cls,
        achievement_type: AchievementType,
        rarity: 'Rarity',
        owner_level: int,
        milestone_data: Dict[str, Any],
        cosmic_signature: str
    ) -> 'NFTAttributes':
        """Create attributes for achievement-based NFT"""
        achievement_name = achievement_type.value.replace('_', ' ').title()
        
        base_traits = [
            {"trait_type": "Achievement", "value": achievement_name},
            {"trait_type": "Rarity", "value": rarity.level.value.title()},
            {"trait_type": "Power Level", "value": float(rarity.get_bonus_percentage())},
            {"trait_type": "Owner Level", "value": owner_level},
            {"trait_type": "Mint Date", "value": datetime.now(timezone.utc).strftime("%Y-%m-%d")},
            {"trait_type": "Genesis Series", "value": "Phase 1"}
        ]
        
        # Add milestone-specific traits
        for key, value in milestone_data.items():
            if key not in ["cosmic_signature", "stellar_alignment"]:
                base_traits.append({
                    "trait_type": key.replace('_', ' ').title(),
                    "value": value
                })
        
        cosmic_properties = {
            "stellar_alignment": cls._calculate_stellar_alignment(owner_level, milestone_data),
            "cosmic_resonance": cls._calculate_cosmic_resonance(rarity),
            "genesis_signature": cosmic_signature,
            "quantum_entropy": secrets.randbelow(1000) / 10.0
        }
        
        special_properties = cls._determine_special_properties(achievement_type, rarity, milestone_data)
        
        return cls(
            traits=base_traits,
            cosmic_properties=cosmic_properties,
            rarity_boost=rarity.get_bonus_percentage(),
            special_properties=special_properties
        )
    
    @staticmethod
    def _calculate_stellar_alignment(level: int, milestone_data: Dict[str, Any]) -> float:
        """Calculate stellar alignment score"""
        base_alignment = min(level * 2.0, 100.0)
        trades = milestone_data.get("total_trades", 0)
        win_rate = milestone_data.get("win_rate", 0)
        
        bonus_alignment = min((trades / 100.0) + (win_rate * 20), 50.0)
        return min(base_alignment + bonus_alignment, 150.0)
    
    @staticmethod
    def _calculate_cosmic_resonance(rarity: 'Rarity') -> float:
        """Calculate cosmic resonance based on rarity"""
        base_resonance = float(rarity.score) * 15.0
        variance = secrets.randbelow(21) - 10  # -10 to +10
        return max(0.0, base_resonance + variance)
    
    @staticmethod
    def _determine_special_properties(
        achievement_type: AchievementType,
        rarity: 'Rarity',
        milestone_data: Dict[str, Any]
    ) -> List[str]:
        """Determine special properties based on achievement and rarity"""
        properties = []
        
        # Achievement-specific properties
        if achievement_type == AchievementType.CONSTELLATION_FOUNDER:
            properties.append("Leadership Aura")
        elif achievement_type == AchievementType.TRADING_MASTER:
            properties.append("Market Oracle")
        elif achievement_type == AchievementType.VIRAL_LEGEND:
            properties.append("Influence Amplifier")
        
        # Rarity-specific properties
        if rarity.level == RarityLevel.LEGENDARY:
            properties.extend(["Cosmic Mastery", "Reality Bender"])
        elif rarity.level == RarityLevel.EPIC:
            properties.append("Stellar Authority")
        elif rarity.level == RarityLevel.RARE:
            properties.append("Celestial Insight")
        
        # Performance-based properties
        win_rate = milestone_data.get("win_rate", 0)
        if win_rate >= 0.9:
            properties.append("Perfect Strategist")
        elif win_rate >= 0.8:
            properties.append("Master Tactician")
        
        return properties
    
    def get_trait_value(self, trait_type: str) -> Any:
        """Get value of specific trait"""
        for trait in self.traits:
            if trait.get("trait_type") == trait_type:
                return trait.get("value")
        return None
    
    def has_special_property(self, property_name: str) -> bool:
        """Check if NFT has specific special property"""
        return property_name in self.special_properties
    
    def get_total_power_score(self) -> Decimal:
        """Calculate total power score from all attributes"""
        base_power = self.rarity_boost
        
        # Add cosmic property bonuses
        stellar_alignment = self.cosmic_properties.get("stellar_alignment", 0)
        cosmic_resonance = self.cosmic_properties.get("cosmic_resonance", 0)
        
        cosmic_bonus = Decimal(str((stellar_alignment + cosmic_resonance) / 10.0))
        special_bonus = Decimal(str(len(self.special_properties) * 5))
        
        return base_power + cosmic_bonus + special_bonus
    
    def get_market_value_multiplier(self) -> Decimal:
        """Get market value multiplier based on attributes"""
        base_multiplier = Decimal("1.0")
        
        # Special property bonuses
        for prop in self.special_properties:
            if prop in ["Cosmic Mastery", "Reality Bender"]:
                base_multiplier += Decimal("0.5")
            elif prop in ["Stellar Authority", "Market Oracle"]:
                base_multiplier += Decimal("0.3")
            else:
                base_multiplier += Decimal("0.1")
        
        # Cosmic properties bonus
        quantum_entropy = self.cosmic_properties.get("quantum_entropy", 50)
        if quantum_entropy >= 90:
            base_multiplier += Decimal("0.2")
        elif quantum_entropy >= 80:
            base_multiplier += Decimal("0.1")
        
        return base_multiplier


@dataclass(frozen=True)
class BlockchainTransaction:
    """Value object for blockchain transaction details"""
    transaction_hash: str
    block_number: int
    gas_used: int
    contract_address: str
    token_id: Optional[int] = None
    status: str = "confirmed"
    timestamp: Optional[datetime] = None
    
    def __post_init__(self):
        if not self.transaction_hash or len(self.transaction_hash) < 10:
            raise ValueError("Transaction hash must be at least 10 characters")
        if self.block_number <= 0:
            raise ValueError("Block number must be positive")
        if self.gas_used <= 0:
            raise ValueError("Gas used must be positive")
        if not self.contract_address or len(self.contract_address) < 10:
            raise ValueError("Contract address must be at least 10 characters")
        if self.token_id is not None and self.token_id <= 0:
            raise ValueError("Token ID must be positive")
    
    @classmethod
    def create_mock_transaction(cls, token_id: int, operation: str = "mint") -> 'BlockchainTransaction':
        """Create mock transaction for development/testing"""
        return cls(
            transaction_hash=f"0x{secrets.token_hex(32)}",
            block_number=1000000 + token_id,
            gas_used=150000 if operation == "mint" else 80000,
            contract_address="0x1234567890abcdef1234567890abcdef12345678",
            token_id=token_id,
            status="confirmed",
            timestamp=datetime.now(timezone.utc)
        )
    
    def is_confirmed(self) -> bool:
        """Check if transaction is confirmed"""
        return self.status.lower() == "confirmed"
    
    def get_explorer_url(self) -> str:
        """Get blockchain explorer URL for transaction"""
        # For StarkNet
        return f"https://starkscan.co/tx/{self.transaction_hash}"
    
    def get_estimated_cost_usd(self) -> Decimal:
        """Get estimated transaction cost in USD (mock)"""
        # Mock calculation based on gas used
        eth_price = Decimal("2000")  # Mock ETH price
        gas_price_gwei = Decimal("20")  # Mock gas price
        wei_per_gwei = Decimal("1000000000")
        wei_per_eth = Decimal("1000000000000000000")
        
        cost_wei = Decimal(self.gas_used) * gas_price_gwei * wei_per_gwei
        cost_eth = cost_wei / wei_per_eth
        cost_usd = cost_eth * eth_price
        
        return cost_usd