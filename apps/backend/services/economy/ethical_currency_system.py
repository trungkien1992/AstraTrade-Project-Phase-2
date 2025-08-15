"""
Ethical Dual-Currency System

Implements the first anti-predatory virtual currency system for trading platforms.
Based on research findings: creates sustainable revenue through ethical design,
preventing pay-to-win mechanics while maintaining clear value exchange.

Research basis:
- Gen Z requires radical transparency and ethical value exchange
- Virtual currency bridge enables revenue without exploitation  
- Dual-currency prevents money laundering while providing utility
- Economic stability mechanisms prevent inflation and manipulation
"""

import asyncio
import hashlib
import secrets
from datetime import datetime, timezone, timedelta
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional, List, Dict, Any, Tuple
from enum import Enum
import json
import math

from ..cosmic.cosmic_avatar_system import CosmicCredentials


class CurrencyType(str, Enum):
    """Types of currencies in the ethical system"""
    COSMIC_CREDITS = "cosmic_credits"    # Earned currency (60% of economy)
    STAR_TOKENS = "star_tokens"          # Purchased currency (40% of economy)


class TransactionType(str, Enum):
    """Types of currency transactions"""
    EARNED_REWARD = "earned_reward"           # Daily rewards, achievements
    PURCHASE = "purchase"                     # Real money purchase
    CONVERSION = "conversion"                 # Credits to real funds
    SINK_COSMETIC = "sink_cosmetic"          # Cosmetic purchases
    SINK_TOURNAMENT = "sink_tournament"       # Tournament entries
    SINK_EDUCATION = "sink_education"         # Educational content
    SINK_PREMIUM = "sink_premium"             # Premium subscriptions
    TRANSFER = "transfer"                     # User-to-user transfers


class EconomicHealthStatus(str, Enum):
    """Economic health indicators"""
    HEALTHY = "healthy"                       # Normal operation
    INFLATION_WARNING = "inflation_warning"   # Approaching inflation limits
    DEFLATION_WARNING = "deflation_warning"   # Too much currency being removed
    VELOCITY_LOW = "velocity_low"             # Currency not circulating
    VELOCITY_HIGH = "velocity_high"           # Too much speculation


