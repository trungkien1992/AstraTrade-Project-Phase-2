#!/usr/bin/env python3
"""
Financial Domain Validation Runner

Comprehensive validation of Financial Domain implementation
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


def test_money_operations():
    """Test Money value object operations"""
    print("  Testing Money operations...")
    
    # Basic creation
    money = vo.Money(Decimal('100.50'), vo.Currency.USD)
    assert money.amount == Decimal('100.50')
    
    # Addition
    money2 = vo.Money(Decimal('50'), vo.Currency.USD)
    sum_money = money.add(money2)
    assert sum_money.amount == Decimal('150.50')
    
    # Multiplication
    result = money.multiply(Decimal('2'))
    assert result.amount == Decimal('201.00')
    
    print("    ✅ Money operations work correctly")


def test_payment_method():
    """Test PaymentMethod value object"""
    print("  Testing PaymentMethod...")
    
    payment_method = vo.PaymentMethod(
        method_type=vo.PaymentMethodType.CREDIT_CARD,
        identifier="1234",
        display_name="Visa ending in 1234"
    )
    
    assert payment_method.is_card()
    assert not payment_method.is_crypto()
    assert not payment_method.is_expired()
    
    print("    ✅ PaymentMethod works correctly")


def test_subscription_tier():
    """Test SubscriptionTier value object"""
    print("  Testing SubscriptionTier...")
    
    tier = vo.SubscriptionTier(
        tier_type=vo.SubscriptionTierType.PRO,
        name="Pro Plan",
        description="Professional features",
        monthly_price=vo.Money(Decimal('29.99'), vo.Currency.USD),
        yearly_price=vo.Money(Decimal('299.99'), vo.Currency.USD),
        features=frozenset(["unlimited_trades"]),
        real_trading_enabled=True
    )
    
    assert tier.allows_real_trading()
    savings = tier.get_savings_percentage()
    assert savings > Decimal('0')
    
    print("    ✅ SubscriptionTier works correctly")


def test_account_entity():
    """Test Account entity"""
    print("  Testing Account entity...")
    
    account = ent.Account(
        user_id=123,
        balance=vo.Money(Decimal('1000'), vo.Currency.USD)
    )
    account.set_account_id("acc_123456")
    
    # Test basic operations
    assert account.is_active()
    assert account.balance.amount == Decimal('1000')
    
    # Test adding funds
    account.add_funds(vo.Money(Decimal('500'), vo.Currency.USD), "txn_001", "deposit")
    assert account.balance.amount == Decimal('1500')
    
    # Test domain events
    events = account.get_domain_events()
    assert len(events) > 0
    
    print("    ✅ Account entity works correctly")


def test_subscription_entity():
    """Test Subscription entity"""
    print("  Testing Subscription entity...")
    
    tier = vo.SubscriptionTier(
        tier_type=vo.SubscriptionTierType.PRO,
        name="Pro Plan",
        description="Pro features",
        monthly_price=vo.Money(Decimal('29.99'), vo.Currency.USD),
        yearly_price=vo.Money(Decimal('299.99'), vo.Currency.USD),
        features=frozenset(["unlimited_trades"]),
        real_trading_enabled=True
    )
    
    subscription = ent.Subscription(
        user_id=123,
        account_id="acc_123456",
        current_tier=tier,
        billing_cycle=vo.BillingCycle.MONTHLY
    )
    subscription.set_subscription_id("sub_123456")
    
    assert subscription.is_active()
    assert subscription.allows_real_trading()
    
    print("    ✅ Subscription entity works correctly")


def test_payment_entity():
    """Test Payment entity"""
    print("  Testing Payment entity...")
    
    payment_method = vo.PaymentMethod(
        method_type=vo.PaymentMethodType.CREDIT_CARD,
        identifier="1234",
        display_name="Test Card"
    )
    
    payment = ent.Payment(
        account_id="acc_123456",
        amount=vo.Money(Decimal('29.99'), vo.Currency.USD),
        payment_method=payment_method
    )
    payment.set_payment_id("pay_123456")
    
    assert payment.is_pending()
    
    # Test payment lifecycle
    payment.process_payment("processor_txn_123")
    payment.complete_payment()
    assert payment.is_successful()
    
    print("    ✅ Payment entity works correctly")


def test_business_rules():
    """Test key business rules"""
    print("  Testing business rules...")
    
    # Test account balance cannot go negative
    account = ent.Account(user_id=123, balance=vo.Money(Decimal('100'), vo.Currency.USD))
    account.set_account_id("acc_test")
    
    try:
        account.withdraw_funds(vo.Money(Decimal('200'), vo.Currency.USD), "txn_001")
        assert False, "Should not allow overdraft"
    except ValueError:
        pass  # Expected
    
    # Test currency consistency
    try:
        account.add_funds(vo.Money(Decimal('100'), vo.Currency.EUR), "txn_002")
        assert False, "Should not allow different currency"
    except ValueError:
        pass  # Expected
    
    print("    ✅ Business rules enforced correctly")


def test_financial_calculations():
    """Test financial calculation precision"""
    print("  Testing financial calculations...")
    
    # Test precise decimal arithmetic
    money1 = vo.Money(Decimal('100.33'), vo.Currency.USD)
    money2 = vo.Money(Decimal('200.67'), vo.Currency.USD)
    sum_money = money1.add(money2)
    assert sum_money.amount == Decimal('301.00')
    
    # Test fee calculations
    processor = vo.PaymentProcessor(
        processor_name="Stripe",
        api_key_reference="stripe_key",
        supported_methods=frozenset([vo.PaymentMethodType.CREDIT_CARD]),
        supported_currencies=frozenset([vo.Currency.USD]),
        fee_percentage=Decimal('0.029'),  # 2.9%
        fixed_fee=vo.Money(Decimal('0.30'), vo.Currency.USD)
    )
    
    amount = vo.Money(Decimal('100'), vo.Currency.USD)
    fee = processor.calculate_fee(amount)
    assert fee.amount == Decimal('3.20')  # $2.90 + $0.30
    
    print("    ✅ Financial calculations accurate")


def main():
    """Run all Financial Domain tests"""
    print("🚀 Financial Domain Validation")
    print("=" * 50)
    
    tests = [
        test_money_operations,
        test_payment_method,
        test_subscription_tier,
        test_account_entity,
        test_subscription_entity,
        test_payment_entity,
        test_business_rules,
        test_financial_calculations
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
        print("Financial Domain implementation is working correctly.")
        print("\n💰 Validated capabilities:")
        print("  • Precise decimal money calculations")
        print("  • Payment method management")
        print("  • Subscription tier system")
        print("  • Account balance management")
        print("  • Payment processing lifecycle")
        print("  • Business rule enforcement")
        print("  • Financial fee calculations")
        print("  • Domain event emission")
        
        return True
    else:
        print(f"\n⚠️  {total-passed} tests failed.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)