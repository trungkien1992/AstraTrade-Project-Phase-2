"""
Redis Streams Consumer Groups Configuration

Defines consumer groups for each domain and cross-domain event processing.
Implements the consumer group strategy for horizontal scaling and load distribution.
"""

from dataclasses import dataclass
from typing import Dict, List, Callable, Any
from enum import Enum


class ConsumerGroupType(Enum):
    """Types of consumer groups for different processing patterns."""
    DOMAIN_INTERNAL = "domain_internal"  # Process events within same domain
    CROSS_DOMAIN = "cross_domain"        # Process events from other domains
    ANALYTICS = "analytics"              # Process events for analytics/reporting
    AUDIT = "audit"                      # Process events for audit trails


@dataclass
class ConsumerGroupConfig:
    """Configuration for a Redis Streams consumer group."""
    name: str
    stream_patterns: List[str]
    consumer_count: int
    group_type: ConsumerGroupType
    description: str
    handler_function: str = None  # Name of handler function
    
    def get_redis_commands(self) -> List[str]:
        """Generate Redis commands to create this consumer group."""
        commands = []
        for pattern in self.stream_patterns:
            commands.append(
                f"XGROUP CREATE {pattern} {self.name} 0 MKSTREAM"
            )
        return commands


class AstraTradeConsumerGroups:
    """
    Centralized configuration for all AstraTrade consumer groups.
    
    Defines the complete consumer group architecture for cross-domain
    event processing and microservices communication.
    """
    
    # Trading Domain Consumer Groups
    TRADING_CONSUMERS = [
        ConsumerGroupConfig(
            name="trading_internal",
            stream_patterns=["astra.trading.*"],
            consumer_count=2,
            group_type=ConsumerGroupType.DOMAIN_INTERNAL,
            description="Process internal trading events (risk management, portfolio updates)",
            handler_function="handle_trading_internal_event"
        ),
        ConsumerGroupConfig(
            name="trading_risk_management",
            stream_patterns=["astra.trading.tradeexecuted.*", "astra.trading.positionclosed.*"],
            consumer_count=3,
            group_type=ConsumerGroupType.DOMAIN_INTERNAL,
            description="High-priority risk management and compliance processing",
            handler_function="handle_risk_management_event"
        )
    ]
    
    # Gamification Domain Consumer Groups
    GAMIFICATION_CONSUMERS = [
        ConsumerGroupConfig(
            name="gamification_xp_processors",
            stream_patterns=["astra.trading.traderewardsCalculated.*", "astra.social.socialinteraction.*"],
            consumer_count=2,
            group_type=ConsumerGroupType.CROSS_DOMAIN,
            description="Process XP calculation from trading and social activities",
            handler_function="handle_xp_calculation_event"
        ),
        ConsumerGroupConfig(
            name="leaderboard_updaters", 
            stream_patterns=["astra.gamification.xpgained.*", "astra.gamification.levelup.*"],
            consumer_count=1,
            group_type=ConsumerGroupType.DOMAIN_INTERNAL,
            description="Update leaderboards and rankings",
            handler_function="handle_leaderboard_update_event"
        ),
        ConsumerGroupConfig(
            name="achievement_processors",
            stream_patterns=["astra.*.*.v1"],  # Listen to all events for achievement detection
            consumer_count=1,
            group_type=ConsumerGroupType.CROSS_DOMAIN,
            description="Detect and unlock achievements across all domains",
            handler_function="handle_achievement_detection_event"
        )
    ]
    
    # Social Domain Consumer Groups
    SOCIAL_CONSUMERS = [
        ConsumerGroupConfig(
            name="social_feed_generators",
            stream_patterns=["astra.trading.tradeexecuted.*", "astra.gamification.levelup.*", "astra.nft.nftsold.*"],
            consumer_count=2,
            group_type=ConsumerGroupType.CROSS_DOMAIN,
            description="Generate social feed content from cross-domain events",
            handler_function="handle_social_feed_generation"
        ),
        ConsumerGroupConfig(
            name="clan_battle_processors",
            stream_patterns=["astra.trading.clanbattlescoreupdated.*"],
            consumer_count=1,
            group_type=ConsumerGroupType.CROSS_DOMAIN,
            description="Process clan battle scores and rankings",
            handler_function="handle_clan_battle_event"
        ),
        ConsumerGroupConfig(
            name="influence_calculators",
            stream_patterns=["astra.social.*"],
            consumer_count=1,
            group_type=ConsumerGroupType.DOMAIN_INTERNAL,
            description="Calculate influence scores from social interactions",
            handler_function="handle_influence_calculation"
        )
    ]
    
    # Financial Domain Consumer Groups
    FINANCIAL_CONSUMERS = [
        ConsumerGroupConfig(
            name="revenue_trackers",
            stream_patterns=["astra.trading.tradeexecuted.*", "astra.nft.marketplacesale.*"],
            consumer_count=1,
            group_type=ConsumerGroupType.CROSS_DOMAIN,
            description="Track revenue from trading fees and NFT marketplace",
            handler_function="handle_revenue_tracking_event"
        ),
        ConsumerGroupConfig(
            name="subscription_processors",
            stream_patterns=["astra.financial.paymentcompleted.*", "astra.user.accountstatuschanged.*"],
            consumer_count=1,
            group_type=ConsumerGroupType.CROSS_DOMAIN,
            description="Process subscription payments and account upgrades",
            handler_function="handle_subscription_event"
        ),
        ConsumerGroupConfig(
            name="financial_compliance",
            stream_patterns=["astra.financial.*"],
            consumer_count=1,
            group_type=ConsumerGroupType.AUDIT,
            description="Ensure compliance and audit trail for financial operations",
            handler_function="handle_compliance_audit"
        )
    ]
    
    # NFT Domain Consumer Groups
    NFT_CONSUMERS = [
        ConsumerGroupConfig(
            name="nft_reward_distributors",
            stream_patterns=["astra.gamification.achievementunlocked.*", "astra.trading.traderewardscalculated.*"],
            consumer_count=1,
            group_type=ConsumerGroupType.CROSS_DOMAIN,
            description="Distribute NFT rewards based on achievements and trading",
            handler_function="handle_nft_reward_distribution"
        ),
        ConsumerGroupConfig(
            name="marketplace_processors",
            stream_patterns=["astra.nft.nftlisted.*", "astra.nft.nftsold.*"],
            consumer_count=2,
            group_type=ConsumerGroupType.DOMAIN_INTERNAL,
            description="Process NFT marketplace transactions",
            handler_function="handle_marketplace_event"
        )
    ]
    
    # User Domain Consumer Groups
    USER_CONSUMERS = [
        ConsumerGroupConfig(
            name="user_profile_updaters",
            stream_patterns=["astra.gamification.levelup.*", "astra.social.socialratingchanged.*"],
            consumer_count=1,
            group_type=ConsumerGroupType.CROSS_DOMAIN,
            description="Update user profiles based on gamification and social changes",
            handler_function="handle_profile_update_event"
        ),
        ConsumerGroupConfig(
            name="notification_senders",
            stream_patterns=["astra.*.*.v1"],  # All events for notifications
            consumer_count=3,
            group_type=ConsumerGroupType.CROSS_DOMAIN,
            description="Send real-time notifications to users",
            handler_function="handle_notification_event"
        )
    ]
    
    # Analytics and Monitoring Consumer Groups
    ANALYTICS_CONSUMERS = [
        ConsumerGroupConfig(
            name="metrics_collectors",
            stream_patterns=["astra.*.*.v1"],  # All events for metrics
            consumer_count=2,
            group_type=ConsumerGroupType.ANALYTICS,
            description="Collect metrics and KPIs from all domain events",
            handler_function="handle_metrics_collection"
        ),
        ConsumerGroupConfig(
            name="audit_trail_recorders",
            stream_patterns=["astra.financial.*", "astra.trading.*", "astra.nft.*"],
            consumer_count=1,
            group_type=ConsumerGroupType.AUDIT,
            description="Record audit trails for compliance and security",
            handler_function="handle_audit_recording"
        )
    ]
    
    @classmethod
    def get_all_consumer_groups(cls) -> List[ConsumerGroupConfig]:
        """Get all configured consumer groups."""
        all_groups = []
        all_groups.extend(cls.TRADING_CONSUMERS)
        all_groups.extend(cls.GAMIFICATION_CONSUMERS)
        all_groups.extend(cls.SOCIAL_CONSUMERS)
        all_groups.extend(cls.FINANCIAL_CONSUMERS)
        all_groups.extend(cls.NFT_CONSUMERS)
        all_groups.extend(cls.USER_CONSUMERS)
        all_groups.extend(cls.ANALYTICS_CONSUMERS)
        return all_groups
    
    @classmethod
    def get_consumer_groups_by_domain(cls, domain: str) -> List[ConsumerGroupConfig]:
        """Get consumer groups that process events for a specific domain."""
        domain_groups = {
            'trading': cls.TRADING_CONSUMERS,
            'gamification': cls.GAMIFICATION_CONSUMERS,
            'social': cls.SOCIAL_CONSUMERS,
            'financial': cls.FINANCIAL_CONSUMERS,
            'nft': cls.NFT_CONSUMERS,
            'user': cls.USER_CONSUMERS,
            'analytics': cls.ANALYTICS_CONSUMERS
        }
        return domain_groups.get(domain.lower(), [])
    
    @classmethod
    def get_cross_domain_consumers(cls) -> List[ConsumerGroupConfig]:
        """Get all cross-domain consumer groups."""
        return [
            group for group in cls.get_all_consumer_groups()
            if group.group_type == ConsumerGroupType.CROSS_DOMAIN
        ]
    
    @classmethod
    def generate_redis_setup_script(cls) -> str:
        """Generate Redis CLI script to create all consumer groups."""
        script_lines = [
            "#!/bin/bash",
            "# AstraTrade Redis Streams Consumer Groups Setup",
            "# Auto-generated configuration script",
            "",
            "echo 'Creating AstraTrade consumer groups...'",
            ""
        ]
        
        for group in cls.get_all_consumer_groups():
            script_lines.append(f"# {group.description}")
            for command in group.get_redis_commands():
                script_lines.append(f"redis-cli {command} || echo 'Group {group.name} may already exist'")
            script_lines.append("")
        
        script_lines.extend([
            "echo 'Consumer group setup completed!'",
            "echo 'Total groups created: " + str(len(cls.get_all_consumer_groups())) + "'",
            "",
            "# Verify consumer groups",
            "echo 'Verifying consumer groups...'",
            "redis-cli XINFO GROUPS astra.trading.tradeexecuted.v1 2>/dev/null || echo 'No trading streams yet'",
            "redis-cli XINFO GROUPS astra.gamification.xpgained.v1 2>/dev/null || echo 'No gamification streams yet'",
            ""
        ])
        
        return "\n".join(script_lines)


