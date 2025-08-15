"""
Tests for Financial Domain Value Objects

Test suite covering all value objects in the Financial Domain
including Money, PaymentMethod, SubscriptionTier, and others.
"""

import pytest
from datetime import datetime, timedelta
from decimal import Decimal

from ..value_objects import (
    Money, PaymentMethod, SubscriptionTier, TransactionRecord, BillingPeriod,
    PaymentProcessor, ComplianceRecord, Currency, PaymentMethodType,
    SubscriptionTierType, BillingCycle, RevenueStream, PaymentStatus
)


class TestMoney:
    """Test Money value object"""
    
    def test_money_creation_with_decimal(self):
        money = Money(Decimal('100.50'), Currency.USD)
        assert money.amount == Decimal('100.50')
        assert money.currency == Currency.USD
    
    def test_money_creation_with_float_converts_to_decimal(self):
        money = Money(100.50, Currency.USD)
        assert money.amount == Decimal('100.50')
    
    def test_money_negative_amount_raises_error(self):
        with pytest.raises(ValueError, match="Money amount cannot be negative"):
            Money(Decimal('-10'), Currency.USD)
    
    def test_money_precision_rounding_fiat(self):
        money = Money(Decimal('100.999'), Currency.USD)
        assert money.amount == Decimal('101.00')  # Rounded to 2 decimal places
    
    def test_money_precision_rounding_crypto(self):
        money = Money(Decimal('1.123456789'), Currency.BTC)
        assert money.amount == Decimal('1.12345679')  # Rounded to 8 decimal places
    
    def test_money_addition_same_currency(self):
        money1 = Money(Decimal('100'), Currency.USD)
        money2 = Money(Decimal('50'), Currency.USD)
        result = money1.add(money2)
        assert result.amount == Decimal('150')
        assert result.currency == Currency.USD
    
    def test_money_addition_different_currency_raises_error(self):
        money1 = Money(Decimal('100'), Currency.USD)
        money2 = Money(Decimal('50'), Currency.EUR)
        with pytest.raises(ValueError, match="Cannot add USD and EUR"):
            money1.add(money2)
    
    def test_money_subtraction_same_currency(self):
        money1 = Money(Decimal('100'), Currency.USD)
        money2 = Money(Decimal('30'), Currency.USD)
        result = money1.subtract(money2)
        assert result.amount == Decimal('70')
    
    def test_money_subtraction_to_negative_raises_error(self):
        money1 = Money(Decimal('50'), Currency.USD)
        money2 = Money(Decimal('100'), Currency.USD)
        with pytest.raises(ValueError, match="Cannot subtract to negative amount"):
            money1.subtract(money2)
    
    def test_money_multiplication(self):
        money = Money(Decimal('100'), Currency.USD)
        result = money.multiply(Decimal('1.5'))
        assert result.amount == Decimal('150.00')
    
    def test_money_is_zero(self):
        zero_money = Money(Decimal('0'), Currency.USD)
        non_zero_money = Money(Decimal('10'), Currency.USD)
        assert zero_money.is_zero()
        assert not non_zero_money.is_zero()
    
    def test_money_string_representation_fiat(self):
        money = Money(Decimal('100.50'), Currency.USD)
        assert str(money) == "100.50 USD"
    
    def test_money_string_representation_crypto(self):
        money = Money(Decimal('0.12345678'), Currency.BTC)
        assert str(money) == "0.12345678 BTC"


class TestPaymentMethod:
    """Test PaymentMethod value object"""
    
    def test_payment_method_creation_valid(self):
        expiry = datetime.now() + timedelta(days=365)
        method = PaymentMethod(
            method_type=PaymentMethodType.CREDIT_CARD,
            identifier="1234",
            display_name="Visa ending in 1234",
            expiry_date=expiry
        )
        assert method.method_type == PaymentMethodType.CREDIT_CARD
        assert method.identifier == "1234"
        assert not method.is_expired()
    
    def test_payment_method_empty_identifier_raises_error(self):
        with pytest.raises(ValueError, match="Payment method identifier cannot be empty"):
            PaymentMethod(
                method_type=PaymentMethodType.CREDIT_CARD,
                identifier="",
                display_name="Test Card"
            )
    
    def test_payment_method_invalid_card_identifier_raises_error(self):
        with pytest.raises(ValueError, match="Card identifier must be 4 digits"):
            PaymentMethod(
                method_type=PaymentMethodType.CREDIT_CARD,
                identifier="123",  # Only 3 digits
                display_name="Test Card"
            )
    
    def test_payment_method_crypto_address_validation(self):
        method = PaymentMethod(
            method_type=PaymentMethodType.CRYPTOCURRENCY,
            identifier="0x1234567890abcdef",
            display_name="ETH Wallet"
        )
        assert method.is_crypto()
        assert not method.is_card()
    
    def test_payment_method_is_expired(self):
        expired_method = PaymentMethod(
            method_type=PaymentMethodType.CREDIT_CARD,
            identifier="1234",
            display_name="Expired Card",
            expiry_date=datetime.now() - timedelta(days=1)
        )
        assert expired_method.is_expired()
    
    def test_payment_method_no_expiry_not_expired(self):
        method = PaymentMethod(
            method_type=PaymentMethodType.BANK_TRANSFER,
            identifier="account123",
            display_name="Bank Account"
        )
        assert not method.is_expired()


