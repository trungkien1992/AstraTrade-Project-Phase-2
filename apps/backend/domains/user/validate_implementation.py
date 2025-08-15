#!/usr/bin/env python3
"""
User Domain Implementation Validator

Validate that the User Domain implementation follows DDD patterns
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
            Email, Username, WalletAddress, UserPreference, SecurityCredentials,
            UserProfile, SessionInfo, UserPermissions, UserStatus, VerificationTier,
            PreferenceType
        )
        
        # Test Email
        email = Email("test@example.com")
        assert email.domain == "example.com"
        assert email.local_part == "test"
        
        # Test Username
        username = Username("validuser123")
        assert str(username) == "validuser123"
        
        # Test WalletAddress
        wallet = WalletAddress("0x1234567890abcdef", "starknet")
        assert wallet.network == "starknet"
        
        # Test UserPreference
        pref = UserPreference(PreferenceType.NOTIFICATION, "email_alerts", "enabled")
        assert pref.key == "email_alerts"
        
        # Test SecurityCredentials
        creds = SecurityCredentials(
            hashed_password="a" * 64,
            two_factor_secret="secret123"
        )
        assert creds.has_two_factor_enabled() is True
        
        # Test UserProfile
        profile = UserProfile(display_name="John Doe", trading_experience_level="advanced")
        assert profile.display_name == "John Doe"
        
        # Test SessionInfo
        now = datetime.now(timezone.utc)
        session_info = SessionInfo(
            session_id="a" * 32,
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0",
            created_at=now,
            expires_at=now + timedelta(hours=24)
        )
        assert not session_info.is_expired()
        
        # Test UserPermissions
        perms = UserPermissions(role="admin", is_admin=True)
        assert perms.has_permission("any_permission") is True
        
        print("✅ Value Objects validation passed")
        return True
        
    except Exception as e:
        print(f"❌ Value Objects validation failed: {e}")
        return False


def validate_entities():
    """Validate entities work correctly"""
    print("🔍 Validating Entities...")
    
    try:
        from entities import User, UserSession, UserActivity, ActivityType
        from value_objects import Username, SecurityCredentials, Email, WalletAddress, UserProfile, SessionInfo
        
        # Test User Entity
        username = Username("testuser")
        credentials = SecurityCredentials(hashed_password="a" * 64)
        email = Email("test@example.com")
        
        user = User(username, credentials, email)
        user.set_user_id(123)
        
        # Test user operations
        assert user.user_id == 123
        assert user.username == username
        assert user.is_active()
        
        # Test password change
        user.change_password("new_hash" + "a" * 56)
        events = user.get_domain_events()
        assert len(events) == 1
        assert events[0].event_type == "password_changed"
        
        # Test wallet connection
        wallet = WalletAddress("0x1234567890abcdef", "starknet")
        user.connect_wallet(wallet)
        assert user.wallet_address == wallet
        
        # Test profile update
        new_profile = UserProfile(display_name="John Doe", bio="Expert trader")
        user.update_profile(new_profile)
        assert user.profile.display_name == "John Doe"
        
        # Test login recording
        session_info = user.record_login("192.168.1.1", "Mozilla/5.0")
        assert user.login_count == 1
        assert session_info.ip_address == "192.168.1.1"
        
        # Test UserSession Entity
        session = UserSession("session123", 123, session_info)
        assert session.is_active
        assert not session.is_expired()
        
        # Test activity recording
        session.record_activity(ActivityType.TRADE_EXECUTED)
        assert len(session.activities) == 1
        
        # Test session termination
        session.terminate("user_logout")
        assert not session.is_active
        
        # Test UserActivity Entity
        today = datetime.now(timezone.utc)
        activity = UserActivity(user_id=123, date=today)
        
        activity.record_login("192.168.1.1")
        assert activity.login_count == 1
        assert activity.activity_score > Decimal('0')
        
        activity.record_trade()
        assert activity.trade_count == 1
        
        engagement = activity.get_engagement_level()
        assert engagement in ["inactive", "low", "medium", "high"]
        
        print("✅ Entities validation passed")
        return True
        
    except Exception as e:
        print(f"❌ Entities validation failed: {e}")
        return False


def validate_business_rules():
    """Validate key business rules"""
    print("🔍 Validating Business Rules...")
    
    try:
        from entities import User
        from value_objects import Username, SecurityCredentials, VerificationTier
        
        # Test user creation and ID immutability
        username = Username("testuser")
        credentials = SecurityCredentials(hashed_password="a" * 64)
        user = User(username, credentials)
        
        user.set_user_id(123)
        try:
            user.set_user_id(456)  # Should fail
            assert False, "Should not allow changing user ID"
        except ValueError:
            pass  # Expected
        
        # Test verification tier upgrade affects permissions
        assert not user.can_real_trade()
        
        user.verify_tier(VerificationTier.IDENTITY_VERIFIED)
        assert user.can_real_trade()
        
        # Test account suspension affects permissions
        user.suspend_account("Test suspension")
        assert not user.is_active()
        assert not user.can_real_trade()
        
        # Test reactivation
        user.reactivate_account()
        assert user.is_active()
        assert user.can_real_trade()
        
        # Test security score calculation
        score = user.get_security_score()
        assert 0 <= score <= 100
        
        print("✅ Business Rules validation passed")
        return True
        
    except Exception as e:
        print(f"❌ Business Rules validation failed: {e}")
        return False


def validate_domain_events():
    """Validate domain events are properly emitted"""
    print("🔍 Validating Domain Events...")
    
    try:
        from entities import User
        from value_objects import Username, SecurityCredentials, Email
        
        username = Username("testuser")
        credentials = SecurityCredentials(hashed_password="a" * 64)
        email = Email("test@example.com")
        user = User(username, credentials, email)
        user.set_user_id(123)
        
        # Perform operations that should emit events
        user.record_login("192.168.1.1", "Mozilla/5.0")
        user.change_password("new_hash" + "a" * 56)
        user.suspend_account("Test")
        user.reactivate_account()
        
        # Get all events
        events = user.get_domain_events()
        
        # Should have events for: login, password_change, suspension, reactivation
        assert len(events) >= 4
        
        event_types = [event.event_type for event in events]
        assert "user_logged_in" in event_types
        assert "password_changed" in event_types
        assert "account_suspended" in event_types
        assert "account_reactivated" in event_types
        
        # Events should be cleared after retrieval
        events2 = user.get_domain_events()
        assert len(events2) == 0
        
        print("✅ Domain Events validation passed")
        return True
        
    except Exception as e:
        print(f"❌ Domain Events validation failed: {e}")
        return False


def main():
    """Run all validations"""
    print("🚀 User Domain Implementation Validation")
    print("=" * 50)
    
    validations = [
        validate_value_objects,
        validate_entities,
        validate_business_rules,
        validate_domain_events
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
        print("User Domain implementation follows DDD patterns correctly.")
        print("Ready for integration with repository and infrastructure layers.")
    else:
        print(f"\n⚠️  {total-passed} validations failed.")
        print("Review implementation before proceeding.")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)