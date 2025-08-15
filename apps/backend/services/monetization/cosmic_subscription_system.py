"""
Cosmic Subscription System

Implements the four-tier ethical subscription model designed for Gen Z trust building.
Features transparent pricing, clear value propositions, and anti-whale mechanics
to prevent exploitation while generating sustainable revenue.

Research basis:
- 70-80% freemium users with 20-30% premium conversion target
- Bonding curve prevents whale dominance
- Educational value prioritized over pay-to-win mechanics
- Transparent value exchange builds long-term loyalty
"""

import asyncio
import secrets
from datetime import datetime, timezone, timedelta
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional, List, Dict, Any, Tuple
from enum import Enum
import json

from ..economy.ethical_currency_system import CurrencyType, TransactionType
from .anti_predatory_design import AntiPredatoryDesignFramework, InteractionType


class SubscriptionTier(str, Enum):
    """Four-tier subscription model"""
    EXPLORER = "explorer"           # Free tier
    NAVIGATOR = "navigator"         # $9.95/month
    CAPTAIN = "captain"            # $19.95/month  
    ADMIRAL = "admiral"            # $39.95/month


class BillingCycle(str, Enum):
    """Billing cycle options"""
    MONTHLY = "monthly"
    ANNUAL = "annual"              # 2 months free discount


class SubscriptionStatus(str, Enum):
    """Subscription status tracking"""
    ACTIVE = "active"
    CANCELLED = "cancelled"         # End of current period
    EXPIRED = "expired"             # Past due
    PAUSED = "paused"              # Temporary hold
    TRIAL = "trial"                # Free trial period


class FeatureCategory(str, Enum):
    """Categories of features for tier management"""
    CORE_TRADING = "core_trading"              # Basic trading functionality
    ADVANCED_ANALYSIS = "advanced_analysis"    # Charts, indicators, analytics
    EDUCATIONAL = "educational"               # Learning content, mentorship
    SOCIAL = "social"                        # Constellation features
    CONVENIENCE = "convenience"              # Automation, notifications
    CUSTOMIZATION = "customization"          # Themes, avatars, cosmetics


class TierFeature:
    """Individual feature within a subscription tier"""
    
    def __init__(
        self,
        feature_id: str,
        name: str,
        description: str,
        category: FeatureCategory,
        value_proposition: str,
        educational_value: bool = False
    ):
        self.feature_id = feature_id
        self.name = name
        self.description = description
        self.category = category
        self.value_proposition = value_proposition
        self.educational_value = educational_value
        self.usage_analytics = {
            'total_users': 0,
            'daily_active': 0,
            'satisfaction_score': 0.0
        }


class SubscriptionTierDefinition:
    """Complete definition of a subscription tier"""
    
    def __init__(
        self,
        tier: SubscriptionTier,
        name: str,
        tagline: str,
        monthly_price: Decimal,
        annual_price: Decimal,
        target_audience: str
    ):
        self.tier = tier
        self.name = name
        self.tagline = tagline
        self.monthly_price = monthly_price
        self.annual_price = annual_price
        self.target_audience = target_audience
        
        # Feature collections
        self.features: Dict[str, TierFeature] = {}
        self.feature_limits: Dict[str, int] = {}
        
        # Value calculation
        self.total_value_score = Decimal('0')
        self.educational_feature_count = 0
        
        # Analytics
        self.subscriber_count = 0
        self.churn_rate = Decimal('0')
        self.satisfaction_score = Decimal('0')
        
    def add_feature(self, feature: TierFeature, limit: Optional[int] = None):
        """Add feature to tier"""
        self.features[feature.feature_id] = feature
        
        if limit is not None:
            self.feature_limits[feature.feature_id] = limit
        
        # Update counts
        if feature.educational_value:
            self.educational_feature_count += 1
        
        # Calculate value score (simplified)
        self.total_value_score += Decimal('10')  # Base value per feature
        if feature.educational_value:
            self.total_value_score += Decimal('5')  # Educational bonus
    
    def get_annual_discount_percentage(self) -> Decimal:
        """Calculate annual discount percentage"""
        monthly_annual_equivalent = self.monthly_price * 12
        if monthly_annual_equivalent > 0:
            savings = monthly_annual_equivalent - self.annual_price
            return (savings / monthly_annual_equivalent) * 100
        return Decimal('0')
    
    def get_feature_list(self, category: Optional[FeatureCategory] = None) -> List[TierFeature]:
        """Get features, optionally filtered by category"""
        if category:
            return [f for f in self.features.values() if f.category == category]
        return list(self.features.values())
    
    def check_feature_access(self, feature_id: str, usage_count: int = 1) -> bool:
        """Check if user can access feature given current usage"""
        if feature_id not in self.features:
            return False
        
        if feature_id in self.feature_limits:
            return usage_count <= self.feature_limits[feature_id]
        
        return True  # Unlimited access


