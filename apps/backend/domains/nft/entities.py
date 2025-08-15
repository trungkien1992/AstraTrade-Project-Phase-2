"""
NFT Domain Entities

Rich domain entities for the NFT Domain following DDD patterns.
These entities contain business logic and maintain domain invariants.
"""

from datetime import datetime, timezone, timedelta
from decimal import Decimal
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
import secrets

from value_objects import (
    AchievementType, RarityLevel, NFTStatus, MarketplaceCurrency, ListingStatus,
    Rarity, AchievementCriteria, NFTMetadata, MarketplaceListing, CollectionStats,
    BlockchainTransaction, NFTRoyalty, NFTAttributes
)


@dataclass
class DomainEvent:
    """Base class for domain events"""
    event_type: str
    entity_id: str
    data: Dict[str, Any]
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class GenesisNFT:
    """
    Genesis NFT Entity (Aggregate Root)
    
    Represents a Genesis Seed NFT with simplified core state management.
    Business logic has been extracted to domain services and value objects.
    """
    
    nft_id: Optional[str] = None
    token_id: Optional[int] = None
    owner_id: int = 0
    achievement_type: AchievementType = AchievementType.FIRST_TRADE
    rarity: Rarity = field(default_factory=lambda: Rarity.from_level(RarityLevel.COMMON))
    metadata: Optional[NFTMetadata] = None
    attributes: Optional[NFTAttributes] = None
    royalty: Optional[NFTRoyalty] = None
    status: NFTStatus = NFTStatus.PENDING_MINT
    minting_transaction: Optional[BlockchainTransaction] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    minted_at: Optional[datetime] = None
    
    # Marketplace related fields
    current_listing: Optional[MarketplaceListing] = None
    sales_history: List[Dict[str, Any]] = field(default_factory=list)
    
    # Domain event storage
    _domain_events: List[DomainEvent] = field(default_factory=list, init=False)
    
    def set_nft_id(self, nft_id: str) -> None:
        """Set NFT ID (can only be set once)"""
        if self.nft_id is not None:
            raise ValueError("NFT ID cannot be changed once set")
        self.nft_id = nft_id
        self._emit_event("nft_created", {
            "nft_id": nft_id,
            "owner_id": self.owner_id,
            "achievement_type": self.achievement_type.value,
            "rarity": self.rarity.level.value
        })
    
    def set_token_id(self, token_id: int) -> None:
        """Set blockchain token ID (can only be set once)"""
        if self.token_id is not None:
            raise ValueError("Token ID cannot be changed once set")
        if token_id <= 0:
            raise ValueError("Token ID must be positive")
        self.token_id = token_id
    
    def mint_nft(self, blockchain_transaction: BlockchainTransaction) -> None:
        """Mint the Genesis NFT with blockchain transaction"""
        if self.status != NFTStatus.PENDING_MINT:
            raise ValueError("Can only mint NFTs in pending_mint status")
        
        if not self.nft_id:
            raise ValueError("NFT ID must be set before minting")
        
        if not blockchain_transaction.is_confirmed():
            raise ValueError("Blockchain transaction must be confirmed")
        
        if not self.metadata:
            raise ValueError("Metadata must be set before minting")
        
        if not self.attributes:
            raise ValueError("Attributes must be set before minting")
        
        # Update mint status
        self.status = NFTStatus.MINTED
        self.minting_transaction = blockchain_transaction
        self.minted_at = datetime.now(timezone.utc)
        self.token_id = blockchain_transaction.token_id
        
        self._emit_event("nft_minted", {
            "nft_id": self.nft_id,
            "token_id": self.token_id,
            "transaction_hash": blockchain_transaction.transaction_hash,
            "rarity": self.rarity.level.value,
            "achievement_type": self.achievement_type.value
        })
    
    def list_on_marketplace(
        self,
        price: Decimal,
        currency: MarketplaceCurrency,
        duration_days: int = 30,
        featured: bool = False,
        description: Optional[str] = None
    ) -> MarketplaceListing:
        """List NFT on marketplace"""
        if self.status != NFTStatus.MINTED:
            raise ValueError("Can only list minted NFTs")
        
        if self.current_listing and self.current_listing.is_active():
            raise ValueError("NFT is already listed on marketplace")
        
        if price <= 0:
            raise ValueError("Listing price must be positive")
        
        # Create marketplace listing
        listing = MarketplaceListing.create_listing(
            nft_token_id=self.token_id,
            owner_id=self.owner_id,
            price=price,
            currency=currency,
            duration_days=duration_days,
            featured=featured,
            description=description
        )
        
        self.current_listing = listing
        self.status = NFTStatus.LISTED
        
        self._emit_event("nft_listed", {
            "nft_id": self.nft_id,
            "listing_id": listing.listing_id,
            "price": str(price),
            "currency": currency.value,
            "duration_days": duration_days,
            "featured": featured
        })
        
        return listing
    
    def unlist_from_marketplace(self, reason: str = "owner_request") -> None:
        """Remove NFT from marketplace"""
        if not self.current_listing or not self.current_listing.is_active():
            raise ValueError("NFT is not currently listed")
        
        old_listing_id = self.current_listing.listing_id
        self.current_listing = None
        self.status = NFTStatus.MINTED
        
        self._emit_event("nft_unlisted", {
            "nft_id": self.nft_id,
            "listing_id": old_listing_id,
            "reason": reason
        })
    
    def sell_to_buyer(self, buyer_id: int, sale_price: Decimal, currency: MarketplaceCurrency) -> Dict[str, Any]:
        """Process sale to buyer using royalty structure"""
        if not self.current_listing or not self.current_listing.is_active():
            raise ValueError("NFT must be actively listed to sell")
        
        if buyer_id == self.owner_id:
            raise ValueError("Cannot sell NFT to current owner")
        
        if sale_price != self.current_listing.price:
            raise ValueError("Sale price must match listing price")
        
        if not self.royalty:
            raise ValueError("Royalty structure must be set for sales")
        
        # Calculate fees using royalty value object
        fee_breakdown = self.royalty.calculate_fees(sale_price)
        
        # Create sale record
        sale_record = {
            "sale_id": f"sale_{secrets.token_hex(8)}",
            "listing_id": self.current_listing.listing_id,
            "seller_id": self.owner_id,
            "buyer_id": buyer_id,
            "sale_price": sale_price,
            "currency": currency.value,
            "platform_fee": fee_breakdown["platform_fee"],
            "creator_royalty": fee_breakdown["creator_royalty"],
            "transaction_fee": fee_breakdown["transaction_fee"],
            "total_fees": fee_breakdown["total_fees"],
            "seller_proceeds": fee_breakdown["seller_proceeds"],
            "sale_date": datetime.now(timezone.utc)
        }
        
        # Update ownership and status
        old_owner_id = self.owner_id
        self.owner_id = buyer_id
        self.status = NFTStatus.SOLD
        self.current_listing = None
        self.sales_history.append(sale_record)
        
        self._emit_event("nft_sold", {
            "nft_id": self.nft_id,
            "sale_id": sale_record["sale_id"],
            "seller_id": old_owner_id,
            "buyer_id": buyer_id,
            "sale_price": str(sale_price),
            "currency": currency.value,
            "total_fees": str(fee_breakdown["total_fees"]),
            "seller_proceeds": str(fee_breakdown["seller_proceeds"])
        })
        
        return sale_record
    
    def transfer_to_owner(self, new_owner_id: int, transfer_reason: str = "direct_transfer") -> None:
        """Transfer NFT to new owner (non-marketplace)"""
        if self.status not in [NFTStatus.MINTED, NFTStatus.SOLD]:
            raise ValueError("Can only transfer minted or sold NFTs")
        
        if new_owner_id == self.owner_id:
            raise ValueError("Cannot transfer NFT to current owner")
        
        if new_owner_id <= 0:
            raise ValueError("New owner ID must be positive")
        
        old_owner_id = self.owner_id
        self.owner_id = new_owner_id
        self.status = NFTStatus.TRANSFERRED
        
        # Clear any active listing
        if self.current_listing and self.current_listing.is_active():
            self.current_listing = None
        
        self._emit_event("nft_transferred", {
            "nft_id": self.nft_id,
            "old_owner_id": old_owner_id,
            "new_owner_id": new_owner_id,
            "transfer_reason": transfer_reason
        })
    
    def update_marketplace_listing(
        self,
        new_price: Optional[Decimal] = None,
        new_currency: Optional[MarketplaceCurrency] = None,
        extend_days: Optional[int] = None,
        featured: Optional[bool] = None
    ) -> MarketplaceListing:
        """Update active marketplace listing"""
        if not self.current_listing or not self.current_listing.is_active():
            raise ValueError("No active listing to update")
        
        # Create updated listing
        updated_listing = MarketplaceListing(
            listing_id=self.current_listing.listing_id,
            nft_token_id=self.current_listing.nft_token_id,
            owner_id=self.current_listing.owner_id,
            price=new_price if new_price is not None else self.current_listing.price,
            currency=new_currency if new_currency is not None else self.current_listing.currency,
            status=self.current_listing.status,
            listed_at=self.current_listing.listed_at,
            expires_at=(
                self.current_listing.expires_at + timedelta(days=extend_days)
                if extend_days is not None else self.current_listing.expires_at
            ),
            featured=featured if featured is not None else self.current_listing.featured,
            description=self.current_listing.description
        )
        
        self.current_listing = updated_listing
        
        self._emit_event("listing_updated", {
            "nft_id": self.nft_id,
            "listing_id": updated_listing.listing_id,
            "new_price": str(updated_listing.price),
            "new_currency": updated_listing.currency.value,
            "featured": updated_listing.featured
        })
        
        return updated_listing
    
    def get_estimated_value(self) -> Dict[str, Decimal]:
        """Get basic estimated market value - use NFTValuationService for advanced pricing"""
        # Use metadata estimate if available
        if self.metadata:
            base_value = self.metadata.get_market_value_estimate()
        elif self.attributes:
            # Use attributes multiplier if available
            multiplier = self.attributes.get_market_value_multiplier()
            rarity_base = {
                RarityLevel.COMMON: Decimal("1000"),
                RarityLevel.UNCOMMON: Decimal("2500"),
                RarityLevel.RARE: Decimal("5000"),
                RarityLevel.EPIC: Decimal("15000"),
                RarityLevel.LEGENDARY: Decimal("50000")
            }
            base_value = rarity_base.get(self.rarity.level, Decimal("1000")) * multiplier
        else:
            # Fallback to rarity-based estimate
            rarity_values = {
                RarityLevel.COMMON: Decimal("1000"),
                RarityLevel.UNCOMMON: Decimal("2500"),
                RarityLevel.RARE: Decimal("5000"),
                RarityLevel.EPIC: Decimal("15000"),
                RarityLevel.LEGENDARY: Decimal("50000")
            }
            base_value = rarity_values.get(self.rarity.level, Decimal("1000"))
        
        return {
            "stellar_shards": base_value,
            "lumina": base_value * Decimal("0.2"),  # 1 LM = 5 SS
            "starknet_eth": base_value / Decimal("50000")  # Mock conversion
        }
    
    def is_owned_by(self, user_id: int) -> bool:
        """Check if NFT is owned by specific user"""
        return self.owner_id == user_id
    
    def is_tradeable(self) -> bool:
        """Check if NFT can be traded"""
        return self.status in [NFTStatus.MINTED, NFTStatus.SOLD, NFTStatus.TRANSFERRED]
    
    def get_cosmic_properties(self) -> Dict[str, Any]:
        """Get cosmic properties from attributes or metadata"""
        if self.attributes:
            return self.attributes.cosmic_properties
        elif self.metadata:
            return self.metadata.cosmic_properties
        else:
            return {}
    
    def get_sales_count(self) -> int:
        """Get number of times NFT has been sold"""
        return len(self.sales_history)
    
    def get_total_volume(self) -> Decimal:
        """Get total trading volume for this NFT"""
        return sum(Decimal(str(sale["sale_price"])) for sale in self.sales_history)
    
    
    def _emit_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """Emit domain event"""
        event = DomainEvent(
            event_type=event_type,
            entity_id=self.nft_id or "unknown",
            data=data
        )
        self._domain_events.append(event)
    
    def get_domain_events(self) -> List[DomainEvent]:
        """Get and clear domain events"""
        events = self._domain_events.copy()
        self._domain_events.clear()
        return events


