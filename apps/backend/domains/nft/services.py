"""
NFT Domain Services

Domain services for the NFT Domain implementing complex business operations
that span multiple entities or integrate with external systems.
"""

from datetime import datetime, timezone, timedelta
from decimal import Decimal
from typing import List, Optional, Dict, Any, Protocol
from abc import ABC, abstractmethod
import secrets

from entities import GenesisNFT, NFTCollection, MarketplaceItem, DomainEvent
from value_objects import (
    AchievementType, RarityLevel, NFTStatus, MarketplaceCurrency, ListingStatus,
    Rarity, AchievementCriteria, NFTMetadata, MarketplaceListing, CollectionStats,
    BlockchainTransaction, NFTRoyalty, NFTAttributes
)


# Repository Interfaces (following Dependency Inversion Principle)
class NFTRepositoryInterface(ABC):
    """Interface for NFT persistence operations"""
    
    @abstractmethod
    def save(self, nft: GenesisNFT) -> None:
        pass
    
    @abstractmethod
    def find_by_id(self, nft_id: str) -> Optional[GenesisNFT]:
        pass
    
    @abstractmethod
    def find_by_owner(self, owner_id: int) -> List[GenesisNFT]:
        pass
    
    @abstractmethod
    def find_by_achievement_type(self, achievement_type: AchievementType) -> List[GenesisNFT]:
        pass
    
    @abstractmethod
    def find_by_rarity(self, rarity_level: RarityLevel) -> List[GenesisNFT]:
        pass


class CollectionRepositoryInterface(ABC):
    """Interface for collection persistence operations"""
    
    @abstractmethod
    def save(self, collection: NFTCollection) -> None:
        pass
    
    @abstractmethod
    def find_by_id(self, collection_id: str) -> Optional[NFTCollection]:
        pass
    
    @abstractmethod
    def find_by_owner(self, owner_id: int) -> Optional[NFTCollection]:
        pass
    
    @abstractmethod
    def find_public_collections(self, limit: int) -> List[NFTCollection]:
        pass


class MarketplaceRepositoryInterface(ABC):
    """Interface for marketplace persistence operations"""
    
    @abstractmethod
    def save(self, item: MarketplaceItem) -> None:
        pass
    
    @abstractmethod
    def find_by_id(self, item_id: str) -> Optional[MarketplaceItem]:
        pass
    
    @abstractmethod
    def find_active_listings(self, filters: Dict[str, Any]) -> List[MarketplaceItem]:
        pass
    
    @abstractmethod
    def find_trending_items(self, limit: int) -> List[MarketplaceItem]:
        pass


class BlockchainServiceInterface(ABC):
    """Interface for blockchain integration"""
    
    @abstractmethod
    def mint_nft(self, nft_data: Dict[str, Any]) -> BlockchainTransaction:
        pass
    
    @abstractmethod
    def transfer_nft(self, token_id: int, from_address: str, to_address: str) -> BlockchainTransaction:
        pass
    
    @abstractmethod
    def get_transaction_status(self, tx_hash: str) -> str:
        pass


class PaymentServiceInterface(ABC):
    """Interface for payment processing integration"""
    
    @abstractmethod
    def process_marketplace_payment(self, buyer_id: int, amount: Decimal, currency: str) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def transfer_seller_proceeds(self, seller_id: int, amount: Decimal, currency: str) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def collect_platform_fee(self, amount: Decimal, currency: str) -> Dict[str, Any]:
        pass


class NotificationServiceInterface(ABC):
    """Interface for sending notifications"""
    
    @abstractmethod
    def send_nft_minted_notification(self, user_id: int, nft: GenesisNFT) -> None:
        pass
    
    @abstractmethod
    def send_nft_sold_notification(self, seller_id: int, buyer_id: int, sale_data: Dict[str, Any]) -> None:
        pass
    
    @abstractmethod
    def send_listing_expired_notification(self, user_id: int, listing: MarketplaceListing) -> None:
        pass


