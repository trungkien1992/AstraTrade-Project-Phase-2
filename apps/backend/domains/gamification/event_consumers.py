"""
Gamification Domain Event Consumers

Cross-domain event consumers that process events from other domains
to calculate XP, achievements, and progression updates.
"""

import asyncio
import json
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from decimal import Decimal

# Import gamification components
try:
    from .events import create_xp_gained_event, create_level_up_event, create_gamification_event
    from .services import GamificationService
    from .entities import UserXP, Achievement
except ImportError:
    print("Warning: Gamification domain components not available")

# Import shared event system
import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'shared'))

try:
    from redis_streams import RedisStreamsEventBus, create_redis_event
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    print("Warning: Redis integration not available")


class GamificationEventConsumer:
    """
    Primary consumer for gamification events from other domains.
    
    Processes events to calculate XP, detect achievements, and update
    user progression across the entire AstraTrade platform.
    """
    
    def __init__(self, event_bus: RedisStreamsEventBus, gamification_service=None):
        self.event_bus = event_bus
        self.gamification_service = gamification_service
        self.domain = "gamification"
        
        # Achievement configuration
        self.achievement_config = self._load_achievement_config()
        
        # XP calculation rules
        self.xp_rules = self._load_xp_rules()
    
    async def handle_trading_event(self, event_data: Dict[str, Any]) -> None:
        """
        Handle trading events and calculate gamification rewards.
        
        Processing flow:
        1. Parse trading event data
        2. Calculate XP based on activity type and amount
        3. Check for achievement unlocks
        4. Update user progression
        5. Publish gamification events
        """
        event_type = event_data.get('event_type', '')
        correlation_id = event_data.get('correlation_id', '')
        
        print(f"🎮 Gamification processing: {event_type}")
        print(f"   Correlation ID: {correlation_id}")
        
        if event_type == "Trading.TradeExecuted":
            await self._process_trade_execution(event_data, correlation_id)
        
        elif event_type == "Trading.TradingRewardsCalculated":
            await self._process_trading_rewards(event_data, correlation_id)
        
        elif event_type == "Trading.ClanBattleScoreUpdated":
            await self._process_clan_battle_score(event_data, correlation_id)
    
    async def handle_social_event(self, event_data: Dict[str, Any]) -> None:
        """Handle social events and calculate social XP."""
        event_type = event_data.get('event_type', '')
        correlation_id = event_data.get('correlation_id', '')
        
        print(f"🎮 Gamification processing social: {event_type}")
        
        if event_type == "Social.SocialInteractionPerformed":
            await self._process_social_interaction(event_data, correlation_id)
        
        elif event_type == "Social.ConstellationCreated":
            await self._process_constellation_creation(event_data, correlation_id)
        
        elif event_type == "Social.ViralContentShared":
            await self._process_viral_content(event_data, correlation_id)
    
    async def handle_nft_event(self, event_data: Dict[str, Any]) -> None:
        """Handle NFT events and calculate collection XP."""
        event_type = event_data.get('event_type', '')
        correlation_id = event_data.get('correlation_id', '')
        
        print(f"🎮 Gamification processing NFT: {event_type}")
        
        if event_type == "NFT.NFTMinted":
            await self._process_nft_mint(event_data, correlation_id)
        
        elif event_type == "NFT.MarketplaceSale":
            await self._process_nft_sale(event_data, correlation_id)
    
    async def _process_trade_execution(self, event_data: Dict[str, Any], correlation_id: str) -> None:
        """Process trade execution for XP calculation."""
        data = self._parse_event_data(event_data)
        
        user_id = data.get('user_id')
        amount = Decimal(str(data.get('amount', '0')))
        pnl = Decimal(str(data.get('pnl_usd', '0')))
        
        if not user_id:
            return
        
        # Calculate XP based on trading rules
        base_xp = self._calculate_trading_xp(amount, pnl)
        
        # Check for trading achievements
        achievements = await self._check_trading_achievements(user_id, data)
        
        # Create and publish XP gained event
        xp_event = create_redis_event(
            event_type="Gamification.XPGained",
            domain=self.domain,
            entity_id=f"user_{user_id}",
            data={
                "user_id": user_id,
                "activity_type": "trading",
                "xp_amount": base_xp,
                "total_xp": await self._get_user_total_xp(user_id) + base_xp,
                "source_event": "trade_execution",
                "trade_amount": str(amount),
                "trade_pnl": str(pnl)
            },
            correlation_id=correlation_id,
            causation_id=event_data.get('event_id')
        )
        
        await self.event_bus.emit(xp_event)
        print(f"   ✨ Generated {base_xp} XP for user {user_id}")
        
        # Process achievements if any
        for achievement in achievements:
            await self._publish_achievement_unlock(user_id, achievement, correlation_id)
        
        # Check for level up
        await self._check_and_process_level_up(user_id, base_xp, correlation_id)
    
    async def _process_trading_rewards(self, event_data: Dict[str, Any], correlation_id: str) -> None:
        """Process pre-calculated trading rewards."""
        data = self._parse_event_data(event_data)
        
        user_id = data.get('user_id')
        xp_gained = data.get('xp_gained', 0)
        achievements = data.get('achievements_unlocked', [])
        
        if not user_id:
            return
        
        # Update user XP
        new_total_xp = await self._update_user_xp(user_id, xp_gained)
        
        # Process achievements
        for achievement_id in achievements:
            achievement_data = self.achievement_config.get(achievement_id, {})
            if achievement_data:
                await self._publish_achievement_unlock(user_id, achievement_data, correlation_id)
        
        # Check for level up
        await self._check_and_process_level_up(user_id, xp_gained, correlation_id)
        
        print(f"   🎯 Processed rewards: {xp_gained} XP, {len(achievements)} achievements")
    
    async def _process_social_interaction(self, event_data: Dict[str, Any], correlation_id: str) -> None:
        """Process social interactions for social XP."""
        data = self._parse_event_data(event_data)
        
        user_id = data.get('user_id')
        interaction_type = data.get('interaction_type', 'unknown')
        
        # Calculate social XP
        social_xp = self.xp_rules['social'].get(interaction_type, 5)  # Default 5 XP
        
        # Create social XP event
        xp_event = create_redis_event(
            event_type="Gamification.XPGained",
            domain=self.domain,
            entity_id=f"user_{user_id}",
            data={
                "user_id": user_id,
                "activity_type": "social",
                "xp_amount": social_xp,
                "interaction_type": interaction_type,
                "total_xp": await self._get_user_total_xp(user_id) + social_xp
            },
            correlation_id=correlation_id,
            causation_id=event_data.get('event_id')
        )
        
        await self.event_bus.emit(xp_event)
        print(f"   👥 Social XP: {social_xp} for {interaction_type}")
    
    async def _process_nft_mint(self, event_data: Dict[str, Any], correlation_id: str) -> None:
        """Process NFT minting for collector XP."""
        data = self._parse_event_data(event_data)
        
        user_id = data.get('user_id')
        nft_rarity = data.get('rarity', 'common')
        
        # Calculate NFT XP based on rarity
        nft_xp = self.xp_rules['nft']['mint'].get(nft_rarity, 10)
        
        xp_event = create_redis_event(
            event_type="Gamification.XPGained",
            domain=self.domain,
            entity_id=f"user_{user_id}",
            data={
                "user_id": user_id,
                "activity_type": "nft_collection",
                "xp_amount": nft_xp,
                "nft_rarity": nft_rarity,
                "total_xp": await self._get_user_total_xp(user_id) + nft_xp
            },
            correlation_id=correlation_id,
            causation_id=event_data.get('event_id')
        )
        
        await self.event_bus.emit(xp_event)
        print(f"   🎨 NFT mint XP: {nft_xp} for {nft_rarity} NFT")
    
    def _calculate_trading_xp(self, amount: Decimal, pnl: Decimal) -> int:
        """Calculate XP from trading activity."""
        # Base XP: 1 XP per $100 traded
        base_xp = max(1, int(amount / 100))
        
        # Profit bonus: 1 XP per $10 profit
        profit_bonus = max(0, int(pnl / 10)) if pnl > 0 else 0
        
        # Volume bonus for large trades
        volume_bonus = max(0, int((amount - 1000) / 500)) if amount > 1000 else 0
        
        return base_xp + profit_bonus + volume_bonus
    
    async def _check_trading_achievements(self, user_id: int, trade_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check for trading-related achievement unlocks."""
        achievements = []
        
        pnl = Decimal(str(trade_data.get('pnl_usd', '0')))
        amount = Decimal(str(trade_data.get('amount', '0')))
        
        # Profitable trade achievement
        if pnl > 0:
            achievements.append({
                "id": "profitable_trade",
                "name": "Profitable Trader",
                "description": "Complete a profitable trade",
                "xp_reward": 25
            })
        
        # High volume achievement
        if amount > 5000:
            achievements.append({
                "id": "high_volume_trader",
                "name": "High Volume Trader", 
                "description": "Execute a trade over $5,000",
                "xp_reward": 50
            })
        
        # Big winner achievement
        if pnl > 500:
            achievements.append({
                "id": "big_winner",
                "name": "Big Winner",
                "description": "Earn over $500 profit in a single trade",
                "xp_reward": 100
            })
        
        return achievements
    
    async def _publish_achievement_unlock(self, user_id: int, achievement: Dict[str, Any], correlation_id: str) -> None:
        """Publish achievement unlock event."""
        achievement_event = create_redis_event(
            event_type="Gamification.AchievementUnlocked",
            domain=self.domain,
            entity_id=f"achievement_{achievement['id']}",
            data={
                "user_id": user_id,
                "achievement_id": achievement["id"],
                "achievement_name": achievement["name"],
                "description": achievement["description"],
                "xp_reward": achievement.get("xp_reward", 0)
            },
            correlation_id=correlation_id
        )
        
        await self.event_bus.emit(achievement_event)
        print(f"   🏆 Achievement unlocked: {achievement['name']}")
    
    async def _check_and_process_level_up(self, user_id: int, xp_gained: int, correlation_id: str) -> None:
        """Check if user leveled up and publish event."""
        current_total_xp = await self._get_user_total_xp(user_id)
        new_total_xp = current_total_xp + xp_gained
        
        old_level = self._calculate_level(current_total_xp)
        new_level = self._calculate_level(new_total_xp)
        
        if new_level > old_level:
            level_rewards = self._get_level_rewards(new_level)
            
            level_event = create_redis_event(
                event_type="Gamification.LevelUp",
                domain=self.domain,
                entity_id=f"user_{user_id}",
                data={
                    "user_id": user_id,
                    "old_level": old_level,
                    "new_level": new_level,
                    "total_xp": new_total_xp,
                    "rewards_unlocked": level_rewards
                },
                correlation_id=correlation_id
            )
            
            await self.event_bus.emit(level_event)
            print(f"   🆙 Level up! User {user_id}: {old_level} → {new_level}")
    
    def _calculate_level(self, total_xp: int) -> int:
        """Calculate user level from total XP."""
        # Simple level calculation: level = floor(sqrt(xp/100)) + 1
        import math
        return min(100, max(1, int(math.sqrt(total_xp / 100)) + 1))
    
    def _get_level_rewards(self, level: int) -> List[str]:
        """Get rewards for reaching a specific level."""
        rewards = []
        
        if level % 5 == 0:  # Every 5 levels
            rewards.append("bonus_xp_multiplier")
        
        if level % 10 == 0:  # Every 10 levels
            rewards.append("exclusive_badge")
            rewards.append("trading_bonus")
        
        if level in [25, 50, 75, 100]:  # Milestone levels
            rewards.append("milestone_nft")
        
        return rewards
    
    async def _get_user_total_xp(self, user_id: int) -> int:
        """Get user's current total XP (mock implementation)."""
        # In real implementation, would query database
        return 1250  # Mock current XP
    
    async def _update_user_xp(self, user_id: int, xp_gained: int) -> int:
        """Update user's XP in database (mock implementation)."""
        current_xp = await self._get_user_total_xp(user_id)
        new_total = current_xp + xp_gained
        # Would update database here
        return new_total
    
    def _parse_event_data(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse event data from various formats."""
        data = event_data.get('data', {})
        if isinstance(data, str):
            try:
                return json.loads(data)
            except json.JSONDecodeError:
                return {}
        return data
    
    def _load_achievement_config(self) -> Dict[str, Dict[str, Any]]:
        """Load achievement configuration."""
        return {
            "profitable_trade": {
                "name": "Profitable Trader",
                "description": "Complete a profitable trade",
                "xp_reward": 25
            },
            "high_volume_trader": {
                "name": "High Volume Trader",
                "description": "Execute a trade over $5,000", 
                "xp_reward": 50
            },
            "big_winner": {
                "name": "Big Winner",
                "description": "Earn over $500 profit in a single trade",
                "xp_reward": 100
            },
            "social_butterfly": {
                "name": "Social Butterfly",
                "description": "Complete 10 social interactions",
                "xp_reward": 30
            }
        }
    
    def _load_xp_rules(self) -> Dict[str, Dict[str, Any]]:
        """Load XP calculation rules."""
        return {
            "trading": {
                "base_per_100_usd": 1,
                "profit_per_10_usd": 1,
                "volume_bonus_threshold": 1000
            },
            "social": {
                "like": 2,
                "comment": 5,
                "share": 10,
                "follow": 3,
                "constellation_join": 20
            },
            "nft": {
                "mint": {
                    "common": 10,
                    "uncommon": 25,
                    "rare": 50,
                    "epic": 100,
                    "legendary": 250
                }
            }
        }
    
    async def start_consuming(self) -> None:
        """Start consuming events from other domains."""
        print("🎮 Starting Gamification event consumers...")
        
        # Subscribe to trading events
        await self.event_bus.subscribe(
            "astra.trading.*",
            "gamification_xp_processors",
            self.handle_trading_event
        )
        
        # Subscribe to social events
        await self.event_bus.subscribe(
            "astra.social.*",
            "gamification_xp_processors", 
            self.handle_social_event
        )
        
        # Subscribe to NFT events
        await self.event_bus.subscribe(
            "astra.nft.*",
            "gamification_xp_processors",
            self.handle_nft_event
        )
        
        print("✅ Gamification consumers active")


# Example usage and testing
async def test_gamification_consumer():
    """Test gamification event consumer."""
    print("🔧 Testing Gamification Event Consumer")
    print("=" * 50)
    
    if not REDIS_AVAILABLE:
        print("📝 Redis not available - using mock events")
    
    # Create mock event bus
    class MockEventBus:
        async def emit(self, event): 
            print(f"📡 Mock emit: {event['event_type']}")
        async def subscribe(self, pattern, group, handler):
            print(f"📡 Mock subscribe: {pattern} -> {group}")
    
    event_bus = MockEventBus() if not REDIS_AVAILABLE else RedisStreamsEventBus()
    
    try:
        # Create consumer
        consumer = GamificationEventConsumer(event_bus)
        
        # Test trading event processing
        trade_event = {
            "event_id": "test_123",
            "event_type": "Trading.TradeExecuted",
            "correlation_id": "test_correlation",
            "data": {
                "user_id": 123,
                "amount": "1500.00",
                "pnl_usd": "75.50",
                "asset_symbol": "STRK"
            }
        }
        
        print("📊 Processing test trading event...")
        await consumer.handle_trading_event(trade_event)
        
        # Test social event processing
        social_event = {
            "event_id": "social_123",
            "event_type": "Social.SocialInteractionPerformed",
            "correlation_id": "test_correlation", 
            "data": {
                "user_id": 123,
                "interaction_type": "like"
            }
        }
        
        print("\n👥 Processing test social event...")
        await consumer.handle_social_event(social_event)
        
        print("\n✅ Gamification consumer test completed")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    finally:
        if hasattr(event_bus, 'close'):
            await event_bus.close()


if __name__ == "__main__":
    asyncio.run(test_gamification_consumer())