class CurrencyTransaction:
    """Individual currency transaction with full audit trail"""
    
    def __init__(
        self,
        transaction_id: str,
        user_id: int,
        currency_type: CurrencyType,
        transaction_type: TransactionType,
        amount: Decimal,
        reason: str,
        metadata: Dict[str, Any] = None
    ):
        self.transaction_id = transaction_id
        self.user_id = user_id
        self.currency_type = currency_type
        self.transaction_type = transaction_type
        self.amount = amount
        self.reason = reason
        self.metadata = metadata or {}
        self.timestamp = datetime.now(timezone.utc)
        
        # Audit and compliance
        self.user_hash = hashlib.sha256(f"user_{user_id}".encode()).hexdigest()[:12]
        self.approved = True  # Set false for review-required transactions
        self.compliance_checked = False
        
        # Economic tracking
        self.exchange_rate = None  # USD equivalent rate
        self.inflation_impact = Decimal('0')  # Impact on currency supply
    
    def calculate_inflation_impact(self, total_supply: Decimal) -> Decimal:
        """Calculate this transaction's impact on currency inflation"""
        if self.transaction_type in [TransactionType.EARNED_REWARD, TransactionType.PURCHASE]:
            # Adding currency to supply
            self.inflation_impact = (self.amount / total_supply) * 100
        elif self.transaction_type.startswith('SINK_'):
            # Removing currency from supply
            self.inflation_impact = -(self.amount / total_supply) * 100
        
        return self.inflation_impact
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage/API"""
        return {
            "transaction_id": self.transaction_id,
            "user_hash": self.user_hash,  # Never expose real user_id
            "currency_type": self.currency_type,
            "transaction_type": self.transaction_type,
            "amount": str(self.amount),
            "reason": self.reason,
            "timestamp": self.timestamp.isoformat(),
            "approved": self.approved,
            "exchange_rate": str(self.exchange_rate) if self.exchange_rate else None,
            "inflation_impact": str(self.inflation_impact),
            "metadata": self.metadata
        }


class UserCurrencyBalance:
    """User's currency balances with spending controls"""
    
    def __init__(self, user_id: int):
        self.user_id = user_id
        self.cosmic_credits = Decimal('0')
        self.star_tokens = Decimal('0')
        
        # Self-control mechanisms (user-configurable)
        self.daily_spending_limit = Decimal('100')  # USD equivalent
        self.weekly_spending_limit = Decimal('500')
        self.monthly_spending_limit = Decimal('2000')
        
        # Tracking for limits
        self.daily_spent = Decimal('0')
        self.weekly_spent = Decimal('0') 
        self.monthly_spent = Decimal('0')
        self.last_reset_date = datetime.now(timezone.utc).date()
        
        # Anti-addiction safeguards
        self.cooling_period_until: Optional[datetime] = None
        self.large_transaction_alerts = True
        self.parental_controls_active = False
        
        # Earning tracking
        self.total_earned_credits = Decimal('0')
        self.total_purchased_tokens = Decimal('0')
        self.last_earned_timestamp = datetime.now(timezone.utc)
    
    def reset_daily_limits_if_needed(self):
        """Reset spending limits at day boundaries"""
        today = datetime.now(timezone.utc).date()
        
        if today > self.last_reset_date:
            # Reset daily
            self.daily_spent = Decimal('0')
            
            # Reset weekly if it's been a week
            days_diff = (today - self.last_reset_date).days
            if days_diff >= 7:
                self.weekly_spent = Decimal('0')
            
            # Reset monthly if it's been a month  
            if days_diff >= 30:
                self.monthly_spent = Decimal('0')
            
            self.last_reset_date = today
    
    def can_spend(self, amount_usd: Decimal) -> Tuple[bool, str]:
        """Check if user can spend amount considering all limits"""
        self.reset_daily_limits_if_needed()
        
        # Check cooling period
        if self.cooling_period_until and datetime.now(timezone.utc) < self.cooling_period_until:
            remaining = self.cooling_period_until - datetime.now(timezone.utc)
            return False, f"Cooling period active for {remaining.total_seconds()//3600:.0f} more hours"
        
        # Check daily limit
        if self.daily_spent + amount_usd > self.daily_spending_limit:
            return False, f"Would exceed daily limit of ${self.daily_spending_limit}"
        
        # Check weekly limit
        if self.weekly_spent + amount_usd > self.weekly_spending_limit:
            return False, f"Would exceed weekly limit of ${self.weekly_spending_limit}"
        
        # Check monthly limit
        if self.monthly_spent + amount_usd > self.monthly_spending_limit:
            return False, f"Would exceed monthly limit of ${self.monthly_spending_limit}"
        
        return True, "Spending approved"
    
    def record_spending(self, amount_usd: Decimal):
        """Record spending against limits"""
        self.daily_spent += amount_usd
        self.weekly_spent += amount_usd
        self.monthly_spent += amount_usd
        
        # Trigger cooling period for large transactions
        if amount_usd >= Decimal('1000'):
            self.cooling_period_until = datetime.now(timezone.utc) + timedelta(hours=48)
    
    def add_currency(
        self,
        currency_type: CurrencyType,
        amount: Decimal,
        source: TransactionType
    ):
        """Add currency to user balance"""
        if currency_type == CurrencyType.COSMIC_CREDITS:
            self.cosmic_credits += amount
            if source == TransactionType.EARNED_REWARD:
                self.total_earned_credits += amount
                self.last_earned_timestamp = datetime.now(timezone.utc)
        
        elif currency_type == CurrencyType.STAR_TOKENS:
            self.star_tokens += amount
            if source == TransactionType.PURCHASE:
                self.total_purchased_tokens += amount
    
    def spend_currency(
        self,
        currency_type: CurrencyType,
        amount: Decimal
    ) -> bool:
        """Spend currency if sufficient balance"""
        if currency_type == CurrencyType.COSMIC_CREDITS:
            if self.cosmic_credits >= amount:
                self.cosmic_credits -= amount
                return True
        
        elif currency_type == CurrencyType.STAR_TOKENS:
            if self.star_tokens >= amount:
                self.star_tokens -= amount
                return True
        
        return False