# Builder Pattern
class GenesisNFTBuilder:
    """
    Builder for creating Genesis NFT entities with controlled construction
    
    Provides a fluent interface for building Genesis NFTs with proper validation
    and business rule enforcement at each step.
    """
    
    def __init__(self):
        self.reset()
    
    def reset(self) -> 'GenesisNFTBuilder':
        """Reset builder to initial state"""
        self._owner_id: Optional[int] = None
        self._achievement_type: Optional[AchievementType] = None
        self._rarity: Optional[Rarity] = None
        self._metadata: Optional[NFTMetadata] = None
        self._attributes: Optional[NFTAttributes] = None
        self._royalty: Optional[NFTRoyalty] = None
        self._status: NFTStatus = NFTStatus.PENDING_MINT
        self._nft_id: Optional[str] = None
        return self
    
    def with_owner(self, owner_id: int) -> 'GenesisNFTBuilder':
        """Set NFT owner"""
        if owner_id <= 0:
            raise ValueError("Owner ID must be positive")
        self._owner_id = owner_id
        return self
    
    def with_achievement(self, achievement_type: AchievementType) -> 'GenesisNFTBuilder':
        """Set achievement type"""
        self._achievement_type = achievement_type
        return self
    
    def with_rarity(self, rarity: Rarity) -> 'GenesisNFTBuilder':
        """Set NFT rarity"""
        self._rarity = rarity
        return self
    
    def with_auto_rarity(self, achievement_type: AchievementType, user_stats: Dict[str, Any]) -> 'GenesisNFTBuilder':
        """Automatically determine rarity based on achievement and user stats"""
        criteria = self._get_achievement_criteria(achievement_type, user_stats)
        final_rarity_level = criteria.calculate_final_rarity(user_stats)
        self._rarity = Rarity.from_level(final_rarity_level)
        return self
    
    def with_metadata(self, metadata: NFTMetadata) -> 'GenesisNFTBuilder':
        """Set NFT metadata"""
        self._metadata = metadata
        return self
    
    def with_auto_metadata(
        self,
        owner_level: int,
        milestone_data: Dict[str, Any],
        cosmic_signature: Optional[str] = None
    ) -> 'GenesisNFTBuilder':
        """Automatically generate metadata"""
        if not self._achievement_type or not self._rarity:
            raise ValueError("Achievement type and rarity must be set before generating metadata")
        
        if not cosmic_signature:
            cosmic_signature = self._generate_cosmic_signature()
        
        self._metadata = NFTMetadata.create_genesis_metadata(
            achievement_type=self._achievement_type,
            rarity=self._rarity,
            owner_level=owner_level,
            milestone_data=milestone_data,
            cosmic_signature=cosmic_signature
        )
        return self
    
    def with_attributes(self, attributes: NFTAttributes) -> 'GenesisNFTBuilder':
        """Set NFT attributes"""
        self._attributes = attributes
        return self
    
    def with_auto_attributes(
        self,
        owner_level: int,
        milestone_data: Dict[str, Any],
        cosmic_signature: Optional[str] = None
    ) -> 'GenesisNFTBuilder':
        """Automatically generate attributes"""
        if not self._achievement_type or not self._rarity:
            raise ValueError("Achievement type and rarity must be set before generating attributes")
        
        if not cosmic_signature:
            cosmic_signature = self._generate_cosmic_signature()
        
        self._attributes = NFTAttributes.create_from_achievement(
            achievement_type=self._achievement_type,
            rarity=self._rarity,
            owner_level=owner_level,
            milestone_data=milestone_data,
            cosmic_signature=cosmic_signature
        )
        return self
    
    def with_royalty(self, royalty: NFTRoyalty) -> 'GenesisNFTBuilder':
        """Set NFT royalty structure"""
        self._royalty = royalty
        return self
    
    def with_genesis_royalty(self, currency: MarketplaceCurrency) -> 'GenesisNFTBuilder':
        """Set default Genesis NFT royalty structure"""
        self._royalty = NFTRoyalty.create_genesis_royalty(currency)
        return self
    
    def with_nft_id(self, nft_id: Optional[str] = None) -> 'GenesisNFTBuilder':
        """Set or generate NFT ID"""
        if nft_id:
            self._nft_id = nft_id
        else:
            if not self._owner_id or not self._achievement_type:
                raise ValueError("Owner ID and achievement type must be set before generating NFT ID")
            self._nft_id = self._generate_nft_id()
        return self
    
    def build(self) -> GenesisNFT:
        """Build the Genesis NFT"""
        self._validate_build_requirements()
        
        # Create the NFT entity
        genesis_nft = GenesisNFT(
            owner_id=self._owner_id,
            achievement_type=self._achievement_type,
            rarity=self._rarity,
            metadata=self._metadata,
            status=self._status
        )
        
        # Set NFT ID if provided
        if self._nft_id:
            genesis_nft.set_nft_id(self._nft_id)
        
        return genesis_nft
    
    def build_for_minting(
        self,
        owner_level: int,
        milestone_data: Dict[str, Any],
        user_stats: Dict[str, Any]
    ) -> GenesisNFT:
        """Build a complete Genesis NFT ready for minting"""
        if not self._owner_id or not self._achievement_type:
            raise ValueError("Owner ID and achievement type must be set")
        
        cosmic_signature = self._generate_cosmic_signature()
        
        # Auto-configure everything needed for minting
        return (self
                .with_auto_rarity(self._achievement_type, user_stats)
                .with_auto_metadata(owner_level, milestone_data, cosmic_signature)
                .with_auto_attributes(owner_level, milestone_data, cosmic_signature)
                .with_genesis_royalty(MarketplaceCurrency.STELLAR_SHARDS)
                .with_nft_id()
                .build())
    
    def _validate_build_requirements(self) -> None:
        """Validate that all required fields are set"""
        if not self._owner_id:
            raise ValueError("Owner ID is required")
        if not self._achievement_type:
            raise ValueError("Achievement type is required")
        if not self._rarity:
            raise ValueError("Rarity is required")
    
    def _generate_nft_id(self) -> str:
        """Generate unique NFT ID"""
        timestamp = int(datetime.now(timezone.utc).timestamp())
        unique_string = f"{self._owner_id}_{self._achievement_type.value}_{timestamp}_{secrets.token_hex(4)}"
        return f"GENESIS_{unique_string.upper()}"
    
    def _generate_cosmic_signature(self) -> str:
        """Generate unique cosmic signature"""
        if not self._owner_id or not self._achievement_type:
            raise ValueError("Owner ID and achievement type required for cosmic signature")
        
        data = f"{self._owner_id}_{self._achievement_type.value}_{datetime.now(timezone.utc).timestamp()}"
        return secrets.token_hex(16)
    
    def _get_achievement_criteria(self, achievement_type: AchievementType, milestone_data: Dict[str, Any]) -> AchievementCriteria:
        """Get achievement criteria for given type"""
        if achievement_type == AchievementType.FIRST_TRADE:
            return AchievementCriteria.create_first_trade()
        elif achievement_type == AchievementType.LEVEL_MILESTONE:
            level = milestone_data.get("level", 25)
            return AchievementCriteria.create_level_milestone(level)
        elif achievement_type == AchievementType.CONSTELLATION_FOUNDER:
            return AchievementCriteria.create_constellation_founder()
        elif achievement_type == AchievementType.VIRAL_LEGEND:
            return AchievementCriteria.create_viral_legend()
        elif achievement_type == AchievementType.TRADING_MASTER:
            return AchievementCriteria.create_trading_master()
        else:
            raise ValueError(f"Unknown achievement type: {achievement_type}")