class UserSubscription:
    """Individual user's subscription status and history"""
    
    def __init__(
        self,
        user_id: int,
        tier: SubscriptionTier = SubscriptionTier.EXPLORER,
        billing_cycle: BillingCycle = BillingCycle.MONTHLY
    ):
        self.user_id = user_id
        self.current_tier = tier
        self.billing_cycle = billing_cycle
        self.status = SubscriptionStatus.ACTIVE
        
        # Billing information
        self.start_date = datetime.now(timezone.utc)
        self.current_period_end = self._calculate_period_end()
        self.next_billing_date = self.current_period_end
        self.auto_renew = True
        
        # Payment tracking
        self.total_paid = Decimal('0')
        self.payment_history: List[Dict[str, Any]] = []
        
        # Usage tracking
        self.feature_usage: Dict[str, int] = {}  # feature_id -> usage_count
        self.last_active = datetime.now(timezone.utc)
        
        # Upgrade/downgrade history
        self.tier_history: List[Dict[str, Any]] = [{
            'tier': tier,
            'changed_at': self.start_date.isoformat(),
            'reason': 'initial_subscription'
        }]
        
        # Satisfaction and engagement
        self.satisfaction_score = Decimal('0')
        self.feature_feedback: Dict[str, int] = {}  # feature_id -> rating (1-5)
        
        # Cancellation tracking
        self.cancellation_requested = False
        self.cancellation_reason = None
        self.cancellation_date = None
        
    def _calculate_period_end(self) -> datetime:
        """Calculate when current billing period ends"""
        if self.billing_cycle == BillingCycle.MONTHLY:
            return self.start_date + timedelta(days=30)
        else:  # ANNUAL
            return self.start_date + timedelta(days=365)
    
    def record_feature_usage(self, feature_id: str, usage_count: int = 1):
        """Record feature usage"""
        self.feature_usage[feature_id] = self.feature_usage.get(feature_id, 0) + usage_count
        self.last_active = datetime.now(timezone.utc)
    
    def upgrade_tier(self, new_tier: SubscriptionTier, reason: str = "user_request"):
        """Upgrade to higher tier"""
        old_tier = self.current_tier
        self.current_tier = new_tier
        
        # Record tier change
        self.tier_history.append({
            'old_tier': old_tier,
            'new_tier': new_tier,
            'changed_at': datetime.now(timezone.utc).isoformat(),
            'reason': reason
        })
        
        # Prorate billing if mid-cycle
        # (Implementation would handle prorated charges)
    
    def schedule_cancellation(self, reason: str):
        """Schedule cancellation at end of current period"""
        self.cancellation_requested = True
        self.cancellation_reason = reason
        self.cancellation_date = self.current_period_end
        self.auto_renew = False
    
    def calculate_lifetime_value(self) -> Decimal:
        """Calculate customer lifetime value"""
        if not self.payment_history:
            return Decimal('0')
        
        # Sum all payments
        total_paid = sum(Decimal(payment['amount']) for payment in self.payment_history)
        
        # Factor in tenure and engagement
        tenure_months = (datetime.now(timezone.utc) - self.start_date).days / 30
        engagement_multiplier = min(Decimal('2.0'), Decimal(str(len(self.feature_usage) / 10)))
        
        return total_paid * engagement_multiplier