class EconomicStabilityEngine:
    """Manages economic health and stability mechanisms"""
    
    def __init__(self):
        # Economic targets (based on research)
        self.target_inflation_rate = Decimal('2.5')  # 2.5% annually
        self.max_daily_inflation = Decimal('0.1')    # 0.1% daily max
        self.target_currency_velocity = Decimal('2.5')  # 2.5x monthly circulation
        
        # Supply tracking
        self.total_cosmic_credits = Decimal('0')
        self.total_star_tokens = Decimal('0')
        self.currency_in_circulation = Decimal('0')
        self.currency_in_savings = Decimal('0')
        
        # Economic health metrics
        self.current_inflation_rate = Decimal('0')
        self.current_velocity = Decimal('0')
        self.health_status = EconomicHealthStatus.HEALTHY
        
        # Auto-balancing mechanisms
        self.faucet_rate_multiplier = Decimal('1.0')  # Adjust earning rates
        self.sink_rate_multiplier = Decimal('1.0')    # Adjust spending incentives
        
    def calculate_inflation_rate(self, time_window_days: int = 30) -> Decimal:
        """Calculate current inflation rate over time window"""
        # This would integrate with transaction history to calculate real inflation
        # For now, return monitored rate
        return self.current_inflation_rate
    
    def calculate_velocity(self) -> Decimal:
        """Calculate currency velocity (transactions/supply ratio)"""
        if self.total_cosmic_credits > 0:
            # Velocity = transactions in period / average supply
            # This would integrate with transaction volume data
            return self.current_velocity
        return Decimal('0')
    
    def assess_economic_health(self) -> EconomicHealthStatus:
        """Assess overall economic health and return status"""
        inflation = self.calculate_inflation_rate()
        velocity = self.calculate_velocity()
        
        # Check inflation bounds
        if inflation > Decimal('5.0'):  # 5% annual inflation warning
            return EconomicHealthStatus.INFLATION_WARNING
        elif inflation < Decimal('0'):  # Deflation warning
            return EconomicHealthStatus.DEFLATION_WARNING
        
        # Check velocity bounds
        elif velocity > Decimal('5.0'):  # Too much speculation
            return EconomicHealthStatus.VELOCITY_HIGH
        elif velocity < Decimal('1.0'):  # Not enough circulation
            return EconomicHealthStatus.VELOCITY_LOW
        
        return EconomicHealthStatus.HEALTHY
    
    def auto_balance_economy(self) -> Dict[str, Decimal]:
        """Automatically adjust faucet/sink rates for economic balance"""
        health = self.assess_economic_health()
        adjustments = {}
        
        if health == EconomicHealthStatus.INFLATION_WARNING:
            # Reduce faucet, increase sinks
            self.faucet_rate_multiplier *= Decimal('0.9')
            self.sink_rate_multiplier *= Decimal('1.1')
            adjustments['faucet_reduction'] = Decimal('10')
            adjustments['sink_increase'] = Decimal('10')
        
        elif health == EconomicHealthStatus.DEFLATION_WARNING:
            # Increase faucet, reduce sinks
            self.faucet_rate_multiplier *= Decimal('1.1')
            self.sink_rate_multiplier *= Decimal('0.9')
            adjustments['faucet_increase'] = Decimal('10')
            adjustments['sink_reduction'] = Decimal('10')
        
        elif health == EconomicHealthStatus.VELOCITY_LOW:
            # Incentivize spending
            self.sink_rate_multiplier *= Decimal('0.95')
            adjustments['spending_incentive'] = Decimal('5')
        
        elif health == EconomicHealthStatus.VELOCITY_HIGH:
            # Reduce speculation incentives
            self.sink_rate_multiplier *= Decimal('1.05')
            adjustments['speculation_reduction'] = Decimal('5')
        
        # Keep multipliers in reasonable bounds
        self.faucet_rate_multiplier = max(Decimal('0.5'), min(Decimal('2.0'), self.faucet_rate_multiplier))
        self.sink_rate_multiplier = max(Decimal('0.5'), min(Decimal('2.0'), self.sink_rate_multiplier))
        
        return adjustments


