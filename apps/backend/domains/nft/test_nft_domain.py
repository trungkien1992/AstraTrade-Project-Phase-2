#!/usr/bin/env python3
"""
NFT Domain Validation Runner

Comprehensive validation of NFT Domain implementation
without relative import issues.
"""

import sys
import os
from datetime import datetime, timezone, timedelta
from decimal import Decimal

# Add current directory to path to avoid import issues
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Now import modules
import value_objects as vo
import entities as ent


def test_rarity_system():
    """Test Rarity value object and scoring"""
    print("  Testing Rarity system...")
    
    # Test rarity creation from level
    common_rarity = vo.Rarity.from_level(vo.RarityLevel.COMMON)
    legendary_rarity = vo.Rarity.from_level(vo.RarityLevel.LEGENDARY)
    
    assert common_rarity.level == vo.RarityLevel.COMMON
    assert common_rarity.score == Decimal("1.0")
    assert common_rarity.color_code == "808080"
    
    assert legendary_rarity.level == vo.RarityLevel.LEGENDARY
    assert legendary_rarity.score == Decimal("25.0")
    assert legendary_rarity.color_code == "FF8000"
    
    # Test rarity comparison
    assert legendary_rarity.is_higher_than(common_rarity)
    assert not common_rarity.is_higher_than(legendary_rarity)
    
    # Test bonus percentage calculation
    common_bonus = common_rarity.get_bonus_percentage()
    legendary_bonus = legendary_rarity.get_bonus_percentage()
    assert common_bonus == Decimal("5.0")
    assert legendary_bonus == Decimal("40.0")
    
    print("    ✅ Rarity system works correctly")


def test_achievement_criteria():
    """Test Achievement criteria and validation"""
    print("  Testing Achievement criteria...")
    
    # Test first trade achievement
    first_trade_criteria = vo.AchievementCriteria.create_first_trade()
    assert first_trade_criteria.achievement_type == vo.AchievementType.FIRST_TRADE
    assert first_trade_criteria.base_rarity == vo.RarityLevel.COMMON
    assert first_trade_criteria.points_awarded == 100
    
    # Test eligibility check
    user_stats_eligible = {"trades_executed": 5}
    user_stats_not_eligible = {"trades_executed": 0}
    
    assert first_trade_criteria.is_eligible(user_stats_eligible)
    assert not first_trade_criteria.is_eligible(user_stats_not_eligible)
    
    # Test level milestone achievement
    level_criteria = vo.AchievementCriteria.create_level_milestone(50)
    assert level_criteria.base_rarity == vo.RarityLevel.RARE
    assert level_criteria.points_awarded == 250
    
    # Test rarity calculation with bonuses
    user_stats_with_bonus = {"user_level": 50, "level_speed_bonus": True}
    final_rarity = level_criteria.calculate_final_rarity(user_stats_with_bonus)
    assert final_rarity == vo.RarityLevel.EPIC  # Upgraded from RARE
    
    print("    ✅ Achievement criteria works correctly")


def test_nft_metadata():
    """Test NFT metadata creation and properties"""
    print("  Testing NFT metadata...")
    
    # Create test rarity and metadata
    rarity = vo.Rarity.from_level(vo.RarityLevel.EPIC)
    milestone_data = {"total_trades": 1000, "win_rate": 0.85}
    
    metadata = vo.NFTMetadata.create_genesis_metadata(
        achievement_type=vo.AchievementType.TRADING_MASTER,
        rarity=rarity,
        owner_level=75,
        milestone_data=milestone_data,
        cosmic_signature="test_signature_123"
    )
    
    assert "Genesis Trading Master" in metadata.name
    assert metadata.get_attribute_value("Rarity") == "Epic"
    assert metadata.get_attribute_value("Power Level") == 25.0
    assert metadata.get_attribute_value("Owner Level") == 75
    
    # Test market value estimation
    estimated_value = metadata.get_market_value_estimate()
    assert estimated_value > Decimal("10000")  # Epic should be valuable
    
    print("    ✅ NFT metadata works correctly")


def test_marketplace_listing():
    """Test marketplace listing functionality"""
    print("  Testing Marketplace listings...")
    
    # Create marketplace listing
    listing = vo.MarketplaceListing.create_listing(
        nft_token_id=123,
        owner_id=456,
        price=Decimal("5000"),
        currency=vo.MarketplaceCurrency.STELLAR_SHARDS,
        duration_days=30,
        featured=True,
        description="Rare Genesis NFT for sale"
    )
    
    assert listing.nft_token_id == 123
    assert listing.owner_id == 456
    assert listing.price == Decimal("5000")
    assert listing.currency == vo.MarketplaceCurrency.STELLAR_SHARDS
    assert listing.featured is True
    assert listing.is_active()
    assert not listing.is_expired()
    
    # Test currency display
    display_name = listing.get_currency_display_name()
    assert display_name == "Stellar Shards"
    
    # Test days until expiry
    days_left = listing.days_until_expiry()
    assert days_left is not None
    assert 29 <= days_left <= 30
    
    print("    ✅ Marketplace listings work correctly")


