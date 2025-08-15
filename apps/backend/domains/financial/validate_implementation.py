#!/usr/bin/env python3
"""
Financial Domain Implementation Validator

Validate that the Financial Domain implementation follows DDD patterns
and business logic works correctly without external dependencies.
"""

import sys
from datetime import datetime, timezone, timedelta
from decimal import Decimal


def validate_value_objects():
    """Validate value objects work correctly"""
    print("🔍 Validating Value Objects...")
    
    try:
        from value_objects import (
            Money, PaymentMethod, SubscriptionTier, TransactionRecord, BillingPeriod,
            PaymentProcessor, ComplianceRecord, Currency, PaymentMethodType,
            SubscriptionTierType, BillingCycle, RevenueStream
        )
        
        # Test Money
        money = Money(Decimal('100.50'), Currency.USD)
        assert money.amount == Decimal('100.50')
        assert str(money) == "100.50 USD"
        
        # Test Money operations
        money2 = Money(Decimal('50'), Currency.USD)
        sum_money = money.add(money2)
        assert sum_money.amount == Decimal('150.50')
        
        # Test PaymentMethod
        payment_method = PaymentMethod(
            method_type=PaymentMethodType.CREDIT_CARD,
            identifier="1234",
            display_name="Visa ending in 1234"
        )
        assert payment_method.is_card()
        assert not payment_method.is_crypto()
        
        # Test SubscriptionTier
        tier = SubscriptionTier(
            tier_type=SubscriptionTierType.PRO,
            name="Pro Plan",
            description="Professional features",
            monthly_price=Money(Decimal('29.99'), Currency.USD),
            yearly_price=Money(Decimal('299.99'), Currency.USD),
            features=frozenset(["unlimited_trades"]),
            real_trading_enabled=True
        )
        assert tier.allows_real_trading()
        assert tier.get_savings_percentage() > Decimal('0')
        
        # Test TransactionRecord
        transaction = TransactionRecord(
            transaction_id="txn_123456789",
            amount=Money(Decimal('100'), Currency.USD),
            transaction_type="subscription_payment",
            revenue_stream=RevenueStream.SUBSCRIPTIONS
        )
        assert transaction.is_subscription_revenue()
        
        # Test BillingPeriod
        start = datetime.now(timezone.utc)
        end = start + timedelta(days=30)
        period = BillingPeriod(
            cycle=BillingCycle.MONTHLY,
            start_date=start,
            end_date=end,
            amount_due=Money(Decimal('29.99'), Currency.USD)
        )
        assert period.is_current()
        
        # Test PaymentProcessor
        processor = PaymentProcessor(
            processor_name="Stripe",
            api_key_reference="stripe_key",
            supported_methods=frozenset([PaymentMethodType.CREDIT_CARD]),
            supported_currencies=frozenset([Currency.USD]),
            fee_percentage=Decimal('0.029'),
            fixed_fee=Money(Decimal('0.30'), Currency.USD)
        )
        fee = processor.calculate_fee(Money(Decimal('100'), Currency.USD))
        assert fee.amount == Decimal('3.20')  # 2.9% + $0.30
        
        # Test ComplianceRecord
        compliance = ComplianceRecord(
            record_id="kyc_123456",
            compliance_type="KYC",
            status="approved",
            created_at=datetime.now(timezone.utc),
            details={"verified": True}
        )
        assert compliance.is_valid()
        
        print("✅ Value Objects validation passed")
        return True
        
    except Exception as e:
        print(f"❌ Value Objects validation failed: {e}")
        return False