# Domain Services
class NFTMintingService:
    """
    Domain service for NFT minting operations
    
    Handles Genesis NFT creation, eligibility validation, and minting process.
    Coordinates between achievement validation, blockchain minting, and collection management.
    """
    
    def __init__(
        self,
        nft_repository: NFTRepositoryInterface,
        collection_repository: CollectionRepositoryInterface,
        blockchain_service: BlockchainServiceInterface,
        notification_service: NotificationServiceInterface
    ):
        self.nft_repository = nft_repository
        self.collection_repository = collection_repository
        self.blockchain_service = blockchain_service
        self.notification_service = notification_service
    
    def mint_genesis_nft(
        self,
        user_id: int,
        achievement_type: AchievementType,
        user_stats: Dict[str, Any],
        milestone_data: Dict[str, Any]
    ) -> GenesisNFT:
        """Mint a Genesis NFT for achievement"""
        
        # Get achievement criteria
        criteria = self._get_achievement_criteria(achievement_type, milestone_data)
        
        # Validate eligibility
        if not criteria.is_eligible(user_stats):
            raise ValueError(f"User not eligible for {achievement_type.value} achievement")
        
        # Check if user already has this achievement NFT
        existing_nfts = self.nft_repository.find_by_owner(user_id)
        if any(nft.achievement_type == achievement_type for nft in existing_nfts):
            raise ValueError(f"User already has {achievement_type.value} Genesis NFT")
        
        # Create Genesis NFT using builder
        builder = GenesisNFTBuilder()
        genesis_nft = builder.with_owner(user_id).with_achievement(achievement_type).build_for_minting(
            owner_level=user_stats.get("user_level", 1),
            milestone_data=milestone_data,
            user_stats=user_stats
        )
        
        # Mint on blockchain
        blockchain_data = {
            "owner_id": user_id,
            "achievement_type": achievement_type.value,
            "rarity": rarity.level.value,
            "metadata": milestone_data
        }
        
        try:
            blockchain_tx = self.blockchain_service.mint_nft(blockchain_data)
            
            # Complete minting process with simplified method
            genesis_nft.mint_nft(blockchain_tx)
            
            # Save NFT
            self.nft_repository.save(genesis_nft)
            
            # Add to user's collection
            self._add_to_user_collection(user_id, genesis_nft)
            
            # Send notification
            self.notification_service.send_nft_minted_notification(user_id, genesis_nft)
            
            return genesis_nft
            
        except Exception as e:
            raise ValueError(f"Failed to mint Genesis NFT: {str(e)}")
    
    def validate_achievement_eligibility(
        self,
        user_id: int,
        achievement_type: AchievementType,
        user_stats: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate if user is eligible for achievement NFT"""
        
        criteria = self._get_achievement_criteria(achievement_type, {})
        is_eligible = criteria.is_eligible(user_stats)
        
        # Check existing NFTs
        existing_nfts = self.nft_repository.find_by_owner(user_id)
        already_has_nft = any(nft.achievement_type == achievement_type for nft in existing_nfts)
        
        final_rarity = criteria.calculate_final_rarity(user_stats) if is_eligible else None
        
        return {
            "eligible": is_eligible and not already_has_nft,
            "already_owns": already_has_nft,
            "criteria_met": is_eligible,
            "requirements": criteria.minimum_requirements,
            "bonus_requirements": criteria.bonus_requirements,
            "final_rarity": final_rarity.value if final_rarity else None,
            "points_awarded": criteria.points_awarded,
            "reason": self._get_eligibility_reason(is_eligible, already_has_nft, criteria, user_stats)
        }
    
    def get_all_eligible_achievements(self, user_id: int, user_stats: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get all achievements user is eligible for"""
        eligible_achievements = []
        
        for achievement_type in AchievementType:
            eligibility = self.validate_achievement_eligibility(user_id, achievement_type, user_stats)
            if eligibility["eligible"]:
                criteria = self._get_achievement_criteria(achievement_type, {})
                eligible_achievements.append({
                    "achievement_type": achievement_type.value,
                    "title": criteria.title,
                    "description": criteria.description,
                    "rarity": eligibility["final_rarity"],
                    "points": criteria.points_awarded,
                    "requirements_met": True
                })
        
        return eligible_achievements
    
    def _get_achievement_criteria(self, achievement_type: AchievementType, milestone_data: Dict[str, Any]) -> AchievementCriteria:
        """Get achievement criteria for given type"""
        if achievement_type == AchievementType.FIRST_TRADE:
            return AchievementCriteria.create_first_trade()
        elif achievement_type == AchievementType.LEVEL_MILESTONE:
            level = milestone_data.get("level", 25)
            return AchievementCriteria.create_level_milestone(level)
        elif achievement_type == AchievementType.CONSTELLATION_FOUNDER:
            return AchievementCriteria.create_constellation_founder()
        elif achievement_type == AchievementType.VIRAL_LEGEND:
            return AchievementCriteria.create_viral_legend()
        elif achievement_type == AchievementType.TRADING_MASTER:
            return AchievementCriteria.create_trading_master()
        else:
            raise ValueError(f"Unknown achievement type: {achievement_type}")
    
    def _generate_nft_id(self, user_id: int, achievement_type: AchievementType) -> str:
        """Generate unique NFT ID"""
        timestamp = int(datetime.now(timezone.utc).timestamp())
        unique_string = f"{user_id}_{achievement_type.value}_{timestamp}_{secrets.token_hex(4)}"
        return f"GENESIS_{unique_string.upper()}"
    
    def _add_to_user_collection(self, user_id: int, genesis_nft: GenesisNFT) -> None:
        """Add NFT to user's collection"""
        collection = self.collection_repository.find_by_owner(user_id)
        
        if not collection:
            # Create new collection for user
            collection = NFTCollection(owner_id=user_id)
            collection_id = f"collection_{user_id}_{secrets.token_hex(6)}"
            collection.set_collection_id(collection_id)
        
        collection.add_nft(genesis_nft)
        self.collection_repository.save(collection)
    
    def _get_eligibility_reason(
        self,
        criteria_met: bool,
        already_has_nft: bool,
        criteria: AchievementCriteria,
        user_stats: Dict[str, Any]
    ) -> str:
        """Get human-readable eligibility reason"""
        if already_has_nft:
            return f"Already owns {criteria.title} Genesis NFT"
        elif not criteria_met:
            missing_requirements = []
            for key, required_value in criteria.minimum_requirements.items():
                user_value = user_stats.get(key, 0)
                if isinstance(required_value, (int, float)) and user_value < required_value:
                    missing_requirements.append(f"{key}: {user_value}/{required_value}")
                elif user_value != required_value:
                    missing_requirements.append(f"{key}: {user_value} (requires {required_value})")
            return f"Missing requirements: {', '.join(missing_requirements)}"
        else:
            return "Eligible for minting"


class MarketplaceService:
    """
    Domain service for NFT marketplace operations
    
    Handles listing, buying, selling, and marketplace analytics.
    Coordinates between NFT entities, payment processing, and revenue tracking.
    """
    
    def __init__(
        self,
        nft_repository: NFTRepositoryInterface,
        marketplace_repository: MarketplaceRepositoryInterface,
        payment_service: PaymentServiceInterface,
        notification_service: NotificationServiceInterface
    ):
        self.nft_repository = nft_repository
        self.marketplace_repository = marketplace_repository
        self.payment_service = payment_service
        self.notification_service = notification_service
    
    def list_nft_for_sale(
        self,
        nft_id: str,
        seller_id: int,
        price: Decimal,
        currency: MarketplaceCurrency,
        duration_days: int = 30,
        featured: bool = False,
        description: Optional[str] = None
    ) -> MarketplaceItem:
        """List NFT on marketplace"""
        
        # Get and validate NFT
        nft = self.nft_repository.find_by_id(nft_id)
        if not nft:
            raise ValueError("NFT not found")
        
        if not nft.is_owned_by(seller_id):
            raise ValueError("Only NFT owner can list for sale")
        
        if not nft.is_tradeable():
            raise ValueError("NFT is not in tradeable status")
        
        if nft.current_listing and nft.current_listing.is_active():
            raise ValueError("NFT is already listed on marketplace")
        
        # Create marketplace listing
        listing = nft.list_on_marketplace(
            price=price,
            currency=currency,
            duration_days=duration_days,
            featured=featured,
            description=description
        )
        
        # Create marketplace item
        marketplace_item = MarketplaceItem(
            genesis_nft=nft,
            listing=listing
        )
        
        item_id = self._generate_marketplace_item_id(nft_id)
        marketplace_item.set_item_id(item_id)
        
        # Save both NFT and marketplace item
        self.nft_repository.save(nft)
        self.marketplace_repository.save(marketplace_item)
        
        return marketplace_item
    
    def buy_nft(
        self,
        item_id: str,
        buyer_id: int,
        buyer_wallet_address: str
    ) -> Dict[str, Any]:
        """Purchase NFT from marketplace"""
        
        # Get marketplace item
        marketplace_item = self.marketplace_repository.find_by_id(item_id)
        if not marketplace_item:
            raise ValueError("Marketplace item not found")
        
        nft = marketplace_item.genesis_nft
        if not nft or not marketplace_item.listing:
            raise ValueError("Invalid marketplace item")
        
        if not marketplace_item.listing.is_active():
            raise ValueError("Listing is not active")
        
        if nft.is_owned_by(buyer_id):
            raise ValueError("Cannot buy your own NFT")
        
        # Process payment
        listing = marketplace_item.listing
        try:
            payment_result = self.payment_service.process_marketplace_payment(
                buyer_id=buyer_id,
                amount=listing.price,
                currency=listing.currency.value
            )
            
            if not payment_result.get("success"):
                raise ValueError(f"Payment failed: {payment_result.get('error')}")
            
            # Ensure NFT has royalty structure
            if not nft.royalty:
                nft.royalty = NFTRoyalty.create_genesis_royalty(listing.currency)
            
            # Process sale using simplified method
            sale_record = nft.sell_to_buyer(
                buyer_id=buyer_id,
                sale_price=listing.price,
                currency=listing.currency
            )
            
            # Transfer seller proceeds
            seller_proceeds = sale_record["seller_proceeds"]
            self.payment_service.transfer_seller_proceeds(
                seller_id=sale_record["seller_id"],
                amount=seller_proceeds,
                currency=listing.currency.value
            )
            
            # Collect platform fee
            platform_fee = sale_record["platform_fee"]
            self.payment_service.collect_platform_fee(
                amount=platform_fee,
                currency=listing.currency.value
            )
            
            # Update marketplace item
            marketplace_item.listing = None  # Clear listing since sold
            
            # Save updates
            self.nft_repository.save(nft)
            self.marketplace_repository.save(marketplace_item)
            
            # Send notifications
            self.notification_service.send_nft_sold_notification(
                seller_id=sale_record["seller_id"],
                buyer_id=buyer_id,
                sale_data=sale_record
            )
            
            return {
                "success": True,
                "sale_record": sale_record,
                "payment_transaction": payment_result["transaction_id"],
                "new_owner": buyer_id
            }
            
        except Exception as e:
            raise ValueError(f"Purchase failed: {str(e)}")
    
    def unlist_nft(self, nft_id: str, owner_id: int, reason: str = "owner_request") -> None:
        """Remove NFT from marketplace"""
        
        nft = self.nft_repository.find_by_id(nft_id)
        if not nft:
            raise ValueError("NFT not found")
        
        if not nft.is_owned_by(owner_id):
            raise ValueError("Only NFT owner can unlist")
        
        if not nft.current_listing or not nft.current_listing.is_active():
            raise ValueError("NFT is not currently listed")
        
        # Unlist NFT
        nft.unlist_from_marketplace(reason)
        
        # Update marketplace item
        marketplace_items = self.marketplace_repository.find_active_listings({"nft_id": nft_id})
        for item in marketplace_items:
            if item.genesis_nft and item.genesis_nft.nft_id == nft_id:
                item.listing = None
                self.marketplace_repository.save(item)
                break
        
        # Save NFT
        self.nft_repository.save(nft)
    
    def get_marketplace_listings(
        self,
        filters: Dict[str, Any] = None,
        sort_by: str = "listed_at",
        sort_order: str = "desc",
        limit: int = 50,
        offset: int = 0
    ) -> List[MarketplaceItem]:
        """Get marketplace listings with filtering and sorting"""
        
        if filters is None:
            filters = {}
        
        # Add active status filter
        filters["status"] = "active"
        
        # Get listings from repository
        all_listings = self.marketplace_repository.find_active_listings(filters)
        
        # Apply sorting
        if sort_by == "price":
            all_listings.sort(
                key=lambda x: x.listing.price if x.listing else Decimal("0"),
                reverse=(sort_order == "desc")
            )
        elif sort_by == "rarity":
            all_listings.sort(
                key=lambda x: x.genesis_nft.rarity.score if x.genesis_nft else Decimal("0"),
                reverse=(sort_order == "desc")
            )
        elif sort_by == "popularity":
            all_listings.sort(
                key=lambda x: x.get_popularity_score(),
                reverse=(sort_order == "desc")
            )
        else:  # Default to listed_at
            all_listings.sort(
                key=lambda x: x.created_at,
                reverse=(sort_order == "desc")
            )
        
        # Apply pagination
        return all_listings[offset:offset + limit]
    
    def get_trending_nfts(self, limit: int = 20) -> List[MarketplaceItem]:
        """Get trending NFTs on marketplace"""
        return self.marketplace_repository.find_trending_items(limit)
    
    def record_marketplace_view(self, item_id: str, viewer_id: Optional[int] = None) -> None:
        """Record a view of marketplace item"""
        marketplace_item = self.marketplace_repository.find_by_id(item_id)
        if marketplace_item:
            marketplace_item.add_view(viewer_id)
            self.marketplace_repository.save(marketplace_item)
    
    def toggle_favorite(self, item_id: str, user_id: int, is_favorite: bool) -> None:
        """Add or remove item from user's favorites"""
        marketplace_item = self.marketplace_repository.find_by_id(item_id)
        if marketplace_item:
            if is_favorite:
                marketplace_item.add_to_favorites(user_id)
            else:
                marketplace_item.remove_from_favorites(user_id)
            self.marketplace_repository.save(marketplace_item)
    
    def get_marketplace_analytics(self, time_period_days: int = 30) -> Dict[str, Any]:
        """Get marketplace analytics for specified period"""
        # This would typically query repository for analytics data
        # For now, return a basic structure
        return {
            "total_listings": 0,
            "total_sales": 0,
            "total_volume": {"stellar_shards": 0, "lumina": 0},
            "average_sale_price": {"stellar_shards": 0, "lumina": 0},
            "most_popular_rarity": "epic",
            "most_active_achievement": "constellation_founder",
            "platform_fees_collected": {"stellar_shards": 0, "lumina": 0}
        }
    
    def _generate_marketplace_item_id(self, nft_id: str) -> str:
        """Generate unique marketplace item ID"""
        timestamp = int(datetime.now(timezone.utc).timestamp())
        return f"marketplace_{nft_id}_{timestamp}"


class NFTValuationService:
    """
    Domain service for NFT valuation and price estimation
    
    Handles market value calculation, price trends, and valuation analytics.
    Provides sophisticated pricing models based on rarity, attributes, and market conditions.
    """
    
    def __init__(
        self,
        marketplace_repository: MarketplaceRepositoryInterface,
        nft_repository: NFTRepositoryInterface
    ):
        self.marketplace_repository = marketplace_repository
        self.nft_repository = nft_repository
    
    def estimate_nft_value(self, genesis_nft: GenesisNFT) -> Dict[str, Decimal]:
        """Estimate market value of Genesis NFT in different currencies"""
        base_value = self._calculate_base_value(genesis_nft)
        
        # Apply market modifiers
        rarity_multiplier = self._get_rarity_multiplier(genesis_nft.rarity)
        attribute_multiplier = self._get_attribute_multiplier(genesis_nft)
        market_multiplier = self._get_market_multiplier(genesis_nft)
        history_multiplier = self._get_history_multiplier(genesis_nft)
        
        # Calculate final value
        final_value = base_value * rarity_multiplier * attribute_multiplier * market_multiplier * history_multiplier
        
        return {
            "stellar_shards": final_value,
            "lumina": final_value * Decimal("0.2"),  # 1 LM = 5 SS
            "starknet_eth": final_value / Decimal("50000")  # Mock conversion
        }
    
    def get_price_recommendation(
        self,
        genesis_nft: GenesisNFT,
        listing_strategy: str = "optimal"
    ) -> Dict[str, Any]:
        """Get recommended listing price based on strategy"""
        estimated_values = self.estimate_nft_value(genesis_nft)
        base_price = estimated_values["stellar_shards"]
        
        strategies = {
            "quick_sale": Decimal("0.85"),  # 15% below estimate for quick sale
            "optimal": Decimal("1.0"),      # At estimated value
            "premium": Decimal("1.2"),      # 20% above estimate for premium positioning
            "collector": Decimal("1.5")     # 50% above for rare collectors
        }
        
        multiplier = strategies.get(listing_strategy, Decimal("1.0"))
        recommended_price = base_price * multiplier
        
        # Get comparable sales
        comparables = self._find_comparable_sales(genesis_nft)
        
        return {
            "recommended_price": {
                "stellar_shards": recommended_price,
                "lumina": recommended_price * Decimal("0.2"),
                "starknet_eth": recommended_price / Decimal("50000")
            },
            "strategy": listing_strategy,
            "confidence_score": self._calculate_confidence_score(genesis_nft, comparables),
            "market_positioning": self._get_market_positioning(recommended_price, comparables),
            "expected_sale_time_days": self._estimate_sale_time(listing_strategy, genesis_nft),
            "comparable_sales": comparables[:5]  # Top 5 comparables
        }
    
    def analyze_price_trends(self, achievement_type: AchievementType, rarity_level: RarityLevel) -> Dict[str, Any]:
        """Analyze price trends for specific NFT category"""
        similar_nfts = self.nft_repository.find_by_achievement_type(achievement_type)
        similar_nfts = [nft for nft in similar_nfts if nft.rarity.level == rarity_level]
        
        if not similar_nfts:
            return self._empty_trend_analysis()
        
        # Analyze sales history
        all_sales = []
        for nft in similar_nfts:
            all_sales.extend(nft.sales_history)
        
        if not all_sales:
            return self._empty_trend_analysis()
        
        # Sort by date
        all_sales.sort(key=lambda x: x["sale_date"])
        
        # Calculate trends
        recent_sales = all_sales[-10:]  # Last 10 sales
        older_sales = all_sales[-30:-10] if len(all_sales) >= 30 else all_sales[:-10]
        
        recent_avg = self._calculate_average_price(recent_sales)
        older_avg = self._calculate_average_price(older_sales) if older_sales else recent_avg
        
        trend_direction = "stable"
        trend_percentage = Decimal("0")
        
        if recent_avg != older_avg:
            trend_percentage = ((recent_avg - older_avg) / older_avg) * Decimal("100")
            if trend_percentage > Decimal("10"):
                trend_direction = "increasing"
            elif trend_percentage < Decimal("-10"):
                trend_direction = "decreasing"
        
        return {
            "achievement_type": achievement_type.value,
            "rarity_level": rarity_level.value,
            "total_sales": len(all_sales),
            "recent_average_price": float(recent_avg),
            "trend_direction": trend_direction,
            "trend_percentage": float(trend_percentage),
            "price_range": {
                "min": float(min(Decimal(str(sale["sale_price"])) for sale in all_sales)),
                "max": float(max(Decimal(str(sale["sale_price"])) for sale in all_sales)),
                "median": float(self._calculate_median_price(all_sales))
            },
            "volume_last_30_days": float(sum(Decimal(str(sale["sale_price"])) for sale in all_sales[-30:])),
            "most_active_price_range": self._find_most_active_price_range(all_sales)
        }
    
    def get_collection_valuation(self, nft_collection: 'NFTCollection') -> Dict[str, Any]:
        """Get comprehensive valuation for entire collection"""
        if not nft_collection.genesis_nfts:
            return {"total_value": {"stellar_shards": 0, "lumina": 0, "starknet_eth": 0}}
        
        individual_valuations = []
        total_values = {"stellar_shards": Decimal("0"), "lumina": Decimal("0"), "starknet_eth": Decimal("0")}
        
        for nft in nft_collection.genesis_nfts:
            valuation = self.estimate_nft_value(nft)
            individual_valuations.append({
                "nft_id": nft.nft_id,
                "achievement_type": nft.achievement_type.value,
                "rarity": nft.rarity.level.value,
                "estimated_value": valuation
            })
            
            for currency, value in valuation.items():
                total_values[currency] += value
        
        # Calculate collection premium (collections can be worth more than sum of parts)
        collection_premium = self._calculate_collection_premium(nft_collection)
        
        for currency in total_values:
            total_values[currency] *= collection_premium
        
        return {
            "total_value": {currency: float(value) for currency, value in total_values.items()},
            "collection_premium": float(collection_premium),
            "individual_valuations": individual_valuations,
            "value_distribution": self._analyze_value_distribution(individual_valuations),
            "collection_tier": nft_collection.collection_stats.get_collection_tier() if nft_collection.collection_stats else "common",
            "growth_potential": self._assess_growth_potential(nft_collection)
        }
    
    def _calculate_base_value(self, genesis_nft: GenesisNFT) -> Decimal:
        """Calculate base value from metadata"""
        if genesis_nft.metadata:
            return genesis_nft.metadata.get_market_value_estimate()
        else:
            # Fallback to rarity-based valuation
            rarity_values = {
                RarityLevel.COMMON: Decimal("1000"),
                RarityLevel.UNCOMMON: Decimal("2500"),
                RarityLevel.RARE: Decimal("5000"),
                RarityLevel.EPIC: Decimal("15000"),
                RarityLevel.LEGENDARY: Decimal("50000")
            }
            return rarity_values.get(genesis_nft.rarity.level, Decimal("1000"))
    
    def _get_rarity_multiplier(self, rarity: Rarity) -> Decimal:
        """Get rarity-based price multiplier"""
        return Decimal("1.0") + (rarity.score / Decimal("10.0"))
    
    def _get_attribute_multiplier(self, genesis_nft: GenesisNFT) -> Decimal:
        """Get attribute-based price multiplier"""
        if not genesis_nft.metadata:
            return Decimal("1.0")
        
        # Base multiplier
        multiplier = Decimal("1.0")
        
        # Power level bonus
        power_level = genesis_nft.metadata.get_attribute_value("Power Level") or 0
        if power_level > 30:
            multiplier += Decimal("0.3")
        elif power_level > 20:
            multiplier += Decimal("0.2")
        elif power_level > 10:
            multiplier += Decimal("0.1")
        
        # Cosmic properties bonus
        cosmic_props = genesis_nft.get_cosmic_properties()
        stellar_alignment = cosmic_props.get("stellar_alignment", 0)
        if stellar_alignment > 120:
            multiplier += Decimal("0.2")
        elif stellar_alignment > 100:
            multiplier += Decimal("0.1")
        
        return multiplier
    
    def _get_market_multiplier(self, genesis_nft: GenesisNFT) -> Decimal:
        """Get market condition multiplier"""
        # This would integrate with real market data
        # For now, return base multiplier with some variation
        achievement_popularity = {
            AchievementType.TRADING_MASTER: Decimal("1.3"),
            AchievementType.CONSTELLATION_FOUNDER: Decimal("1.2"),
            AchievementType.VIRAL_LEGEND: Decimal("1.15"),
            AchievementType.LEVEL_MILESTONE: Decimal("1.05"),
            AchievementType.FIRST_TRADE: Decimal("1.0")
        }
        return achievement_popularity.get(genesis_nft.achievement_type, Decimal("1.0"))
    
    def _get_history_multiplier(self, genesis_nft: GenesisNFT) -> Decimal:
        """Get historical sales multiplier"""
        if not genesis_nft.sales_history:
            return Decimal("1.0")
        
        # Premium for previously traded NFTs (provenance)
        sales_count = len(genesis_nft.sales_history)
        if sales_count > 5:
            return Decimal("1.2")
        elif sales_count > 2:
            return Decimal("1.1")
        else:
            return Decimal("1.05")
    
    def _find_comparable_sales(self, genesis_nft: GenesisNFT) -> List[Dict[str, Any]]:
        """Find comparable sales for pricing reference"""
        # Find NFTs with same achievement type and similar rarity
        similar_nfts = self.nft_repository.find_by_achievement_type(genesis_nft.achievement_type)
        
        comparables = []
        for nft in similar_nfts:
            if nft.nft_id == genesis_nft.nft_id:
                continue
            
            # Check rarity similarity
            rarity_diff = abs(float(nft.rarity.score - genesis_nft.rarity.score))
            if rarity_diff <= 5.0:  # Similar rarity
                for sale in nft.sales_history[-3:]:  # Last 3 sales
                    comparables.append({
                        "nft_id": nft.nft_id,
                        "sale_price": sale["sale_price"],
                        "sale_date": sale["sale_date"],
                        "rarity": nft.rarity.level.value,
                        "rarity_score": float(nft.rarity.score)
                    })
        
        # Sort by recency and rarity similarity
        comparables.sort(key=lambda x: (x["sale_date"], abs(x["rarity_score"] - float(genesis_nft.rarity.score))), reverse=True)
        return comparables
    
    def _calculate_confidence_score(self, genesis_nft: GenesisNFT, comparables: List[Dict[str, Any]]) -> float:
        """Calculate confidence score for price estimate"""
        base_confidence = 0.5
        
        # More comparables = higher confidence
        if len(comparables) >= 10:
            base_confidence += 0.3
        elif len(comparables) >= 5:
            base_confidence += 0.2
        elif len(comparables) >= 2:
            base_confidence += 0.1
        
        # Recent sales = higher confidence
        recent_comparables = [c for c in comparables if (datetime.now(timezone.utc) - c["sale_date"]).days <= 30]
        if len(recent_comparables) >= 3:
            base_confidence += 0.1
        
        # Exact rarity match = higher confidence
        exact_rarity_matches = [c for c in comparables if c["rarity"] == genesis_nft.rarity.level.value]
        if len(exact_rarity_matches) >= 2:
            base_confidence += 0.1
        
        return min(1.0, base_confidence)
    
    def _get_market_positioning(self, recommended_price: Decimal, comparables: List[Dict[str, Any]]) -> str:
        """Determine market positioning of recommended price"""
        if not comparables:
            return "unknown"
        
        comparable_prices = [Decimal(str(c["sale_price"])) for c in comparables[-10:]]
        avg_comparable = sum(comparable_prices) / len(comparable_prices)
        
        if recommended_price > avg_comparable * Decimal("1.2"):
            return "premium"
        elif recommended_price > avg_comparable * Decimal("1.1"):
            return "above_market"
        elif recommended_price < avg_comparable * Decimal("0.9"):
            return "below_market"
        elif recommended_price < avg_comparable * Decimal("0.8"):
            return "discount"
        else:
            return "market_rate"
    
    def _estimate_sale_time(self, strategy: str, genesis_nft: GenesisNFT) -> int:
        """Estimate time to sale based on strategy and NFT characteristics"""
        base_days = {
            "quick_sale": 3,
            "optimal": 14,
            "premium": 30,
            "collector": 60
        }
        
        estimated_days = base_days.get(strategy, 14)
        
        # Adjust based on rarity
        if genesis_nft.rarity.level == RarityLevel.LEGENDARY:
            estimated_days *= 2  # Legendary takes longer but commands premium
        elif genesis_nft.rarity.level == RarityLevel.COMMON:
            estimated_days = int(estimated_days * 0.7)  # Common sells faster
        
        return estimated_days
    
    def _empty_trend_analysis(self) -> Dict[str, Any]:
        """Return empty trend analysis structure"""
        return {
            "total_sales": 0,
            "recent_average_price": 0,
            "trend_direction": "insufficient_data",
            "trend_percentage": 0,
            "price_range": {"min": 0, "max": 0, "median": 0},
            "volume_last_30_days": 0,
            "most_active_price_range": "unknown"
        }
    
    def _calculate_average_price(self, sales: List[Dict[str, Any]]) -> Decimal:
        """Calculate average price from sales"""
        if not sales:
            return Decimal("0")
        return sum(Decimal(str(sale["sale_price"])) for sale in sales) / len(sales)
    
    def _calculate_median_price(self, sales: List[Dict[str, Any]]) -> Decimal:
        """Calculate median price from sales"""
        if not sales:
            return Decimal("0")
        
        prices = sorted([Decimal(str(sale["sale_price"])) for sale in sales])
        n = len(prices)
        
        if n % 2 == 0:
            return (prices[n//2 - 1] + prices[n//2]) / 2
        else:
            return prices[n//2]
    
    def _find_most_active_price_range(self, sales: List[Dict[str, Any]]) -> str:
        """Find the most active price range"""
        if not sales:
            return "unknown"
        
        # Define price ranges
        ranges = {
            "0-1000": (0, 1000),
            "1000-5000": (1000, 5000),
            "5000-15000": (5000, 15000),
            "15000-50000": (15000, 50000),
            "50000+": (50000, float('inf'))
        }
        
        range_counts = {range_name: 0 for range_name in ranges}
        
        for sale in sales:
            price = float(sale["sale_price"])
            for range_name, (min_price, max_price) in ranges.items():
                if min_price <= price < max_price:
                    range_counts[range_name] += 1
                    break
        
        return max(range_counts.items(), key=lambda x: x[1])[0]
    
    def _calculate_collection_premium(self, nft_collection: 'NFTCollection') -> Decimal:
        """Calculate collection premium based on completeness and synergies"""
        base_premium = Decimal("1.0")
        
        if not nft_collection.collection_stats:
            return base_premium
        
        # Completion bonus
        completion_pct = nft_collection.collection_stats.completion_percentage
        if completion_pct >= 100:
            base_premium += Decimal("0.25")  # 25% bonus for complete collection
        elif completion_pct >= 80:
            base_premium += Decimal("0.15")  # 15% bonus for nearly complete
        elif completion_pct >= 60:
            base_premium += Decimal("0.10")  # 10% bonus for majority complete
        
        # Rarity synergy bonus
        avg_rarity = nft_collection.collection_stats.get_average_rarity_score()
        if avg_rarity >= Decimal("15.0"):
            base_premium += Decimal("0.20")  # High rarity collection
        elif avg_rarity >= Decimal("8.0"):
            base_premium += Decimal("0.10")  # Medium rarity collection
        
        return base_premium
    
    def _analyze_value_distribution(self, individual_valuations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze how value is distributed across the collection"""
        if not individual_valuations:
            return {}
        
        values = [val["estimated_value"]["stellar_shards"] for val in individual_valuations]
        total_value = sum(values)
        
        # Find most valuable NFT
        most_valuable = max(individual_valuations, key=lambda x: x["estimated_value"]["stellar_shards"])
        
        # Calculate concentration (what % of value is in top NFT)
        concentration = (most_valuable["estimated_value"]["stellar_shards"] / total_value) * 100
        
        return {
            "most_valuable_nft": most_valuable,
            "value_concentration_pct": concentration,
            "average_nft_value": total_value / len(individual_valuations),
            "value_distribution": "concentrated" if concentration > 50 else "balanced"
        }
    
    def _assess_growth_potential(self, nft_collection: 'NFTCollection') -> str:
        """Assess the growth potential of the collection"""
        if not nft_collection.collection_stats:
            return "unknown"
        
        completion = nft_collection.collection_stats.completion_percentage
        avg_rarity = nft_collection.collection_stats.get_average_rarity_score()
        
        if completion >= 80 and avg_rarity >= Decimal("10.0"):
            return "high"
        elif completion >= 60 or avg_rarity >= Decimal("5.0"):
            return "medium"
        else:
            return "low"


class CollectionService:
    """
    Domain service for NFT collection management
    
    Handles user collections, analytics, and social features.
    Provides collection insights and sharing capabilities.
    """
    
    def __init__(
        self,
        collection_repository: CollectionRepositoryInterface,
        nft_repository: NFTRepositoryInterface
    ):
        self.collection_repository = collection_repository
        self.nft_repository = nft_repository
    
    def get_user_collection(self, user_id: int) -> Optional[NFTCollection]:
        """Get user's NFT collection"""
        collection = self.collection_repository.find_by_owner(user_id)
        
        if not collection:
            # Create collection if it doesn't exist
            collection = NFTCollection(owner_id=user_id)
            collection_id = f"collection_{user_id}_{secrets.token_hex(6)}"
            collection.set_collection_id(collection_id)
            
            # Add user's NFTs to collection
            user_nfts = self.nft_repository.find_by_owner(user_id)
            for nft in user_nfts:
                collection.add_nft(nft)
            
            self.collection_repository.save(collection)
        
        return collection
    
    def update_collection_preferences(
        self,
        user_id: int,
        display_order: str,
        public_visibility: bool
    ) -> NFTCollection:
        """Update user's collection display preferences"""
        collection = self.get_user_collection(user_id)
        if not collection:
            raise ValueError("Collection not found")
        
        collection.update_display_preferences(display_order, public_visibility)
        self.collection_repository.save(collection)
        
        return collection
    
    def set_featured_nft(self, user_id: int, nft_id: str) -> NFTCollection:
        """Set featured NFT in collection"""
        collection = self.get_user_collection(user_id)
        if not collection:
            raise ValueError("Collection not found")
        
        collection.set_featured_nft(nft_id)
        self.collection_repository.save(collection)
        
        return collection
    
    def get_collection_analytics(self, user_id: int) -> Dict[str, Any]:
        """Get detailed collection analytics"""
        collection = self.get_user_collection(user_id)
        if not collection or not collection.genesis_nfts:
            return self._empty_analytics()
        
        # Calculate comprehensive analytics
        nfts = collection.genesis_nfts
        total_value = collection.get_collection_value()
        achievement_completion = collection.get_achievement_completion()
        
        # Rarity breakdown
        rarity_breakdown = {}
        for nft in nfts:
            rarity = nft.rarity.level.value
            rarity_breakdown[rarity] = rarity_breakdown.get(rarity, 0) + 1
        
        # Achievement breakdown
        achievement_breakdown = {}
        for nft in nfts:
            achievement = nft.achievement_type.value
            achievement_breakdown[achievement] = achievement_breakdown.get(achievement, 0) + 1
        
        # Trading activity
        total_sales = sum(nft.get_sales_count() for nft in nfts)
        total_volume = sum(nft.get_total_volume() for nft in nfts)
        
        return {
            "total_nfts": len(nfts),
            "total_value": {currency: float(value) for currency, value in total_value.items()},
            "rarity_breakdown": rarity_breakdown,
            "achievement_breakdown": achievement_breakdown,
            "achievement_completion": achievement_completion,
            "completion_percentage": float(collection.collection_stats.completion_percentage) if collection.collection_stats else 0,
            "average_rarity_score": float(collection.collection_stats.get_average_rarity_score()) if collection.collection_stats else 0,
            "collection_tier": collection.collection_stats.get_collection_tier() if collection.collection_stats else "common",
            "trading_activity": {
                "total_sales": total_sales,
                "total_volume": float(total_volume),
                "most_valuable_nft": self._get_most_valuable_nft(nfts)
            },
            "recent_additions": [
                {
                    "nft_id": nft.nft_id,
                    "achievement_type": nft.achievement_type.value,
                    "rarity": nft.rarity.level.value,
                    "created_at": nft.created_at.isoformat()
                }
                for nft in collection.get_recent_nfts(5)
            ]
        }
    
    def get_collection_leaderboard(self, metric: str = "total_value", limit: int = 100) -> List[Dict[str, Any]]:
        """Get collection leaderboard by specified metric"""
        public_collections = self.collection_repository.find_public_collections(limit * 2)  # Get more than needed for filtering
        
        leaderboard = []
        for collection in public_collections:
            if not collection.public_visibility or not collection.genesis_nfts:
                continue
            
            collection_data = {
                "collection_id": collection.collection_id,
                "owner_id": collection.owner_id,
                "total_nfts": len(collection.genesis_nfts),
                "total_value": collection.get_collection_value(),
                "completion_percentage": float(collection.collection_stats.completion_percentage) if collection.collection_stats else 0,
                "average_rarity": float(collection.collection_stats.get_average_rarity_score()) if collection.collection_stats else 0,
                "collection_tier": collection.collection_stats.get_collection_tier() if collection.collection_stats else "common"
            }
            leaderboard.append(collection_data)
        
        # Sort by metric
        if metric == "total_value":
            leaderboard.sort(key=lambda x: x["total_value"]["stellar_shards"], reverse=True)
        elif metric == "completion_percentage":
            leaderboard.sort(key=lambda x: x["completion_percentage"], reverse=True)
        elif metric == "average_rarity":
            leaderboard.sort(key=lambda x: x["average_rarity"], reverse=True)
        elif metric == "total_nfts":
            leaderboard.sort(key=lambda x: x["total_nfts"], reverse=True)
        
        return leaderboard[:limit]
    
    def get_global_collection_stats(self) -> Dict[str, Any]:
        """Get global collection statistics"""
        # This would typically aggregate data from all collections
        return {
            "total_collections": 0,
            "total_nfts_minted": 0,
            "average_collection_size": 0,
            "most_popular_achievement": "first_trade",
            "rarity_distribution": {
                "common": 0,
                "uncommon": 0,
                "rare": 0,
                "epic": 0,
                "legendary": 0
            },
            "completion_rate": 0.0
        }
    
    def _empty_analytics(self) -> Dict[str, Any]:
        """Return empty analytics structure"""
        return {
            "total_nfts": 0,
            "total_value": {"stellar_shards": 0, "lumina": 0, "starknet_eth": 0},
            "rarity_breakdown": {},
            "achievement_breakdown": {},
            "achievement_completion": {achievement.value: False for achievement in AchievementType},
            "completion_percentage": 0,
            "average_rarity_score": 0,
            "collection_tier": "common",
            "trading_activity": {"total_sales": 0, "total_volume": 0, "most_valuable_nft": None},
            "recent_additions": []
        }
    
    def _get_most_valuable_nft(self, nfts: List[GenesisNFT]) -> Optional[Dict[str, Any]]:
        """Get most valuable NFT in collection"""
        if not nfts:
            return None
        
        most_valuable = max(nfts, key=lambda nft: nft.get_estimated_value()["stellar_shards"])
        estimated_value = most_valuable.get_estimated_value()
        
        return {
            "nft_id": most_valuable.nft_id,
            "achievement_type": most_valuable.achievement_type.value,
            "rarity": most_valuable.rarity.level.value,
            "estimated_value": float(estimated_value["stellar_shards"])
        }