@dataclass
class NFTCollection:
    """
    NFT Collection Entity
    
    Represents a user's complete NFT collection with analytics and management.
    Handles collection statistics, featured NFTs, and collection value tracking.
    """
    
    collection_id: Optional[str] = None
    owner_id: int = 0
    genesis_nfts: List[GenesisNFT] = field(default_factory=list)
    featured_nft_id: Optional[str] = None
    collection_stats: Optional[CollectionStats] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Collection preferences
    public_visibility: bool = True
    display_order: str = "rarity_desc"  # rarity_desc, rarity_asc, date_desc, date_asc
    
    # Domain event storage
    _domain_events: List[DomainEvent] = field(default_factory=list, init=False)
    
    def set_collection_id(self, collection_id: str) -> None:
        """Set collection ID (can only be set once)"""
        if self.collection_id is not None:
            raise ValueError("Collection ID cannot be changed once set")
        self.collection_id = collection_id
        self._emit_event("collection_created", {
            "collection_id": collection_id,
            "owner_id": self.owner_id
        })
    
    def add_nft(self, genesis_nft: GenesisNFT) -> None:
        """Add NFT to collection"""
        if not genesis_nft.is_owned_by(self.owner_id):
            raise ValueError("Cannot add NFT not owned by collection owner")
        
        # Check if NFT already in collection
        if any(nft.nft_id == genesis_nft.nft_id for nft in self.genesis_nfts):
            raise ValueError("NFT already in collection")
        
        self.genesis_nfts.append(genesis_nft)
        self.updated_at = datetime.now(timezone.utc)
        self._recalculate_stats()
        
        # Set as featured if it's the first or highest rarity
        if not self.featured_nft_id or self._should_be_featured(genesis_nft):
            self.featured_nft_id = genesis_nft.nft_id
        
        self._emit_event("nft_added_to_collection", {
            "collection_id": self.collection_id,
            "nft_id": genesis_nft.nft_id,
            "rarity": genesis_nft.rarity.level.value,
            "achievement_type": genesis_nft.achievement_type.value
        })
    
    def remove_nft(self, nft_id: str) -> None:
        """Remove NFT from collection"""
        nft_to_remove = None
        for nft in self.genesis_nfts:
            if nft.nft_id == nft_id:
                nft_to_remove = nft
                break
        
        if not nft_to_remove:
            raise ValueError("NFT not found in collection")
        
        self.genesis_nfts.remove(nft_to_remove)
        self.updated_at = datetime.now(timezone.utc)
        self._recalculate_stats()
        
        # Update featured NFT if removed
        if self.featured_nft_id == nft_id:
            self._select_new_featured_nft()
        
        self._emit_event("nft_removed_from_collection", {
            "collection_id": self.collection_id,
            "nft_id": nft_id
        })
    
    def set_featured_nft(self, nft_id: str) -> None:
        """Set featured NFT for collection"""
        if not any(nft.nft_id == nft_id for nft in self.genesis_nfts):
            raise ValueError("NFT not found in collection")
        
        old_featured = self.featured_nft_id
        self.featured_nft_id = nft_id
        self.updated_at = datetime.now(timezone.utc)
        
        self._emit_event("featured_nft_changed", {
            "collection_id": self.collection_id,
            "old_featured_nft": old_featured,
            "new_featured_nft": nft_id
        })
    
    def get_featured_nft(self) -> Optional[GenesisNFT]:
        """Get the featured NFT"""
        if not self.featured_nft_id:
            return None
        
        for nft in self.genesis_nfts:
            if nft.nft_id == self.featured_nft_id:
                return nft
        return None
    
    def get_nfts_by_rarity(self, rarity_level: RarityLevel) -> List[GenesisNFT]:
        """Get NFTs filtered by rarity level"""
        return [nft for nft in self.genesis_nfts if nft.rarity.level == rarity_level]
    
    def get_nfts_by_achievement(self, achievement_type: AchievementType) -> List[GenesisNFT]:
        """Get NFTs filtered by achievement type"""
        return [nft for nft in self.genesis_nfts if nft.achievement_type == achievement_type]
    
    def get_recent_nfts(self, limit: int = 5) -> List[GenesisNFT]:
        """Get most recently added NFTs"""
        sorted_nfts = sorted(self.genesis_nfts, key=lambda x: x.created_at, reverse=True)
        return sorted_nfts[:limit]
    
    def get_sorted_nfts(self) -> List[GenesisNFT]:
        """Get NFTs sorted by display order preference"""
        if self.display_order == "rarity_desc":
            return sorted(self.genesis_nfts, key=lambda x: x.rarity.score, reverse=True)
        elif self.display_order == "rarity_asc":
            return sorted(self.genesis_nfts, key=lambda x: x.rarity.score)
        elif self.display_order == "date_desc":
            return sorted(self.genesis_nfts, key=lambda x: x.created_at, reverse=True)
        elif self.display_order == "date_asc":
            return sorted(self.genesis_nfts, key=lambda x: x.created_at)
        else:
            return self.genesis_nfts
    
    def get_collection_value(self) -> Dict[str, Decimal]:
        """Get total collection value in all currencies"""
        total_values = {"stellar_shards": Decimal("0"), "lumina": Decimal("0"), "starknet_eth": Decimal("0")}
        
        for nft in self.genesis_nfts:
            nft_values = nft.get_estimated_value()
            for currency, value in nft_values.items():
                total_values[currency] += value
        
        return total_values
    
    def get_achievement_completion(self) -> Dict[str, bool]:
        """Get completion status for all achievement types"""
        owned_achievements = {nft.achievement_type for nft in self.genesis_nfts}
        
        return {
            achievement_type.value: achievement_type in owned_achievements
            for achievement_type in AchievementType
        }
    
    def update_display_preferences(self, display_order: str, public_visibility: bool) -> None:
        """Update collection display preferences"""
        valid_orders = ["rarity_desc", "rarity_asc", "date_desc", "date_asc"]
        if display_order not in valid_orders:
            raise ValueError(f"Invalid display order. Must be one of: {valid_orders}")
        
        self.display_order = display_order
        self.public_visibility = public_visibility
        self.updated_at = datetime.now(timezone.utc)
        
        self._emit_event("collection_preferences_updated", {
            "collection_id": self.collection_id,
            "display_order": display_order,
            "public_visibility": public_visibility
        })
    
    def _recalculate_stats(self) -> None:
        """Recalculate collection statistics"""
        nft_data = []
        for nft in self.genesis_nfts:
            nft_data.append({
                "rarity": nft.rarity.level.value,
                "achievement_type": nft.achievement_type.value
            })
        
        self.collection_stats = CollectionStats.calculate_from_nfts(nft_data)
    
    def _should_be_featured(self, new_nft: GenesisNFT) -> bool:
        """Determine if new NFT should be featured"""
        if not self.featured_nft_id:
            return True
        
        current_featured = self.get_featured_nft()
        if not current_featured:
            return True
        
        # Feature if new NFT has higher rarity
        return new_nft.rarity.is_higher_than(current_featured.rarity)
    
    def _select_new_featured_nft(self) -> None:
        """Select new featured NFT after current one is removed"""
        if not self.genesis_nfts:
            self.featured_nft_id = None
            return
        
        # Select highest rarity NFT, or most recent if tied
        best_nft = max(
            self.genesis_nfts,
            key=lambda x: (x.rarity.score, x.created_at)
        )
        self.featured_nft_id = best_nft.nft_id
    
    def _emit_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """Emit domain event"""
        event = DomainEvent(
            event_type=event_type,
            entity_id=self.collection_id or "unknown",
            data=data
        )
        self._domain_events.append(event)
    
    def get_domain_events(self) -> List[DomainEvent]:
        """Get and clear domain events"""
        events = self._domain_events.copy()
        self._domain_events.clear()
        return events