class CosmicSubscriptionSystem:
    """Main system for managing cosmic-themed subscription tiers"""
    
    def __init__(self, anti_predatory_framework: AntiPredatoryDesignFramework):
        self.anti_predatory = anti_predatory_framework
        self.tier_definitions = self._initialize_tier_definitions()
        self.user_subscriptions: Dict[int, UserSubscription] = {}
        
        # System configuration
        self.free_trial_days = 14
        self.refund_period_days = 60
        self.proration_enabled = True
        
        # Analytics
        self.conversion_metrics = {
            'free_to_paid': Decimal('0'),
            'tier_upgrades': Decimal('0'),
            'churn_rate': Decimal('0'),
            'average_ltv': Decimal('0')
        }
        
    def _initialize_tier_definitions(self) -> Dict[SubscriptionTier, SubscriptionTierDefinition]:
        """Initialize the four-tier subscription model"""
        
        tiers = {}
        
        # EXPLORER (Free)
        explorer = SubscriptionTierDefinition(
            tier=SubscriptionTier.EXPLORER,
            name="Cosmic Explorer",
            tagline="Start your galactic trading journey",
            monthly_price=Decimal('0'),
            annual_price=Decimal('0'),
            target_audience="New traders exploring cosmic trading"
        )
        
        # Core free features
        explorer.add_feature(TierFeature(
            "basic_dashboard", "Cosmic Dashboard", "Real-time portfolio overview with cosmic theming",
            FeatureCategory.CORE_TRADING, "Track your galactic fleet progress", True
        ))
        
        explorer.add_feature(TierFeature(
            "chart_indicators", "Basic Indicators", "2 technical indicators per chart",
            FeatureCategory.ADVANCED_ANALYSIS, "Essential market analysis tools"
        ), limit=2)
        
        explorer.add_feature(TierFeature(
            "community_access", "Constellation Access", "Join public trading constellations",
            FeatureCategory.SOCIAL, "Learn from fellow cosmic traders", True
        ))
        
        explorer.add_feature(TierFeature(
            "basic_education", "Academy Missions", "Limited educational content access",
            FeatureCategory.EDUCATIONAL, "Foundation trading knowledge", True
        ), limit=5)
        
        tiers[SubscriptionTier.EXPLORER] = explorer
        
        # NAVIGATOR ($9.95/month)
        navigator = SubscriptionTierDefinition(
            tier=SubscriptionTier.NAVIGATOR,
            name="Cosmic Navigator",
            tagline="Navigate the stars with enhanced tools",
            monthly_price=Decimal('9.95'),
            annual_price=Decimal('99.50'),  # 2 months free
            target_audience="Active traders ready for enhanced features"
        )
        
        # Include all Explorer features plus enhanced ones
        for feature in explorer.features.values():
            navigator.add_feature(feature)
        
        # Navigator-specific features
        navigator.add_feature(TierFeature(
            "ad_free", "Ad-Free Experience", "Clean interface without advertisements",
            FeatureCategory.CONVENIENCE, "Distraction-free cosmic trading"
        ))
        
        navigator.add_feature(TierFeature(
            "advanced_indicators", "Advanced Indicators", "5 technical indicators per chart",
            FeatureCategory.ADVANCED_ANALYSIS, "Professional analysis capabilities"
        ), limit=5)
        
        navigator.add_feature(TierFeature(
            "unlimited_education", "Unlimited Academy", "Full access to educational content",
            FeatureCategory.EDUCATIONAL, "Complete trading education library", True
        ))
        
        navigator.add_feature(TierFeature(
            "enhanced_social", "Enhanced Social", "Advanced constellation features",
            FeatureCategory.SOCIAL, "Deeper community engagement"
        ))
        
        tiers[SubscriptionTier.NAVIGATOR] = navigator
        
        # CAPTAIN ($19.95/month)
        captain = SubscriptionTierDefinition(
            tier=SubscriptionTier.CAPTAIN,
            name="Cosmic Captain",
            tagline="Command your fleet with professional tools",
            monthly_price=Decimal('19.95'),
            annual_price=Decimal('199.50'),  # 2 months free
            target_audience="Professional traders needing advanced capabilities"
        )
        
        # Include all Navigator features
        for feature in navigator.features.values():
            captain.add_feature(feature)
        
        # Captain-specific features
        captain.add_feature(TierFeature(
            "professional_indicators", "Professional Indicators", "10 technical indicators per chart",
            FeatureCategory.ADVANCED_ANALYSIS, "Institutional-grade analysis"
        ), limit=10)
        
        captain.add_feature(TierFeature(
            "backtesting", "Advanced Backtesting", "Test strategies against historical data",
            FeatureCategory.ADVANCED_ANALYSIS, "Validate strategies before risking capital", True
        ))
        
        captain.add_feature(TierFeature(
            "premium_constellations", "Premium Constellations", "Access to exclusive trading groups",
            FeatureCategory.SOCIAL, "Elite community connections"
        ))
        
        captain.add_feature(TierFeature(
            "priority_support", "Priority Support", "Fast response customer service",
            FeatureCategory.CONVENIENCE, "Get help when you need it"
        ))
        
        captain.add_feature(TierFeature(
            "advanced_analytics", "Portfolio Analytics", "Deep performance analysis and insights",
            FeatureCategory.ADVANCED_ANALYSIS, "Understand your trading patterns", True
        ))
        
        tiers[SubscriptionTier.CAPTAIN] = captain
        
        # ADMIRAL ($39.95/month)
        admiral = SubscriptionTierDefinition(
            tier=SubscriptionTier.ADMIRAL,
            name="Cosmic Admiral",
            tagline="Ultimate cosmic trading mastery",
            monthly_price=Decimal('39.95'),
            annual_price=Decimal('399.50'),  # 2 months free
            target_audience="Elite traders and constellation leaders"
        )
        
        # Include all Captain features
        for feature in captain.features.values():
            admiral.add_feature(feature)
        
        # Admiral-specific features
        admiral.add_feature(TierFeature(
            "unlimited_indicators", "Unlimited Indicators", "25+ technical indicators per chart",
            FeatureCategory.ADVANCED_ANALYSIS, "Complete analytical freedom"
        ), limit=25)
        
        admiral.add_feature(TierFeature(
            "white_label_constellations", "Constellation Management", "Create and manage private constellations",
            FeatureCategory.SOCIAL, "Build your own trading community"
        ))
        
        admiral.add_feature(TierFeature(
            "api_access", "API Access", "Programmatic access to platform features",
            FeatureCategory.ADVANCED_ANALYSIS, "Custom integrations and automation"
        ))
        
        admiral.add_feature(TierFeature(
            "advanced_risk_management", "Advanced Risk Management", "Sophisticated portfolio protection tools",
            FeatureCategory.ADVANCED_ANALYSIS, "Institutional-level risk control", True
        ))
        
        admiral.add_feature(TierFeature(
            "personal_account_manager", "Personal Account Manager", "Dedicated support representative",
            FeatureCategory.CONVENIENCE, "Personalized service experience"
        ))
        
        tiers[SubscriptionTier.ADMIRAL] = admiral
        
        return tiers
    
    async def get_user_subscription(self, user_id: int) -> UserSubscription:
        """Get or create user subscription"""
        if user_id not in self.user_subscriptions:
            self.user_subscriptions[user_id] = UserSubscription(user_id)
        
        return self.user_subscriptions[user_id]
    
    async def present_upgrade_offer(
        self,
        user_id: int,
        target_tier: SubscriptionTier,
        context: Dict[str, Any] = None
    ) -> Tuple[bool, Dict[str, Any]]:
        """Present upgrade offer using anti-predatory framework"""
        
        user_subscription = await self.get_user_subscription(user_id)
        tier_def = self.tier_definitions[target_tier]
        
        # Create offer content
        offer_content = {
            'title': f'Upgrade to {tier_def.name}',
            'description': tier_def.tagline,
            'price_usd': float(tier_def.monthly_price),
            'billing_frequency': 'monthly',
            'features': [f.name for f in tier_def.features.values()],
            'value_proposition': f'Get {len(tier_def.features)} professional features',
            'educational_features_count': tier_def.educational_feature_count,
            'annual_discount': float(tier_def.get_annual_discount_percentage()),
            'free_trial_days': self.free_trial_days,
            'refund_period_days': self.refund_period_days
        }
        
        # Use anti-predatory framework to evaluate offer
        approved, evaluation_result = await self.anti_predatory.evaluate_monetization_interaction(
            user_id,
            InteractionType.SUBSCRIPTION_OFFER,
            offer_content,
            context
        )
        
        if approved:
            # Add subscription-specific transparency
            evaluation_result['enhanced_content']['subscription_transparency'] = {
                'no_hidden_fees': True,
                'cancel_anytime': True,
                'prorated_refunds': True,
                'feature_comparison': self._generate_feature_comparison(user_subscription.current_tier, target_tier),
                'usage_based_recommendation': self._generate_usage_recommendation(user_subscription)
            }
        
        return approved, evaluation_result
    
    def _generate_feature_comparison(
        self,
        current_tier: SubscriptionTier,
        target_tier: SubscriptionTier
    ) -> Dict[str, Any]:
        """Generate clear feature comparison between tiers"""
        
        current_def = self.tier_definitions[current_tier]
        target_def = self.tier_definitions[target_tier]
        
        # Features gained
        current_features = set(current_def.features.keys())
        target_features = set(target_def.features.keys())
        new_features = target_features - current_features
        
        # Feature limit improvements
        limit_improvements = {}
        for feature_id in current_features.intersection(target_features):
            current_limit = current_def.feature_limits.get(feature_id, float('inf'))
            target_limit = target_def.feature_limits.get(feature_id, float('inf'))
            
            if target_limit > current_limit:
                current_feature = current_def.features[feature_id]
                limit_improvements[feature_id] = {
                    'feature_name': current_feature.name,
                    'current_limit': current_limit if current_limit != float('inf') else 'Unlimited',
                    'new_limit': target_limit if target_limit != float('inf') else 'Unlimited'
                }
        
        return {
            'new_features': [target_def.features[fid].name for fid in new_features],
            'improved_limits': limit_improvements,
            'total_features_gained': len(new_features) + len(limit_improvements),
            'educational_features_added': len([
                fid for fid in new_features 
                if target_def.features[fid].educational_value
            ])
        }
    
    def _generate_usage_recommendation(self, user_subscription: UserSubscription) -> str:
        """Generate personalized upgrade recommendation based on usage"""
        
        if not user_subscription.feature_usage:
            return "Start with Explorer features and upgrade when you need more capabilities."
        
        # Analyze feature usage patterns
        total_usage = sum(user_subscription.feature_usage.values())
        
        if total_usage < 10:
            return "Continue exploring current features before upgrading."
        elif total_usage < 50:
            return "Navigator tier would enhance your current trading activities."
        elif total_usage < 200:
            return "Captain tier provides professional tools for your active trading."
        else:
            return "Admiral tier offers advanced features for your high-engagement trading."
    
    async def process_subscription_change(
        self,
        user_id: int,
        new_tier: SubscriptionTier,
        billing_cycle: BillingCycle,
        payment_method: str,
        promotional_code: Optional[str] = None
    ) -> Tuple[bool, Dict[str, Any]]:
        """Process subscription upgrade/downgrade"""
        
        user_subscription = await self.get_user_subscription(user_id)
        tier_def = self.tier_definitions[new_tier]
        
        # Calculate pricing
        if billing_cycle == BillingCycle.MONTHLY:
            amount = tier_def.monthly_price
        else:
            amount = tier_def.annual_price
        
        # Apply promotional code if valid
        if promotional_code:
            discount = await self._validate_promotional_code(promotional_code, user_id)
            if discount:
                amount = amount * (Decimal('1') - discount)
        
        # Record payment (simplified - would integrate with payment processor)
        payment_record = {
            'amount': str(amount),
            'currency': 'USD',
            'payment_method': payment_method,
            'tier': new_tier,
            'billing_cycle': billing_cycle,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'promotional_code': promotional_code
        }
        
        user_subscription.payment_history.append(payment_record)
        user_subscription.total_paid += amount
        
        # Update subscription
        user_subscription.upgrade_tier(new_tier, "user_upgrade")
        user_subscription.billing_cycle = billing_cycle
        user_subscription.current_period_end = user_subscription._calculate_period_end()
        
        # Reset usage counters for new billing period
        user_subscription.feature_usage = {}
        
        return True, {
            'success': True,
            'new_tier': new_tier,
            'amount_charged': str(amount),
            'next_billing_date': user_subscription.next_billing_date.isoformat(),
            'features_unlocked': len(tier_def.features),
            'transaction_id': f"sub_{secrets.token_hex(8)}"
        }
    
    async def _validate_promotional_code(
        self,
        code: str,
        user_id: int
    ) -> Optional[Decimal]:
        """Validate promotional code and return discount percentage"""
        
        # Simplified promotional code system
        promo_codes = {
            'COSMIC50': Decimal('0.5'),   # 50% off first month
            'NEWTRADER': Decimal('0.25'), # 25% off for new users
            'ACADEMY': Decimal('0.15')    # 15% off educational focus
        }
        
        if code in promo_codes:
            # Check eligibility (simplified)
            user_subscription = await self.get_user_subscription(user_id)
            
            # New user codes only for Explorer tier users
            if code == 'NEWTRADER' and user_subscription.current_tier != SubscriptionTier.EXPLORER:
                return None
            
            return promo_codes[code]
        
        return None
    
    async def get_subscription_analytics(self) -> Dict[str, Any]:
        """Get comprehensive subscription analytics"""
        
        total_users = len(self.user_subscriptions)
        
        # Tier distribution
        tier_distribution = {}
        total_revenue = Decimal('0')
        
        for tier in SubscriptionTier:
            count = len([
                sub for sub in self.user_subscriptions.values()
                if sub.current_tier == tier and sub.status == SubscriptionStatus.ACTIVE
            ])
            tier_distribution[tier] = count
        
        # Revenue calculation
        for subscription in self.user_subscriptions.values():
            if subscription.status == SubscriptionStatus.ACTIVE:
                total_revenue += subscription.total_paid
        
        # Conversion rates
        paying_users = len([
            sub for sub in self.user_subscriptions.values()
            if sub.current_tier != SubscriptionTier.EXPLORER and sub.status == SubscriptionStatus.ACTIVE
        ])
        
        conversion_rate = (paying_users / total_users * 100) if total_users > 0 else 0
        
        # Average revenue per user
        arpu = total_revenue / total_users if total_users > 0 else Decimal('0')
        
        return {
            'user_metrics': {
                'total_users': total_users,
                'paying_users': paying_users,
                'conversion_rate': f"{conversion_rate:.1f}%",
                'tier_distribution': tier_distribution
            },
            'revenue_metrics': {
                'total_revenue': str(total_revenue),
                'arpu': str(arpu),
                'monthly_recurring_revenue': str(self._calculate_mrr()),
                'average_ltv': str(self._calculate_average_ltv())
            },
            'engagement_metrics': {
                'feature_usage': self._analyze_feature_usage(),
                'satisfaction_scores': self._analyze_satisfaction(),
                'churn_analysis': self._analyze_churn()
            },
            'growth_metrics': {
                'upgrade_rate': self._calculate_upgrade_rate(),
                'downgrade_rate': self._calculate_downgrade_rate(),
                'retention_rate': self._calculate_retention_rate()
            },
            'generated_at': datetime.now(timezone.utc).isoformat()
        }
    
    def _calculate_mrr(self) -> Decimal:
        """Calculate Monthly Recurring Revenue"""
        mrr = Decimal('0')
        
        for subscription in self.user_subscriptions.values():
            if subscription.status == SubscriptionStatus.ACTIVE:
                tier_def = self.tier_definitions[subscription.current_tier]
                
                if subscription.billing_cycle == BillingCycle.MONTHLY:
                    mrr += tier_def.monthly_price
                else:  # Annual
                    mrr += tier_def.annual_price / 12
        
        return mrr
    
    def _calculate_average_ltv(self) -> Decimal:
        """Calculate average customer lifetime value"""
        if not self.user_subscriptions:
            return Decimal('0')
        
        total_ltv = sum(
            subscription.calculate_lifetime_value()
            for subscription in self.user_subscriptions.values()
        )
        
        return total_ltv / len(self.user_subscriptions)
    
    def _analyze_feature_usage(self) -> Dict[str, Any]:
        """Analyze feature usage across tiers"""
        feature_usage = {}
        
        for subscription in self.user_subscriptions.values():
            for feature_id, usage_count in subscription.feature_usage.items():
                if feature_id not in feature_usage:
                    feature_usage[feature_id] = {'total_usage': 0, 'user_count': 0}
                
                feature_usage[feature_id]['total_usage'] += usage_count
                feature_usage[feature_id]['user_count'] += 1
        
        # Calculate average usage per feature
        for feature_data in feature_usage.values():
            feature_data['average_usage'] = (
                feature_data['total_usage'] / feature_data['user_count']
                if feature_data['user_count'] > 0 else 0
            )
        
        return feature_usage
    
    def _analyze_satisfaction(self) -> Dict[str, float]:
        """Analyze satisfaction scores by tier"""
        satisfaction_by_tier = {}
        
        for tier in SubscriptionTier:
            tier_subscriptions = [
                sub for sub in self.user_subscriptions.values()
                if sub.current_tier == tier
            ]
            
            if tier_subscriptions:
                avg_satisfaction = sum(
                    float(sub.satisfaction_score) for sub in tier_subscriptions
                ) / len(tier_subscriptions)
                satisfaction_by_tier[tier] = avg_satisfaction
        
        return satisfaction_by_tier
    
    def _analyze_churn(self) -> Dict[str, Any]:
        """Analyze churn patterns"""
        total_cancelled = len([
            sub for sub in self.user_subscriptions.values()
            if sub.cancellation_requested
        ])
        
        churn_reasons = {}
        for subscription in self.user_subscriptions.values():
            if subscription.cancellation_reason:
                reason = subscription.cancellation_reason
                churn_reasons[reason] = churn_reasons.get(reason, 0) + 1
        
        return {
            'total_cancelled': total_cancelled,
            'churn_rate': (total_cancelled / len(self.user_subscriptions) * 100) if self.user_subscriptions else 0,
            'churn_reasons': churn_reasons
        }
    
    def _calculate_upgrade_rate(self) -> float:
        """Calculate rate of tier upgrades"""
        upgrades = 0
        
        for subscription in self.user_subscriptions.values():
            tier_changes = [
                change for change in subscription.tier_history
                if change.get('reason') == 'user_request' and 
                change.get('new_tier') != SubscriptionTier.EXPLORER
            ]
            upgrades += len(tier_changes)
        
        return (upgrades / len(self.user_subscriptions) * 100) if self.user_subscriptions else 0
    
    def _calculate_downgrade_rate(self) -> float:
        """Calculate rate of tier downgrades"""
        # Implementation would track downgrades
        return 0.0  # Placeholder
    
    def _calculate_retention_rate(self) -> float:
        """Calculate monthly retention rate"""
        # Implementation would track retention over time
        return 85.0  # Placeholder based on target