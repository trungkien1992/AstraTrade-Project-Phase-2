"""
Financial Domain Value Objects

Value objects for the Financial Domain as defined in ADR-001.
These are immutable objects that describe characteristics of financial concepts.
"""

from datetime import datetime, timezone, timedelta
from decimal import Decimal, ROUND_HALF_UP
from enum import Enum
from typing import Optional, Dict, Any
from dataclasses import dataclass
import re


class Currency(Enum):
    """Supported currencies"""
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    ETH = "ETH"
    BTC = "BTC"
    STRK = "STRK"


class PaymentStatus(Enum):
    """Payment processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class PaymentMethodType(Enum):
    """Types of payment methods"""
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    BANK_TRANSFER = "bank_transfer"
    CRYPTOCURRENCY = "cryptocurrency"
    APPLE_PAY = "apple_pay"
    GOOGLE_PAY = "google_pay"
    PAYPAL = "paypal"


class SubscriptionTierType(Enum):
    """Subscription tier levels"""
    FREE = "free"
    BASIC = "basic"
    PRO = "pro"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"


class BillingCycle(Enum):
    """Billing cycle periods"""
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    LIFETIME = "lifetime"


class RevenueStream(Enum):
    """The 4 revenue streams as defined in roadmap"""
    SUBSCRIPTIONS = "subscriptions"
    TRANSACTION_FEES = "transaction_fees"
    NFT_MARKETPLACE = "nft_marketplace"
    PREMIUM_FEATURES = "premium_features"


@dataclass(frozen=True)
class Money:
    """Value object for monetary amounts with precise decimal arithmetic"""
    amount: Decimal
    currency: Currency
    
    def __post_init__(self):
        if not isinstance(self.amount, Decimal):
            object.__setattr__(self, 'amount', Decimal(str(self.amount)))
        
        if self.amount < 0:
            raise ValueError("Money amount cannot be negative")
        
        # Round to appropriate precision based on currency
        precision = 8 if self.currency in [Currency.BTC, Currency.ETH, Currency.STRK] else 2
        rounded_amount = self.amount.quantize(Decimal('0.' + '0' * precision), rounding=ROUND_HALF_UP)
        object.__setattr__(self, 'amount', rounded_amount)
    
    def add(self, other: 'Money') -> 'Money':
        """Add two money amounts (must be same currency)"""
        if self.currency != other.currency:
            raise ValueError(f"Cannot add {self.currency} and {other.currency}")
        return Money(self.amount + other.amount, self.currency)
    
    def subtract(self, other: 'Money') -> 'Money':
        """Subtract two money amounts (must be same currency)"""
        if self.currency != other.currency:
            raise ValueError(f"Cannot subtract {other.currency} from {self.currency}")
        if self.amount < other.amount:
            raise ValueError("Cannot subtract to negative amount")
        return Money(self.amount - other.amount, self.currency)
    
    def multiply(self, factor: Decimal) -> 'Money':
        """Multiply money by a factor"""
        return Money(self.amount * factor, self.currency)
    
    def is_zero(self) -> bool:
        """Check if amount is zero"""
        return self.amount == Decimal('0')
    
    def __str__(self) -> str:
        if self.currency in [Currency.BTC, Currency.ETH, Currency.STRK]:
            return f"{self.amount:.8f} {self.currency.value}"
        return f"{self.amount:.2f} {self.currency.value}"


@dataclass(frozen=True)
class PaymentMethod:
    """Value object for payment method information"""
    method_type: PaymentMethodType
    identifier: str  # Last 4 digits for cards, wallet address for crypto
    display_name: str
    is_primary: bool = False
    expiry_date: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if not self.identifier or len(self.identifier.strip()) == 0:
            raise ValueError("Payment method identifier cannot be empty")
        if not self.display_name or len(self.display_name.strip()) == 0:
            raise ValueError("Payment method display name cannot be empty")
        
        # Validate identifier format based on type
        if self.method_type in [PaymentMethodType.CREDIT_CARD, PaymentMethodType.DEBIT_CARD]:
            if not re.match(r'^\d{4}$', self.identifier):
                raise ValueError("Card identifier must be 4 digits")
        elif self.method_type == PaymentMethodType.CRYPTOCURRENCY:
            if self.identifier.startswith('0x') and len(self.identifier) < 10:
                raise ValueError("Invalid cryptocurrency address")
    
    def is_expired(self) -> bool:
        """Check if payment method has expired"""
        if not self.expiry_date:
            return False
        return datetime.now() > self.expiry_date
    
    def is_card(self) -> bool:
        """Check if payment method is a card"""
        return self.method_type in [PaymentMethodType.CREDIT_CARD, PaymentMethodType.DEBIT_CARD]
    
    def is_crypto(self) -> bool:
        """Check if payment method is cryptocurrency"""
        return self.method_type == PaymentMethodType.CRYPTOCURRENCY


@dataclass(frozen=True)
class SubscriptionTier:
    """Value object for subscription tier configuration"""
    tier_type: SubscriptionTierType
    name: str
    description: str
    monthly_price: Money
    yearly_price: Money
    features: frozenset
    max_trades_per_day: Optional[int] = None
    real_trading_enabled: bool = False
    priority_support: bool = False
    advanced_analytics: bool = False
    
    def __post_init__(self):
        if not self.name or len(self.name.strip()) == 0:
            raise ValueError("Subscription tier name cannot be empty")
        if not self.description or len(self.description.strip()) == 0:
            raise ValueError("Subscription tier description cannot be empty")
        
        # Validate pricing structure
        if self.tier_type == SubscriptionTierType.FREE:
            if not self.monthly_price.is_zero() or not self.yearly_price.is_zero():
                raise ValueError("Free tier must have zero pricing")
        else:
            if self.monthly_price.is_zero() and self.yearly_price.is_zero():
                raise ValueError("Paid tiers must have non-zero pricing")
        
        # Validate yearly discount
        if not self.yearly_price.is_zero() and not self.monthly_price.is_zero():
            yearly_equivalent = self.monthly_price.multiply(Decimal('12'))
            if self.yearly_price.amount >= yearly_equivalent.amount:
                raise ValueError("Yearly price should be less than 12x monthly price")
    
    def get_savings_percentage(self) -> Decimal:
        """Calculate savings percentage for yearly vs monthly"""
        if self.monthly_price.is_zero() or self.yearly_price.is_zero():
            return Decimal('0')
        
        yearly_equivalent = self.monthly_price.multiply(Decimal('12'))
        savings = yearly_equivalent.subtract(self.yearly_price)
        return (savings.amount / yearly_equivalent.amount) * Decimal('100')
    
    def allows_real_trading(self) -> bool:
        """Check if tier allows real money trading"""
        return self.real_trading_enabled
    
    def get_trade_limit(self) -> Optional[int]:
        """Get daily trade limit for this tier"""
        return self.max_trades_per_day


@dataclass(frozen=True)
class TransactionRecord:
    """Value object for transaction details"""
    transaction_id: str
    amount: Money
    transaction_type: str  # subscription_payment, nft_purchase, trading_fee, etc.
    revenue_stream: RevenueStream
    reference_id: Optional[str] = None  # Reference to related entity (subscription_id, nft_id, etc.)
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if not self.transaction_id or len(self.transaction_id) < 6:
            raise ValueError("Transaction ID must be at least 6 characters")
        if not self.transaction_type or len(self.transaction_type.strip()) == 0:
            raise ValueError("Transaction type cannot be empty")
    
    def is_subscription_revenue(self) -> bool:
        """Check if transaction is subscription revenue"""
        return self.revenue_stream == RevenueStream.SUBSCRIPTIONS
    
    def is_trading_fee(self) -> bool:
        """Check if transaction is trading fee"""
        return self.revenue_stream == RevenueStream.TRANSACTION_FEES


@dataclass(frozen=True)
class BillingPeriod:
    """Value object for billing period configuration"""
    cycle: BillingCycle
    start_date: datetime
    end_date: datetime
    amount_due: Money
    
    def __post_init__(self):
        if self.start_date >= self.end_date:
            raise ValueError("Billing period start date must be before end date")
        if self.amount_due.amount < 0:
            raise ValueError("Billing amount cannot be negative")
        
        # Validate period length matches cycle
        period_days = (self.end_date - self.start_date).days
        expected_days = {
            BillingCycle.MONTHLY: 30,
            BillingCycle.QUARTERLY: 90,
            BillingCycle.YEARLY: 365,
            BillingCycle.LIFETIME: 36500  # 100 years as "lifetime"
        }
        
        expected = expected_days.get(self.cycle, 30)
        if abs(period_days - expected) > 5:  # Allow 5-day tolerance
            raise ValueError(f"Period length {period_days} days doesn't match {self.cycle.value} cycle")
    
    def is_current(self) -> bool:
        """Check if billing period is currently active"""
        now = datetime.now(timezone.utc)
        start = self.start_date
        end = self.end_date
        
        # Ensure all datetimes are timezone-aware
        if start.tzinfo is None:
            start = start.replace(tzinfo=timezone.utc)
        if end.tzinfo is None:
            end = end.replace(tzinfo=timezone.utc)
            
        return start <= now <= end
    
    def days_remaining(self) -> int:
        """Get days remaining in billing period"""
        if not self.is_current():
            return 0
        
        now = datetime.now(timezone.utc)
        end = self.end_date
        if end.tzinfo is None:
            end = end.replace(tzinfo=timezone.utc)
            
        return (end - now).days
    
    def progress_percentage(self) -> Decimal:
        """Get progress through billing period as percentage"""
        if not self.is_current():
            return Decimal('100')
        
        now = datetime.now(timezone.utc)
        start = self.start_date
        end = self.end_date
        
        # Ensure all datetimes are timezone-aware
        if start.tzinfo is None:
            start = start.replace(tzinfo=timezone.utc)
        if end.tzinfo is None:
            end = end.replace(tzinfo=timezone.utc)
        
        total_days = (end - start).days
        elapsed_days = (now - start).days
        return (Decimal(elapsed_days) / Decimal(total_days)) * Decimal('100')


@dataclass(frozen=True)
class PaymentProcessor:
    """Value object for payment processor configuration"""
    processor_name: str
    api_key_reference: str  # Reference to secure key storage
    supported_methods: frozenset
    supported_currencies: frozenset
    fee_percentage: Decimal
    fixed_fee: Money
    is_production: bool = False
    
    def __post_init__(self):
        if not self.processor_name or len(self.processor_name.strip()) == 0:
            raise ValueError("Payment processor name cannot be empty")
        if self.fee_percentage < 0 or self.fee_percentage > Decimal('0.1'):  # Max 10%
            raise ValueError("Fee percentage must be between 0 and 10%")
        if len(self.supported_methods) == 0:
            raise ValueError("Payment processor must support at least one payment method")
    
    def calculate_fee(self, amount: Money) -> Money:
        """Calculate processing fee for given amount"""
        if amount.currency not in self.supported_currencies:
            raise ValueError(f"Currency {amount.currency} not supported by {self.processor_name}")
        
        percentage_fee = amount.multiply(self.fee_percentage)
        total_fee = percentage_fee.add(self.fixed_fee)
        return total_fee
    
    def supports_method(self, method_type: PaymentMethodType) -> bool:
        """Check if processor supports payment method"""
        return method_type in self.supported_methods
    
    def supports_currency(self, currency: Currency) -> bool:
        """Check if processor supports currency"""
        return currency in self.supported_currencies


@dataclass(frozen=True)
class ComplianceRecord:
    """Value object for compliance and audit information"""
    record_id: str
    compliance_type: str  # KYC, AML, tax_reporting, etc.
    status: str
    created_at: datetime
    details: Dict[str, Any]
    expiry_date: Optional[datetime] = None
    
    def __post_init__(self):
        if not self.record_id or len(self.record_id) < 6:
            raise ValueError("Compliance record ID must be at least 6 characters")
        if not self.compliance_type or len(self.compliance_type.strip()) == 0:
            raise ValueError("Compliance type cannot be empty")
        if not self.status or len(self.status.strip()) == 0:
            raise ValueError("Compliance status cannot be empty")
    
    def is_expired(self) -> bool:
        """Check if compliance record has expired"""
        if not self.expiry_date:
            return False
        
        now = datetime.now(timezone.utc)
        expiry = self.expiry_date
        if expiry.tzinfo is None:
            expiry = expiry.replace(tzinfo=timezone.utc)
            
        return now > expiry
    
    def is_valid(self) -> bool:
        """Check if compliance record is valid"""
        return self.status.lower() == "approved" and not self.is_expired()
    
    def days_until_expiry(self) -> Optional[int]:
        """Get days until compliance record expires"""
        if not self.expiry_date:
            return None
        
        now = datetime.now(timezone.utc)
        expiry = self.expiry_date
        if expiry.tzinfo is None:
            expiry = expiry.replace(tzinfo=timezone.utc)
            
        return (expiry - now).days