@dataclass
class MarketplaceItem:
    """
    Marketplace Item Entity
    
    Represents an NFT listing in the marketplace with bidding and transaction history.
    Handles marketplace-specific operations and analytics.
    """
    
    item_id: Optional[str] = None
    genesis_nft: Optional[GenesisNFT] = None
    listing: Optional[MarketplaceListing] = None
    view_count: int = 0
    favorite_count: int = 0
    bid_history: List[Dict[str, Any]] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Marketplace analytics
    daily_views: Dict[str, int] = field(default_factory=dict)
    price_history: List[Dict[str, Any]] = field(default_factory=list)
    
    # Domain event storage
    _domain_events: List[DomainEvent] = field(default_factory=list, init=False)
    
    def set_item_id(self, item_id: str) -> None:
        """Set marketplace item ID (can only be set once)"""
        if self.item_id is not None:
            raise ValueError("Marketplace item ID cannot be changed once set")
        self.item_id = item_id
    
    def add_view(self, viewer_id: Optional[int] = None) -> None:
        """Record a view of the marketplace item"""
        self.view_count += 1
        
        # Track daily views
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        self.daily_views[today] = self.daily_views.get(today, 0) + 1
        
        self.updated_at = datetime.now(timezone.utc)
        
        self._emit_event("marketplace_item_viewed", {
            "item_id": self.item_id,
            "viewer_id": viewer_id,
            "total_views": self.view_count
        })
    
    def add_to_favorites(self, user_id: int) -> None:
        """Add item to user's favorites"""
        self.favorite_count += 1
        self.updated_at = datetime.now(timezone.utc)
        
        self._emit_event("marketplace_item_favorited", {
            "item_id": self.item_id,
            "user_id": user_id,
            "total_favorites": self.favorite_count
        })
    
    def remove_from_favorites(self, user_id: int) -> None:
        """Remove item from user's favorites"""
        if self.favorite_count > 0:
            self.favorite_count -= 1
            self.updated_at = datetime.now(timezone.utc)
            
            self._emit_event("marketplace_item_unfavorited", {
                "item_id": self.item_id,
                "user_id": user_id,
                "total_favorites": self.favorite_count
            })
    
    def update_price(self, new_price: Decimal, currency: MarketplaceCurrency) -> None:
        """Update listing price and track price history"""
        if not self.listing or not self.listing.is_active():
            raise ValueError("Cannot update price of inactive listing")
        
        old_price = self.listing.price
        old_currency = self.listing.currency
        
        # Record price change in history
        self.price_history.append({
            "old_price": old_price,
            "new_price": new_price,
            "old_currency": old_currency.value,
            "new_currency": currency.value,
            "changed_at": datetime.now(timezone.utc)
        })
        
        # Update the Genesis NFT's listing
        if self.genesis_nft:
            self.genesis_nft.update_marketplace_listing(
                new_price=new_price,
                new_currency=currency
            )
            self.listing = self.genesis_nft.current_listing
        
        self.updated_at = datetime.now(timezone.utc)
        
        self._emit_event("marketplace_price_updated", {
            "item_id": self.item_id,
            "old_price": str(old_price),
            "new_price": str(new_price),
            "currency": currency.value
        })
    
    def get_popularity_score(self) -> Decimal:
        """Calculate popularity score based on views, favorites, and activity"""
        base_score = Decimal(str(self.view_count * 0.1 + self.favorite_count * 2))
        
        # Boost for recent activity
        days_since_update = (datetime.now(timezone.utc) - self.updated_at).days
        recency_multiplier = max(Decimal("0.1"), Decimal("1.0") - (Decimal(str(days_since_update)) * Decimal("0.1")))
        
        # Boost for price changes (indicates interest)
        price_change_bonus = Decimal(str(len(self.price_history))) * Decimal("5")
        
        return (base_score * recency_multiplier) + price_change_bonus
    
    def get_average_daily_views(self, days: int = 7) -> Decimal:
        """Get average daily views over specified period"""
        if not self.daily_views:
            return Decimal("0")
        
        # Get recent days
        recent_days = []
        for i in range(days):
            date = (datetime.now(timezone.utc) - timedelta(days=i)).strftime("%Y-%m-%d")
            recent_days.append(date)
        
        total_views = sum(self.daily_views.get(date, 0) for date in recent_days)
        return Decimal(str(total_views)) / Decimal(str(days))
    
    def get_price_trend(self) -> str:
        """Determine price trend based on price history"""
        if len(self.price_history) < 2:
            return "stable"
        
        recent_changes = self.price_history[-3:]  # Last 3 price changes
        if not recent_changes:
            return "stable"
        
        increases = sum(1 for change in recent_changes if change["new_price"] > change["old_price"])
        decreases = sum(1 for change in recent_changes if change["new_price"] < change["old_price"])
        
        if increases > decreases:
            return "increasing"
        elif decreases > increases:
            return "decreasing"
        else:
            return "stable"
    
    def is_trending(self) -> bool:
        """Check if item is currently trending"""
        popularity = self.get_popularity_score()
        avg_views = self.get_average_daily_views(3)  # Last 3 days
        
        # Trending if high popularity and recent views
        return popularity >= Decimal("50") and avg_views >= Decimal("5")
    
    def get_engagement_metrics(self) -> Dict[str, Any]:
        """Get comprehensive engagement metrics"""
        return {
            "total_views": self.view_count,
            "total_favorites": self.favorite_count,
            "popularity_score": float(self.get_popularity_score()),
            "average_daily_views": float(self.get_average_daily_views()),
            "price_changes": len(self.price_history),
            "price_trend": self.get_price_trend(),
            "is_trending": self.is_trending(),
            "days_listed": (datetime.now(timezone.utc) - self.created_at).days
        }
    
    def _emit_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """Emit domain event"""
        event = DomainEvent(
            event_type=event_type,
            entity_id=self.item_id or "unknown",
            data=data
        )
        self._domain_events.append(event)
    
    def get_domain_events(self) -> List[DomainEvent]:
        """Get and clear domain events"""
        events = self._domain_events.copy()
        self._domain_events.clear()
        return events