# Stream Naming Convention Reference
STREAM_NAMING_CONVENTION = {
    "pattern": "astra.{domain}.{event_name}.v{version}",
    "examples": {
        "trading": [
            "astra.trading.tradeexecuted.v1",
            "astra.trading.tradeclosed.v1", 
            "astra.trading.clanbattlescoreupdated.v1"
        ],
        "gamification": [
            "astra.gamification.xpgained.v1",
            "astra.gamification.levelup.v1",
            "astra.gamification.achievementunlocked.v1"
        ],
        "social": [
            "astra.social.socialprofilecreated.v1",
            "astra.social.constellationcreated.v1",
            "astra.social.viralcontentshared.v1"
        ],
        "financial": [
            "astra.financial.paymentcompleted.v1",
            "astra.financial.subscriptioncreated.v1",
            "astra.financial.invoicepaid.v1"
        ],
        "nft": [
            "astra.nft.nftminted.v1",
            "astra.nft.marketplacesale.v1",
            "astra.nft.collectioncreated.v1"
        ],
        "user": [
            "astra.user.userregistered.v1",
            "astra.user.profileupdated.v1",
            "astra.user.sessionstarted.v1"
        ]
    }
}


def print_consumer_group_summary():
    """Print summary of all configured consumer groups."""
    print("🔧 AstraTrade Consumer Groups Configuration")
    print("=" * 60)
    
    all_groups = AstraTradeConsumerGroups.get_all_consumer_groups()
    cross_domain = AstraTradeConsumerGroups.get_cross_domain_consumers()
    
    print(f"Total Consumer Groups: {len(all_groups)}")
    print(f"Cross-Domain Groups: {len(cross_domain)}")
    print(f"Internal Groups: {len(all_groups) - len(cross_domain)}")
    print()
    
    # Group by domain
    domains = ['trading', 'gamification', 'social', 'financial', 'nft', 'user', 'analytics']
    
    for domain in domains:
        domain_groups = AstraTradeConsumerGroups.get_consumer_groups_by_domain(domain)
        if domain_groups:
            print(f"📊 {domain.title()} Domain ({len(domain_groups)} groups):")
            for group in domain_groups:
                print(f"   • {group.name} ({group.consumer_count} consumers)")
                print(f"     {group.description}")
                print(f"     Streams: {', '.join(group.stream_patterns)}")
            print()
    
    print("🌐 Cross-Domain Event Flows:")
    for group in cross_domain:
        print(f"   • {group.name}: {group.description}")
    
    print("\n📋 Stream Naming Convention:")
    print(f"   Pattern: {STREAM_NAMING_CONVENTION['pattern']}")
    print("   Examples:")
    for domain, examples in STREAM_NAMING_CONVENTION['examples'].items():
        print(f"     {domain.title()}: {examples[0]}")


if __name__ == "__main__":
    print_consumer_group_summary()
    
    print("\n" + "=" * 60)
    print("🔧 Redis Setup Script:")
    print(AstraTradeConsumerGroups.generate_redis_setup_script())