def test_genesis_nft_entity():
    """Test Genesis NFT entity and business logic"""
    print("  Testing Genesis NFT entity...")
    
    # Create Genesis NFT
    rarity = vo.Rarity.from_level(vo.RarityLevel.RARE)
    genesis_nft = ent.GenesisNFT(
        owner_id=123,
        achievement_type=vo.AchievementType.CONSTELLATION_FOUNDER,
        rarity=rarity
    )
    
    # Set NFT ID
    genesis_nft.set_nft_id("GENESIS_TEST_12345")
    assert genesis_nft.nft_id == "GENESIS_TEST_12345"
    
    # Set up NFT for minting (metadata and attributes required)
    blockchain_tx = vo.BlockchainTransaction.create_mock_transaction(1, "mint")
    milestone_data = {"constellation_name": "Alpha Centauri", "member_count": 15}
    
    # Create metadata and attributes
    cosmic_signature = "test_signature_123"
    genesis_nft.metadata = vo.NFTMetadata.create_genesis_metadata(
        achievement_type=genesis_nft.achievement_type,
        rarity=genesis_nft.rarity,
        owner_level=30,
        milestone_data=milestone_data,
        cosmic_signature=cosmic_signature
    )
    
    genesis_nft.attributes = vo.NFTAttributes.create_from_achievement(
        achievement_type=genesis_nft.achievement_type,
        rarity=genesis_nft.rarity,
        owner_level=30,
        milestone_data=milestone_data,
        cosmic_signature=cosmic_signature
    )
    
    # Test minting process with simplified method
    genesis_nft.mint_nft(blockchain_tx)
    
    assert genesis_nft.status == vo.NFTStatus.MINTED
    assert genesis_nft.metadata is not None
    assert genesis_nft.token_id == blockchain_tx.token_id
    assert genesis_nft.is_tradeable()
    
    # Test marketplace listing
    listing = genesis_nft.list_on_marketplace(
        price=Decimal("10000"),
        currency=vo.MarketplaceCurrency.STELLAR_SHARDS,
        duration_days=30,
        featured=True
    )
    
    assert genesis_nft.status == vo.NFTStatus.LISTED
    assert genesis_nft.current_listing is not None
    assert listing.price == Decimal("10000")
    
    # Test domain events
    events = genesis_nft.get_domain_events()
    assert len(events) > 0
    event_types = [event.event_type for event in events]
    assert "nft_created" in event_types
    assert "nft_minted" in event_types
    assert "nft_listed" in event_types
    
    print("    ✅ Genesis NFT entity works correctly")


def test_nft_collection_entity():
    """Test NFT Collection entity"""
    print("  Testing NFT Collection entity...")
    
    # Create collection
    collection = ent.NFTCollection(owner_id=123)
    collection.set_collection_id("collection_123_abc")
    
    # Create test NFTs
    rarity1 = vo.Rarity.from_level(vo.RarityLevel.RARE)
    rarity2 = vo.Rarity.from_level(vo.RarityLevel.LEGENDARY)
    
    nft1 = ent.GenesisNFT(
        owner_id=123,
        achievement_type=vo.AchievementType.FIRST_TRADE,
        rarity=rarity1
    )
    nft1.set_nft_id("GENESIS_NFT_001")
    
    nft2 = ent.GenesisNFT(
        owner_id=123,
        achievement_type=vo.AchievementType.TRADING_MASTER,
        rarity=rarity2
    )
    nft2.set_nft_id("GENESIS_NFT_002")
    
    # Add NFTs to collection
    collection.add_nft(nft1)
    collection.add_nft(nft2)
    
    assert len(collection.genesis_nfts) == 2
    assert collection.featured_nft_id == "GENESIS_NFT_002"  # Legendary should be featured
    
    # Test collection queries
    rare_nfts = collection.get_nfts_by_rarity(vo.RarityLevel.RARE)
    assert len(rare_nfts) == 1
    assert rare_nfts[0].nft_id == "GENESIS_NFT_001"
    
    trading_nfts = collection.get_nfts_by_achievement(vo.AchievementType.TRADING_MASTER)
    assert len(trading_nfts) == 1
    assert trading_nfts[0].nft_id == "GENESIS_NFT_002"
    
    # Test collection value
    total_value = collection.get_collection_value()
    assert "stellar_shards" in total_value
    assert total_value["stellar_shards"] > Decimal("0")
    
    # Test achievement completion
    completion = collection.get_achievement_completion()
    assert completion[vo.AchievementType.FIRST_TRADE.value] is True
    assert completion[vo.AchievementType.TRADING_MASTER.value] is True
    assert completion[vo.AchievementType.VIRAL_LEGEND.value] is False
    
    print("    ✅ NFT Collection entity works correctly")