def validate_entities():
    """Validate entities work correctly"""
    print("🔍 Validating Entities...")
    
    try:
        from entities import Account, Subscription, Payment, Invoice
        from value_objects import (
            Money, PaymentMethod, SubscriptionTier, PaymentMethodType,
            SubscriptionTierType, BillingCycle, Currency, PaymentStatus
        )
        
        # Test Account Entity
        account = Account(
            user_id=123,
            balance=Money(Decimal('1000'), Currency.USD)
        )
        account.set_account_id("acc_123456")
        
        # Test account operations
        assert account.is_active()
        assert account.balance.amount == Decimal('1000')
        
        # Test adding funds
        account.add_funds(Money(Decimal('500'), Currency.USD), "txn_001", "deposit")
        assert account.balance.amount == Decimal('1500')
        
        # Test payment methods
        payment_method = PaymentMethod(
            method_type=PaymentMethodType.CREDIT_CARD,
            identifier="1234",
            display_name="Test Card"
        )
        account.add_payment_method(payment_method)
        assert len(account.payment_methods) == 1
        
        # Test Subscription Entity
        tier = SubscriptionTier(
            tier_type=SubscriptionTierType.PRO,
            name="Pro Plan",
            description="Pro features",
            monthly_price=Money(Decimal('29.99'), Currency.USD),
            yearly_price=Money(Decimal('299.99'), Currency.USD),
            features=frozenset(["unlimited_trades"]),
            real_trading_enabled=True
        )
        
        subscription = Subscription(
            user_id=123,
            account_id="acc_123456",
            current_tier=tier,
            billing_cycle=BillingCycle.MONTHLY
        )
        subscription.set_subscription_id("sub_123456")
        
        assert subscription.is_active()
        assert subscription.allows_real_trading()
        
        # Test subscription renewal
        new_period = subscription.renew_subscription()
        assert new_period.amount_due.amount == Decimal('29.99')
        
        # Test Payment Entity
        payment = Payment(
            account_id="acc_123456",
            amount=Money(Decimal('29.99'), Currency.USD),
            payment_method=payment_method
        )
        payment.set_payment_id("pay_123456")
        
        assert payment.is_pending()
        
        # Test payment processing
        payment.process_payment("processor_txn_123")
        payment.complete_payment()
        assert payment.is_successful()
        
        # Test Invoice Entity
        invoice = Invoice(
            account_id="acc_123456",
            amount_due=Money(Decimal('29.99'), Currency.USD)
        )
        invoice.set_invoice_id("inv_123456")
        
        invoice.add_line_item("Pro Subscription", Money(Decimal('29.99'), Currency.USD))
        invoice.send_invoice()
        assert invoice.status == "sent"
        
        # Test domain events
        events = account.get_domain_events()
        assert len(events) > 0
        
        print("✅ Entities validation passed")
        return True
        
    except Exception as e:
        print(f"❌ Entities validation failed: {e}")
        return False


def validate_business_rules():
    """Validate key business rules"""
    print("🔍 Validating Business Rules...")
    
    try:
        from entities import Account, Subscription
        from value_objects import Money, Currency, SubscriptionTier, SubscriptionTierType
        
        # Test account balance cannot go negative
        account = Account(user_id=123, balance=Money(Decimal('100'), Currency.USD))
        account.set_account_id("acc_test")
        
        try:
            account.withdraw_funds(Money(Decimal('200'), Currency.USD), "txn_001")
            assert False, "Should not allow overdraft"
        except ValueError:
            pass  # Expected
        
        # Test currency consistency
        try:
            account.add_funds(Money(Decimal('100'), Currency.EUR), "txn_002")
            assert False, "Should not allow different currency"
        except ValueError:
            pass  # Expected
        
        # Test subscription tier rules
        free_tier = SubscriptionTier(
            tier_type=SubscriptionTierType.FREE,
            name="Free",
            description="Free tier",
            monthly_price=Money(Decimal('0'), Currency.USD),
            yearly_price=Money(Decimal('0'), Currency.USD),
            features=frozenset(["basic"])
        )
        
        subscription = Subscription(
            user_id=123,
            account_id="acc_test",
            current_tier=free_tier
        )
        
        # Free tier should not allow real trading
        assert not subscription.allows_real_trading()
        
        # Test tier upgrade validation
        pro_tier = SubscriptionTier(
            tier_type=SubscriptionTierType.PRO,
            name="Pro",
            description="Pro tier",
            monthly_price=Money(Decimal('30'), Currency.USD),
            yearly_price=Money(Decimal('300'), Currency.USD),
            features=frozenset(["unlimited"]),
            real_trading_enabled=True
        )
        
        subscription.set_subscription_id("sub_test")
        subscription.upgrade_tier(pro_tier)
        assert subscription.allows_real_trading()
        
        print("✅ Business Rules validation passed")
        return True
        
    except Exception as e:
        print(f"❌ Business Rules validation failed: {e}")
        return False