class TestSubscriptionTier:
    """Test SubscriptionTier value object"""
    
    def test_subscription_tier_creation_valid(self):
        tier = SubscriptionTier(
            tier_type=SubscriptionTierType.PRO,
            name="Pro Plan",
            description="Professional trading features",
            monthly_price=Money(Decimal('29.99'), Currency.USD),
            yearly_price=Money(Decimal('299.99'), Currency.USD),
            features=frozenset(["unlimited_trades", "advanced_analytics"]),
            real_trading_enabled=True
        )
        assert tier.tier_type == SubscriptionTierType.PRO
        assert tier.allows_real_trading()
        assert tier.get_savings_percentage() > Decimal('0')
    
    def test_free_tier_zero_pricing(self):
        free_tier = SubscriptionTier(
            tier_type=SubscriptionTierType.FREE,
            name="Free Plan",
            description="Basic features",
            monthly_price=Money(Decimal('0'), Currency.USD),
            yearly_price=Money(Decimal('0'), Currency.USD),
            features=frozenset(["limited_trades"])
        )
        assert free_tier.tier_type == SubscriptionTierType.FREE
        assert not free_tier.allows_real_trading()
    
    def test_free_tier_non_zero_pricing_raises_error(self):
        with pytest.raises(ValueError, match="Free tier must have zero pricing"):
            SubscriptionTier(
                tier_type=SubscriptionTierType.FREE,
                name="Free Plan",
                description="Basic features",
                monthly_price=Money(Decimal('10'), Currency.USD),  # Should be zero
                yearly_price=Money(Decimal('0'), Currency.USD),
                features=frozenset()
            )
    
    def test_paid_tier_zero_pricing_raises_error(self):
        with pytest.raises(ValueError, match="Paid tiers must have non-zero pricing"):
            SubscriptionTier(
                tier_type=SubscriptionTierType.PRO,
                name="Pro Plan",
                description="Pro features",
                monthly_price=Money(Decimal('0'), Currency.USD),  # Should be non-zero
                yearly_price=Money(Decimal('0'), Currency.USD),   # Should be non-zero
                features=frozenset()
            )
    
    def test_yearly_price_more_than_monthly_raises_error(self):
        with pytest.raises(ValueError, match="Yearly price should be less than 12x monthly price"):
            SubscriptionTier(
                tier_type=SubscriptionTierType.PRO,
                name="Pro Plan",
                description="Pro features",
                monthly_price=Money(Decimal('30'), Currency.USD),
                yearly_price=Money(Decimal('400'), Currency.USD),  # More than 12 * 30
                features=frozenset()
            )
    
    def test_savings_percentage_calculation(self):
        tier = SubscriptionTier(
            tier_type=SubscriptionTierType.PRO,
            name="Pro Plan",
            description="Pro features",
            monthly_price=Money(Decimal('30'), Currency.USD),
            yearly_price=Money(Decimal('300'), Currency.USD),  # 20% savings
            features=frozenset()
        )
        savings = tier.get_savings_percentage()
        assert abs(savings - Decimal('16.67')) < Decimal('0.1')  # Approximately 16.67% savings