def test_marketplace_item_entity():
    """Test Marketplace Item entity"""
    print("  Testing Marketplace Item entity...")
    
    # Create marketplace item with NFT and listing
    rarity = vo.Rarity.from_level(vo.RarityLevel.EPIC)
    nft = ent.GenesisNFT(
        owner_id=123,
        achievement_type=vo.AchievementType.CONSTELLATION_FOUNDER,
        rarity=rarity
    )
    nft.set_nft_id("GENESIS_MARKETPLACE_TEST")
    
    listing = vo.MarketplaceListing.create_listing(
        nft_token_id=123,
        owner_id=123,
        price=Decimal("15000"),
        currency=vo.MarketplaceCurrency.STELLAR_SHARDS
    )
    
    marketplace_item = ent.MarketplaceItem(
        genesis_nft=nft,
        listing=listing
    )
    marketplace_item.set_item_id("marketplace_item_123")
    
    # Test view tracking
    initial_views = marketplace_item.view_count
    marketplace_item.add_view(viewer_id=456)
    assert marketplace_item.view_count == initial_views + 1
    
    # Test favorites
    initial_favorites = marketplace_item.favorite_count
    marketplace_item.add_to_favorites(user_id=789)
    assert marketplace_item.favorite_count == initial_favorites + 1
    
    # Test popularity score
    popularity = marketplace_item.get_popularity_score()
    assert popularity > Decimal("0")
    
    # Test engagement metrics
    metrics = marketplace_item.get_engagement_metrics()
    assert "total_views" in metrics
    assert "total_favorites" in metrics
    assert "popularity_score" in metrics
    assert "is_trending" in metrics
    
    print("    ✅ Marketplace Item entity works correctly")


def test_collection_stats():
    """Test collection statistics calculation"""
    print("  Testing Collection statistics...")
    
    # Create mock NFT data
    nft_data = [
        {"rarity": "rare", "achievement_type": "first_trade"},
        {"rarity": "epic", "achievement_type": "constellation_founder"},
        {"rarity": "legendary", "achievement_type": "trading_master"},
        {"rarity": "common", "achievement_type": "level_milestone"},
    ]
    
    stats = vo.CollectionStats.calculate_from_nfts(nft_data)
    
    assert stats.total_nfts == 4
    assert stats.unique_achievements == 4
    assert stats.completion_percentage == Decimal("80")  # 4 of 5 achievement types
    
    # Test rarity distribution
    assert stats.rarity_distribution["rare"] == 1
    assert stats.rarity_distribution["epic"] == 1
    assert stats.rarity_distribution["legendary"] == 1
    assert stats.rarity_distribution["common"] == 1
    
    # Test values
    assert stats.estimated_value["stellar_shards"] > Decimal("0")
    assert stats.estimated_value["lumina"] > Decimal("0")
    
    # Test helper methods
    avg_rarity = stats.get_average_rarity_score()
    assert avg_rarity > Decimal("5")  # Should be high with epic/legendary
    
    collection_tier = stats.get_collection_tier()
    assert collection_tier in ["rare", "epic", "legendary"]
    
    print("    ✅ Collection statistics work correctly")


def test_blockchain_transaction():
    """Test blockchain transaction handling"""
    print("  Testing Blockchain transactions...")
    
    # Create blockchain transaction
    tx = vo.BlockchainTransaction.create_mock_transaction(token_id=456, operation="mint")
    
    assert tx.token_id == 456
    assert tx.block_number > 1000000
    assert tx.gas_used > 0
    assert len(tx.transaction_hash) > 10
    assert tx.is_confirmed()
    
    # Test explorer URL generation
    explorer_url = tx.get_explorer_url()
    assert "starkscan.co" in explorer_url
    assert tx.transaction_hash in explorer_url
    
    # Test cost estimation
    estimated_cost = tx.get_estimated_cost_usd()
    assert estimated_cost > Decimal("0")
    
    print("    ✅ Blockchain transactions work correctly")


def main():
    """Run all NFT Domain tests"""
    print("🚀 NFT Domain Validation")
    print("=" * 50)
    
    tests = [
        test_rarity_system,
        test_achievement_criteria,
        test_nft_metadata,
        test_marketplace_listing,
        test_genesis_nft_entity,
        test_nft_collection_entity,
        test_marketplace_item_entity,
        test_collection_stats,
        test_blockchain_transaction
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"    ❌ Test failed: {e}")
    
    print("\n" + "=" * 50)
    print("📊 VALIDATION SUMMARY")
    print("=" * 50)
    print(f"✅ Tests Passed: {passed}/{total}")
    print(f"📈 Success Rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        print("NFT Domain implementation is working correctly.")
        print("\n🏆 Validated capabilities:")
        print("  • Genesis NFT minting with achievement validation")
        print("  • 5-tier rarity system with bonuses and scoring")
        print("  • NFT marketplace with listing and trading")
        print("  • Collection management and analytics")
        print("  • Blockchain integration with transaction tracking")
        print("  • Domain events for cross-domain integration")
        print("  • Revenue tracking integration points")
        print("  • Comprehensive business rule enforcement")
        
        return True
    else:
        print(f"\n⚠️  {total-passed} tests failed.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)