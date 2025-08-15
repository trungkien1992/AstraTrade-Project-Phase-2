"""
NFT Domain

Handles Genesis NFT minting, marketplace operations, and collection management
as defined in ADR-001 Domain-Driven Design implementation.

This domain manages:
- Genesis NFT minting based on user achievements
- NFT marketplace with buying, selling, and listing functionality
- NFT collection management and analytics
- NFT revenue tracking for marketplace transactions
- Integration with blockchain contracts for minting and transfers

Domain Structure:
- value_objects.py: NFTMetadata, AchievementCriteria, Rarity, etc.
- entities.py: GenesisNFT, NFTCollection, MarketplaceItem
- services.py: NFTMintingService, MarketplaceService, CollectionService
- events.py: Domain events for NFT operations

Integration Points:
- Financial Domain: Marketplace transaction fees and revenue tracking
- Gamification Domain: Achievement validation for minting eligibility
- User Domain: NFT ownership verification and user preferences
- Trading Domain: Trading performance metrics for achievement-based NFTs
"""

__version__ = "1.0.0"
__domain__ = "nft"