class TestTransactionRecord:
    """Test TransactionRecord value object"""
    
    def test_transaction_record_creation_valid(self):
        transaction = TransactionRecord(
            transaction_id="txn_123456789",
            amount=Money(Decimal('100'), Currency.USD),
            transaction_type="subscription_payment",
            revenue_stream=RevenueStream.SUBSCRIPTIONS,
            reference_id="sub_123"
        )
        assert transaction.transaction_id == "txn_123456789"
        assert transaction.is_subscription_revenue()
        assert not transaction.is_trading_fee()
    
    def test_transaction_record_short_id_raises_error(self):
        with pytest.raises(ValueError, match="Transaction ID must be at least 6 characters"):
            TransactionRecord(
                transaction_id="123",  # Too short
                amount=Money(Decimal('100'), Currency.USD),
                transaction_type="payment",
                revenue_stream=RevenueStream.SUBSCRIPTIONS
            )
    
    def test_transaction_record_empty_type_raises_error(self):
        with pytest.raises(ValueError, match="Transaction type cannot be empty"):
            TransactionRecord(
                transaction_id="txn_123456",
                amount=Money(Decimal('100'), Currency.USD),
                transaction_type="",  # Empty
                revenue_stream=RevenueStream.SUBSCRIPTIONS
            )


class TestBillingPeriod:
    """Test BillingPeriod value object"""
    
    def test_billing_period_creation_valid(self):
        start = datetime.now()
        end = start + timedelta(days=30)
        amount = Money(Decimal('29.99'), Currency.USD)
        
        period = BillingPeriod(
            cycle=BillingCycle.MONTHLY,
            start_date=start,
            end_date=end,
            amount_due=amount
        )
        assert period.cycle == BillingCycle.MONTHLY
        assert period.is_current()
        assert period.days_remaining() > 0
    
    def test_billing_period_start_after_end_raises_error(self):
        start = datetime.now()
        end = start - timedelta(days=1)  # End before start
        
        with pytest.raises(ValueError, match="Billing period start date must be before end date"):
            BillingPeriod(
                cycle=BillingCycle.MONTHLY,
                start_date=start,
                end_date=end,
                amount_due=Money(Decimal('30'), Currency.USD)
            )
    
    def test_billing_period_negative_amount_raises_error(self):
        start = datetime.now()
        end = start + timedelta(days=30)
        
        with pytest.raises(ValueError, match="Billing amount cannot be negative"):
            BillingPeriod(
                cycle=BillingCycle.MONTHLY,
                start_date=start,
                end_date=end,
                amount_due=Money(Decimal('-10'), Currency.USD)  # This will fail at Money level first
            )
    
    def test_billing_period_wrong_duration_raises_error(self):
        start = datetime.now()
        end = start + timedelta(days=10)  # Too short for monthly
        
        with pytest.raises(ValueError, match="Period length .* days doesn't match monthly cycle"):
            BillingPeriod(
                cycle=BillingCycle.MONTHLY,
                start_date=start,
                end_date=end,
                amount_due=Money(Decimal('30'), Currency.USD)
            )
    
    def test_billing_period_progress_percentage(self):
        start = datetime.now() - timedelta(days=15)  # Started 15 days ago
        end = start + timedelta(days=30)  # 30-day period
        
        period = BillingPeriod(
            cycle=BillingCycle.MONTHLY,
            start_date=start,
            end_date=end,
            amount_due=Money(Decimal('30'), Currency.USD)
        )
        
        progress = period.progress_percentage()
        assert progress > Decimal('40')  # Should be around 50%
        assert progress < Decimal('60')