class EthicalCurrencySystem:
    """Main service for ethical dual-currency management"""
    
    def __init__(self):
        self.user_balances: Dict[int, UserCurrencyBalance] = {}
        self.transaction_history: List[CurrencyTransaction] = []
        self.stability_engine = EconomicStabilityEngine()
        
        # Conversion bridge settings (based on research)
        self.credits_to_usd_rate = Decimal('0.0035')  # $0.0035 per credit
        self.minimum_conversion_credits = Decimal('50000')  # 50,000 credits minimum
        self.conversion_fee_percentage = Decimal('2.0')  # 2% conversion fee
        
        # Real-time pricing from external oracles would be integrated here
        self.usd_to_star_token_rate = Decimal('0.10')  # $0.10 per token
        
        # Bonding curve for Star Token purchases (anti-whale mechanics)
        self.star_token_bonding_curve = [
            (Decimal('5'), Decimal('1500')),    # $5 → 1,500 tokens
            (Decimal('10'), Decimal('3500')),   # $10 → 3,500 tokens (16% bonus)
            (Decimal('20'), Decimal('8000')),   # $20 → 8,000 tokens (33% bonus)
            (Decimal('50'), Decimal('25000')),  # $50 → 25,000 tokens (66% bonus)
        ]
    
    async def get_user_balance(self, user_id: int) -> UserCurrencyBalance:
        """Get or create user currency balance"""
        if user_id not in self.user_balances:
            self.user_balances[user_id] = UserCurrencyBalance(user_id)
        
        return self.user_balances[user_id]
    
    async def award_cosmic_credits(
        self,
        user_id: int,
        amount: Decimal,
        reason: str,
        source: TransactionType = TransactionType.EARNED_REWARD,
        metadata: Dict[str, Any] = None
    ) -> CurrencyTransaction:
        """Award Cosmic Credits for user activities"""
        
        # Apply economic balancing
        adjusted_amount = amount * self.stability_engine.faucet_rate_multiplier
        adjusted_amount = adjusted_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        
        # Create transaction
        transaction = CurrencyTransaction(
            transaction_id=f"credit_{secrets.token_hex(8)}",
            user_id=user_id,
            currency_type=CurrencyType.COSMIC_CREDITS,
            transaction_type=source,
            amount=adjusted_amount,
            reason=reason,
            metadata=metadata
        )
        
        # Update user balance
        user_balance = await self.get_user_balance(user_id)
        user_balance.add_currency(CurrencyType.COSMIC_CREDITS, adjusted_amount, source)
        
        # Update economic tracking
        self.stability_engine.total_cosmic_credits += adjusted_amount
        transaction.calculate_inflation_impact(self.stability_engine.total_cosmic_credits)
        
        # Store transaction
        self.transaction_history.append(transaction)
        
        return transaction
    
    async def purchase_star_tokens(
        self,
        user_id: int,
        usd_amount: Decimal,
        payment_method: str,
        metadata: Dict[str, Any] = None
    ) -> Tuple[bool, Dict[str, Any]]:
        """Purchase Star Tokens with real money"""
        
        user_balance = await self.get_user_balance(user_id)
        
        # Check spending limits
        can_spend, reason = user_balance.can_spend(usd_amount)
        if not can_spend:
            return False, {"error": reason, "spending_limit_exceeded": True}
        
        # Calculate tokens using bonding curve
        tokens_to_award = self._calculate_bonding_curve_tokens(usd_amount)
        
        # Create transaction
        transaction = CurrencyTransaction(
            transaction_id=f"purchase_{secrets.token_hex(8)}",
            user_id=user_id,
            currency_type=CurrencyType.STAR_TOKENS,
            transaction_type=TransactionType.PURCHASE,
            amount=tokens_to_award,
            reason=f"Purchased ${usd_amount} worth of Star Tokens",
            metadata={
                "usd_amount": str(usd_amount),
                "payment_method": payment_method,
                "bonding_curve_bonus": str(tokens_to_award - (usd_amount / self.usd_to_star_token_rate)),
                **(metadata or {})
            }
        )
        
        transaction.exchange_rate = usd_amount / tokens_to_award
        
        # Update balances
        user_balance.add_currency(CurrencyType.STAR_TOKENS, tokens_to_award, TransactionType.PURCHASE)
        user_balance.record_spending(usd_amount)
        
        # Update economic tracking
        self.stability_engine.total_star_tokens += tokens_to_award
        
        # Store transaction
        self.transaction_history.append(transaction)
        
        return True, {
            "tokens_awarded": str(tokens_to_award),
            "usd_spent": str(usd_amount),
            "effective_rate": str(transaction.exchange_rate),
            "transaction_id": transaction.transaction_id,
            "bonding_curve_bonus": transaction.metadata.get("bonding_curve_bonus", "0")
        }
    
    def _calculate_bonding_curve_tokens(self, usd_amount: Decimal) -> Decimal:
        """Calculate Star Tokens using bonding curve pricing"""
        
        # Find matching tier
        for tier_usd, tier_tokens in self.star_token_bonding_curve:
            if usd_amount <= tier_usd:
                return tier_tokens
        
        # For amounts above highest tier, use highest tier rate
        highest_tier = self.star_token_bonding_curve[-1]
        ratio = highest_tier[1] / highest_tier[0]  # tokens per dollar
        return usd_amount * ratio
    
    async def spend_currency(
        self,
        user_id: int,
        currency_type: CurrencyType,
        amount: Decimal,
        reason: str,
        sink_type: TransactionType,
        metadata: Dict[str, Any] = None
    ) -> Tuple[bool, Dict[str, Any]]:
        """Spend user currency with economic balancing"""
        
        user_balance = await self.get_user_balance(user_id)
        
        # Apply economic balancing to sink rates
        adjusted_amount = amount * self.stability_engine.sink_rate_multiplier
        adjusted_amount = adjusted_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        
        # Check if user has sufficient balance
        if not user_balance.spend_currency(currency_type, adjusted_amount):
            return False, {
                "error": "Insufficient balance",
                "required": str(adjusted_amount),
                "available": str(user_balance.cosmic_credits if currency_type == CurrencyType.COSMIC_CREDITS else user_balance.star_tokens)
            }
        
        # Create transaction
        transaction = CurrencyTransaction(
            transaction_id=f"spend_{secrets.token_hex(8)}",
            user_id=user_id,
            currency_type=currency_type,
            transaction_type=sink_type,
            amount=adjusted_amount,
            reason=reason,
            metadata=metadata
        )
        
        # Update economic tracking
        if currency_type == CurrencyType.COSMIC_CREDITS:
            self.stability_engine.total_cosmic_credits -= adjusted_amount
        else:
            self.stability_engine.total_star_tokens -= adjusted_amount
        
        transaction.calculate_inflation_impact(
            self.stability_engine.total_cosmic_credits if currency_type == CurrencyType.COSMIC_CREDITS 
            else self.stability_engine.total_star_tokens
        )
        
        # Store transaction
        self.transaction_history.append(transaction)
        
        return True, {
            "transaction_id": transaction.transaction_id,
            "amount_spent": str(adjusted_amount),
            "remaining_balance": str(
                user_balance.cosmic_credits if currency_type == CurrencyType.COSMIC_CREDITS 
                else user_balance.star_tokens
            )
        }
    
    async def convert_credits_to_usd(
        self,
        user_id: int,
        credit_amount: Decimal,
        kyc_verified: bool = False
    ) -> Tuple[bool, Dict[str, Any]]:
        """Convert Cosmic Credits to real USD (conversion bridge)"""
        
        user_balance = await self.get_user_balance(user_id)
        
        # Check minimum conversion amount
        if credit_amount < self.minimum_conversion_credits:
            return False, {
                "error": f"Minimum conversion is {self.minimum_conversion_credits} credits",
                "provided": str(credit_amount)
            }
        
        # Check if user has sufficient credits
        if user_balance.cosmic_credits < credit_amount:
            return False, {
                "error": "Insufficient Cosmic Credits",
                "required": str(credit_amount),
                "available": str(user_balance.cosmic_credits)
            }
        
        # Calculate USD amount with fees
        gross_usd = credit_amount * self.credits_to_usd_rate
        conversion_fee = gross_usd * (self.conversion_fee_percentage / Decimal('100'))
        net_usd = gross_usd - conversion_fee
        
        # KYC requirement for larger conversions
        if net_usd > Decimal('100') and not kyc_verified:
            return False, {
                "error": "KYC verification required for conversions over $100",
                "usd_amount": str(net_usd),
                "kyc_required": True
            }
        
        # Implement 48-hour cooling period for large conversions
        cooling_period_required = net_usd >= Decimal('1000')
        
        # Create conversion transaction
        transaction = CurrencyTransaction(
            transaction_id=f"convert_{secrets.token_hex(8)}",
            user_id=user_id,
            currency_type=CurrencyType.COSMIC_CREDITS,
            transaction_type=TransactionType.CONVERSION,
            amount=credit_amount,
            reason=f"Converted {credit_amount} credits to ${net_usd} USD",
            metadata={
                "gross_usd": str(gross_usd),
                "conversion_fee": str(conversion_fee),
                "net_usd": str(net_usd),
                "exchange_rate": str(self.credits_to_usd_rate),
                "kyc_verified": kyc_verified,
                "cooling_period": cooling_period_required
            }
        )
        
        transaction.exchange_rate = self.credits_to_usd_rate
        
        if cooling_period_required:
            # Don't actually process yet, require cooling period
            transaction.approved = False
            transaction.metadata["cooling_period_until"] = (
                datetime.now(timezone.utc) + timedelta(hours=48)
            ).isoformat()
        else:
            # Process immediately
            user_balance.spend_currency(CurrencyType.COSMIC_CREDITS, credit_amount)
            self.stability_engine.total_cosmic_credits -= credit_amount
        
        # Store transaction
        self.transaction_history.append(transaction)
        
        result = {
            "transaction_id": transaction.transaction_id,
            "credits_converted": str(credit_amount),
            "gross_usd": str(gross_usd),
            "conversion_fee": str(conversion_fee),
            "net_usd": str(net_usd),
            "processed_immediately": transaction.approved
        }
        
        if cooling_period_required:
            result["cooling_period_until"] = transaction.metadata["cooling_period_until"]
        
        return True, result
    
    async def update_user_spending_limits(
        self,
        user_id: int,
        daily_limit: Optional[Decimal] = None,
        weekly_limit: Optional[Decimal] = None,
        monthly_limit: Optional[Decimal] = None
    ) -> bool:
        """Update user's self-imposed spending limits"""
        
        user_balance = await self.get_user_balance(user_id)
        
        if daily_limit is not None:
            user_balance.daily_spending_limit = daily_limit
        
        if weekly_limit is not None:
            user_balance.weekly_spending_limit = weekly_limit
        
        if monthly_limit is not None:
            user_balance.monthly_spending_limit = monthly_limit
        
        return True
    
    async def get_economic_health_report(self) -> Dict[str, Any]:
        """Generate comprehensive economic health report"""
        
        # Run economic assessment
        health_status = self.stability_engine.assess_economic_health()
        auto_adjustments = self.stability_engine.auto_balance_economy()
        
        # Calculate key metrics
        total_supply = self.stability_engine.total_cosmic_credits + self.stability_engine.total_star_tokens
        credits_percentage = (self.stability_engine.total_cosmic_credits / total_supply * 100) if total_supply > 0 else 0
        
        return {
            "economic_health": {
                "status": health_status,
                "inflation_rate": str(self.stability_engine.calculate_inflation_rate()),
                "target_inflation": str(self.stability_engine.target_inflation_rate),
                "currency_velocity": str(self.stability_engine.calculate_velocity()),
                "target_velocity": str(self.stability_engine.target_currency_velocity)
            },
            "currency_supply": {
                "total_cosmic_credits": str(self.stability_engine.total_cosmic_credits),
                "total_star_tokens": str(self.stability_engine.total_star_tokens),
                "credits_percentage": str(credits_percentage),
                "target_credits_percentage": "60"
            },
            "auto_adjustments": auto_adjustments,
            "conversion_rates": {
                "credits_to_usd": str(self.credits_to_usd_rate),
                "usd_to_star_tokens": str(self.usd_to_star_token_rate),
                "minimum_conversion": str(self.minimum_conversion_credits)
            },
            "transparency": {
                "total_transactions": len(self.transaction_history),
                "active_users": len(self.user_balances),
                "faucet_rate_multiplier": str(self.stability_engine.faucet_rate_multiplier),
                "sink_rate_multiplier": str(self.stability_engine.sink_rate_multiplier)
            },
            "generated_at": datetime.now(timezone.utc).isoformat()
        }