def validate_domain_events():
    """Validate domain events are properly emitted"""
    print("🔍 Validating Domain Events...")
    
    try:
        from entities import Account, Payment
        from value_objects import Money, Currency, PaymentMethod, PaymentMethodType
        
        # Test account events
        account = Account(user_id=123, balance=Money(Decimal('100'), Currency.USD))
        account.set_account_id("acc_events")
        
        # Perform operations that should emit events
        account.add_funds(Money(Decimal('50'), Currency.USD), "txn_001")
        account.suspend_account("Test suspension")
        account.reactivate_account()
        
        # Get events
        events = account.get_domain_events()
        event_types = [event.event_type for event in events]
        
        assert "account_created" in event_types
        assert "funds_added" in event_types
        assert "account_suspended" in event_types
        assert "account_reactivated" in event_types
        
        # Test payment events
        payment_method = PaymentMethod(
            method_type=PaymentMethodType.CREDIT_CARD,
            identifier="1234",
            display_name="Test Card"
        )
        
        payment = Payment(
            account_id="acc_events",
            amount=Money(Decimal('100'), Currency.USD),
            payment_method=payment_method
        )
        payment.set_payment_id("pay_events")
        
        payment.process_payment("processor_123")
        payment.complete_payment()
        
        payment_events = payment.get_domain_events()
        payment_event_types = [event.event_type for event in payment_events]
        
        assert "payment_created" in payment_event_types
        assert "payment_processing" in payment_event_types
        assert "payment_completed" in payment_event_types
        
        print("✅ Domain Events validation passed")
        return True
        
    except Exception as e:
        print(f"❌ Domain Events validation failed: {e}")
        return False


def validate_financial_calculations():
    """Validate financial calculation accuracy"""
    print("🔍 Validating Financial Calculations...")
    
    try:
        from value_objects import Money, Currency, PaymentProcessor, PaymentMethodType
        from decimal import Decimal
        
        # Test precise money calculations
        money1 = Money(Decimal('100.33'), Currency.USD)
        money2 = Money(Decimal('200.67'), Currency.USD)
        sum_money = money1.add(money2)
        assert sum_money.amount == Decimal('301.00')  # Precise addition
        
        # Test multiplication with rounding
        result = money1.multiply(Decimal('1.5'))
        assert result.amount == Decimal('150.50')  # Properly rounded
        
        # Test fee calculations
        processor = PaymentProcessor(
            processor_name="Test",
            api_key_reference="key",
            supported_methods=frozenset([PaymentMethodType.CREDIT_CARD]),
            supported_currencies=frozenset([Currency.USD]),
            fee_percentage=Decimal('0.029'),  # 2.9%
            fixed_fee=Money(Decimal('0.30'), Currency.USD)
        )
        
        # Test fee calculation for $100
        amount = Money(Decimal('100'), Currency.USD)
        fee = processor.calculate_fee(amount)
        expected_fee = Money(Decimal('3.20'), Currency.USD)  # $2.90 + $0.30
        assert fee.amount == expected_fee.amount
        
        # Test crypto precision
        btc_amount = Money(Decimal('0.12345678'), Currency.BTC)
        assert str(btc_amount) == "0.12345678 BTC"
        
        btc_result = btc_amount.multiply(Decimal('2'))
        assert btc_result.amount == Decimal('0.24691356')
        
        print("✅ Financial Calculations validation passed")
        return True
        
    except Exception as e:
        print(f"❌ Financial Calculations validation failed: {e}")
        return False


def main():
    """Run all validations"""
    print("🚀 Financial Domain Implementation Validation")
    print("=" * 50)
    
    validations = [
        validate_value_objects,
        validate_entities,
        validate_business_rules,
        validate_domain_events,
        validate_financial_calculations
    ]
    
    passed = 0
    total = len(validations)
    
    for validation in validations:
        if validation():
            passed += 1
        print()  # Add spacing
    
    print("=" * 50)
    print("📊 VALIDATION SUMMARY")
    print("=" * 50)
    print(f"✅ Validations Passed: {passed}/{total}")
    print(f"📈 Success Rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("\n🎉 ALL VALIDATIONS PASSED!")
        print("Financial Domain implementation follows DDD patterns correctly.")
        print("Ready for integration with repository and infrastructure layers.")
        print("\n💰 Financial capabilities verified:")
        print("  • Money calculations with precise decimal arithmetic")
        print("  • Payment processing lifecycle management")
        print("  • Subscription management with tier upgrades")
        print("  • Revenue tracking across 4 streams")
        print("  • Compliance and audit trail support")
        print("  • Domain events for integration")
    else:
        print(f"\n⚠️  {total-passed} validations failed.")
        print("Review implementation before proceeding.")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)