class TestPaymentProcessor:
    """Test PaymentProcessor value object"""
    
    def test_payment_processor_creation_valid(self):
        processor = PaymentProcessor(
            processor_name="Stripe",
            api_key_reference="stripe_key_ref",
            supported_methods=frozenset([PaymentMethodType.CREDIT_CARD, PaymentMethodType.DEBIT_CARD]),
            supported_currencies=frozenset([Currency.USD, Currency.EUR]),
            fee_percentage=Decimal('0.029'),  # 2.9%
            fixed_fee=Money(Decimal('0.30'), Currency.USD)
        )
        assert processor.processor_name == "Stripe"
        assert processor.supports_method(PaymentMethodType.CREDIT_CARD)
        assert not processor.supports_method(PaymentMethodType.CRYPTOCURRENCY)
    
    def test_payment_processor_empty_name_raises_error(self):
        with pytest.raises(ValueError, match="Payment processor name cannot be empty"):
            PaymentProcessor(
                processor_name="",  # Empty
                api_key_reference="key_ref",
                supported_methods=frozenset([PaymentMethodType.CREDIT_CARD]),
                supported_currencies=frozenset([Currency.USD]),
                fee_percentage=Decimal('0.029'),
                fixed_fee=Money(Decimal('0.30'), Currency.USD)
            )
    
    def test_payment_processor_high_fee_raises_error(self):
        with pytest.raises(ValueError, match="Fee percentage must be between 0 and 10%"):
            PaymentProcessor(
                processor_name="HighFee",
                api_key_reference="key_ref",
                supported_methods=frozenset([PaymentMethodType.CREDIT_CARD]),
                supported_currencies=frozenset([Currency.USD]),
                fee_percentage=Decimal('0.15'),  # 15% - too high
                fixed_fee=Money(Decimal('0.30'), Currency.USD)
            )
    
    def test_payment_processor_no_methods_raises_error(self):
        with pytest.raises(ValueError, match="Payment processor must support at least one payment method"):
            PaymentProcessor(
                processor_name="NoMethods",
                api_key_reference="key_ref",
                supported_methods=frozenset(),  # Empty
                supported_currencies=frozenset([Currency.USD]),
                fee_percentage=Decimal('0.029'),
                fixed_fee=Money(Decimal('0.30'), Currency.USD)
            )
    
    def test_payment_processor_calculate_fee(self):
        processor = PaymentProcessor(
            processor_name="Stripe",
            api_key_reference="stripe_key_ref",
            supported_methods=frozenset([PaymentMethodType.CREDIT_CARD]),
            supported_currencies=frozenset([Currency.USD]),
            fee_percentage=Decimal('0.029'),  # 2.9%
            fixed_fee=Money(Decimal('0.30'), Currency.USD)
        )
        
        amount = Money(Decimal('100'), Currency.USD)
        fee = processor.calculate_fee(amount)
        
        # Fee should be 2.9% + $0.30 = $2.90 + $0.30 = $3.20
        expected_fee = Money(Decimal('3.20'), Currency.USD)
        assert fee.amount == expected_fee.amount
    
    def test_payment_processor_unsupported_currency_raises_error(self):
        processor = PaymentProcessor(
            processor_name="USDOnly",
            api_key_reference="key_ref",
            supported_methods=frozenset([PaymentMethodType.CREDIT_CARD]),
            supported_currencies=frozenset([Currency.USD]),
            fee_percentage=Decimal('0.029'),
            fixed_fee=Money(Decimal('0.30'), Currency.USD)
        )
        
        amount = Money(Decimal('100'), Currency.EUR)  # Unsupported currency
        with pytest.raises(ValueError, match="Currency EUR not supported"):
            processor.calculate_fee(amount)


class TestComplianceRecord:
    """Test ComplianceRecord value object"""
    
    def test_compliance_record_creation_valid(self):
        record = ComplianceRecord(
            record_id="kyc_123456",
            compliance_type="KYC",
            status="approved",
            created_at=datetime.now(),
            details={"document_type": "passport", "verified": True},
            expiry_date=datetime.now() + timedelta(days=365)
        )
        assert record.record_id == "kyc_123456"
        assert record.is_valid()
        assert not record.is_expired()
    
    def test_compliance_record_short_id_raises_error(self):
        with pytest.raises(ValueError, match="Compliance record ID must be at least 6 characters"):
            ComplianceRecord(
                record_id="123",  # Too short
                compliance_type="KYC",
                status="approved",
                created_at=datetime.now(),
                details={}
            )
    
    def test_compliance_record_empty_type_raises_error(self):
        with pytest.raises(ValueError, match="Compliance type cannot be empty"):
            ComplianceRecord(
                record_id="kyc_123456",
                compliance_type="",  # Empty
                status="approved",
                created_at=datetime.now(),
                details={}
            )
    
    def test_compliance_record_expired(self):
        record = ComplianceRecord(
            record_id="kyc_123456",
            compliance_type="KYC",
            status="approved",
            created_at=datetime.now() - timedelta(days=400),
            details={},
            expiry_date=datetime.now() - timedelta(days=1)  # Expired yesterday
        )
        assert record.is_expired()
        assert not record.is_valid()  # Expired records are not valid
    
    def test_compliance_record_days_until_expiry(self):
        record = ComplianceRecord(
            record_id="kyc_123456",
            compliance_type="KYC",
            status="approved",
            created_at=datetime.now(),
            details={},
            expiry_date=datetime.now() + timedelta(days=30)
        )
        days_until_expiry = record.days_until_expiry()
        assert days_until_expiry is not None
        assert 29 <= days_until_expiry <= 30  # Should be around 30 days
    
    def test_compliance_record_no_expiry(self):
        record = ComplianceRecord(
            record_id="kyc_123456",
            compliance_type="KYC",
            status="approved",
            created_at=datetime.now(),
            details={}
            # No expiry_date
        )
        assert not record.is_expired()
        assert record.days_until_expiry() is None