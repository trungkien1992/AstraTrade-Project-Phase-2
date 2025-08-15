"""
Test suite for User Domain Entities

Comprehensive tests ensuring all entities maintain their business invariants
and domain logic works correctly under all conditions.
"""

import pytest
from datetime import datetime, timezone, timedelta
from decimal import Decimal

from ..entities import User, UserSession, UserActivity, ActivityType
from ..value_objects import (
    Email, Username, WalletAddress, UserPreference, SecurityCredentials,
    UserProfile, SessionInfo, UserPermissions, UserStatus, VerificationTier,
    PreferenceType
)


class TestUser:
    """Test User entity"""
    
    def test_user_creation(self):
        """Test creating a valid user"""
        username = Username("testuser")
        credentials = SecurityCredentials(hashed_password="a" * 64)
        email = Email("test@example.com")
        
        user = User(username, credentials, email)
        
        assert user.username == username
        assert user.email == email
        assert user.status == UserStatus.ACTIVE
        assert user.verification_tier == VerificationTier.UNVERIFIED
        assert user.user_id is None  # Not set initially
        assert user.login_count == 0
    
    def test_user_id_setting(self):
        """Test user ID can only be set once"""
        username = Username("testuser")
        credentials = SecurityCredentials(hashed_password="a" * 64)
        user = User(username, credentials)
        
        # First time should work
        user.set_user_id(123)
        assert user.user_id == 123
        
        # Second time should fail
        with pytest.raises(ValueError, match="User ID cannot be changed once set"):
            user.set_user_id(456)
    
    def test_invalid_user_id_raises_error(self):
        """Test that invalid user ID raises error"""
        username = Username("testuser")
        credentials = SecurityCredentials(hashed_password="a" * 64)
        user = User(username, credentials)
        
        with pytest.raises(ValueError, match="User ID must be positive"):
            user.set_user_id(0)
        
        with pytest.raises(ValueError, match="User ID must be positive"):
            user.set_user_id(-1)
    
    def test_password_change(self):
        """Test password change functionality"""
        username = Username("testuser")
        credentials = SecurityCredentials(hashed_password="old_hash" + "a" * 56)
        user = User(username, credentials)
        
        new_hash = "new_hash" + "a" * 56
        user.change_password(new_hash, "old_password")
        
        assert user._security_credentials.hashed_password == new_hash
        assert user._security_credentials.last_password_change is not None
        
        # Should have emitted domain event
        events = user.get_domain_events()
        assert len(events) == 1
        assert events[0].event_type == "password_changed"
    
    def test_invalid_password_hash_raises_error(self):
        """Test that invalid password hash raises error"""
        username = Username("testuser")
        credentials = SecurityCredentials(hashed_password="a" * 64)
        user = User(username, credentials)
        
        with pytest.raises(ValueError, match="Invalid password hash"):
            user.change_password("short", "old_password")
    
    def test_email_update(self):
        """Test email update functionality"""
        username = Username("testuser")
        credentials = SecurityCredentials(hashed_password="a" * 64)
        old_email = Email("old@example.com")
        user = User(username, credentials, old_email)
        
        new_email = Email("new@example.com")
        user.update_email(new_email)
        
        assert user.email == new_email
        assert user.verification_tier == VerificationTier.UNVERIFIED  # Reset on email change
        
        # Should have emitted domain event
        events = user.get_domain_events()
        assert len(events) == 1
        assert events[0].event_type == "email_updated"
    
    def test_wallet_connection(self):
        """Test wallet connection functionality"""
        username = Username("testuser")
        credentials = SecurityCredentials(hashed_password="a" * 64)
        user = User(username, credentials)
        
        wallet = WalletAddress("0x1234567890abcdef", "starknet")
        user.connect_wallet(wallet)
        
        assert user.wallet_address == wallet
        
        # Should have emitted domain event
        events = user.get_domain_events()
        assert len(events) == 1
        assert events[0].event_type == "wallet_connected"
    
    def test_profile_update(self):
        """Test profile update functionality"""
        username = Username("testuser")
        credentials = SecurityCredentials(hashed_password="a" * 64)
        user = User(username, credentials)
        
        new_profile = UserProfile(
            display_name="John Doe",
            bio="Trading expert",
            trading_experience_level="advanced"
        )
        user.update_profile(new_profile)
        
        assert user.profile == new_profile
        
        # Should have emitted domain event
        events = user.get_domain_events()
        assert len(events) == 1
        assert events[0].event_type == "profile_updated"
    
    def test_preference_management(self):
        """Test user preference setting and getting"""
        username = Username("testuser")
        credentials = SecurityCredentials(hashed_password="a" * 64)
        user = User(username, credentials)
        
        # Set preference
        pref = UserPreference(PreferenceType.NOTIFICATION, "email_alerts", "enabled")
        user.set_preference(pref)
        
        # Get preference
        retrieved = user.get_preference(PreferenceType.NOTIFICATION, "email_alerts")
        assert retrieved == pref
        
        # Non-existent preference
        none_pref = user.get_preference(PreferenceType.PRIVACY, "nonexistent")
        assert none_pref is None
        
        # Should have emitted domain event
        events = user.get_domain_events()
        assert len(events) == 1
        assert events[0].event_type == "preference_changed"
    
    def test_verification_tier_update(self):
        """Test verification tier update"""
        username = Username("testuser")
        credentials = SecurityCredentials(hashed_password="a" * 64)
        user = User(username, credentials)
        
        # Verify to identity level
        user.verify_tier(VerificationTier.IDENTITY_VERIFIED)
        
        assert user.verification_tier == VerificationTier.IDENTITY_VERIFIED
        assert user.permissions.can_real_trade is True
        
        # Should have emitted domain event
        events = user.get_domain_events()
        assert len(events) == 1
        assert events[0].event_type == "verification_tier_updated"
    
    def test_account_suspension(self):
        """Test account suspension functionality"""
        username = Username("testuser")
        credentials = SecurityCredentials(hashed_password="a" * 64)
        user = User(username, credentials)
        user.set_user_id(123)
        
        # Suspend account
        user.suspend_account("Terms violation")
        
        assert user.status == UserStatus.SUSPENDED
        assert not user.is_active()
        
        # Should have emitted domain event
        events = user.get_domain_events()
        assert len(events) == 1
        assert events[0].event_type == "account_suspended"
    
    def test_account_reactivation(self):
        """Test account reactivation functionality"""
        username = Username("testuser")
        credentials = SecurityCredentials(hashed_password="a" * 64)
        user = User(username, credentials)
        user.set_user_id(123)
        
        # Suspend then reactivate
        user.suspend_account("Test suspension")
        user.reactivate_account()
        
        assert user.status == UserStatus.ACTIVE
        assert user.is_active()
        
        # Should have emitted domain events
        events = user.get_domain_events()
        assert len(events) == 2
        assert events[0].event_type == "account_suspended"
        assert events[1].event_type == "account_reactivated"
    
    def test_login_recording(self):
        """Test login recording functionality"""
        username = Username("testuser")
        credentials = SecurityCredentials(hashed_password="a" * 64)
        user = User(username, credentials)
        user.set_user_id(123)
        
        # Record login
        session_info = user.record_login("192.168.1.1", "Mozilla/5.0")
        
        assert user.login_count == 1
        assert user.last_login_at is not None
        assert session_info.ip_address == "192.168.1.1"
        assert session_info.user_agent == "Mozilla/5.0"
        
        # Should have emitted domain event
        events = user.get_domain_events()
        assert len(events) == 1
        assert events[0].event_type == "user_logged_in"
    
    def test_real_trading_permission(self):
        """Test real trading permission logic"""
        username = Username("testuser")
        credentials = SecurityCredentials(hashed_password="a" * 64)
        user = User(username, credentials)
        
        # Initially cannot real trade
        assert not user.can_real_trade()
        
        # Verify to identity level
        user.verify_tier(VerificationTier.IDENTITY_VERIFIED)
        assert user.can_real_trade()
        
        # Suspend account
        user.suspend_account("Test")
        assert not user.can_real_trade()
    
    def test_security_score_calculation(self):
        """Test security score calculation"""
        username = Username("testuser")
        credentials = SecurityCredentials(
            hashed_password="a" * 64,
            two_factor_secret="secret123",
            last_password_change=datetime.now(timezone.utc)
        )
        email = Email("test@example.com")
        user = User(username, credentials, email)
        
        # Verify email
        user.verify_tier(VerificationTier.EMAIL_VERIFIED)
        
        # Connect wallet
        wallet = WalletAddress("0x1234567890abcdef", "starknet")
        user.connect_wallet(wallet)
        
        # Calculate security score
        score = user.get_security_score()
        
        # Should have points for: email (20), 2FA (30), password age (20), wallet (15), no identity verification (0)
        assert score == 85  # 20 + 30 + 20 + 15
    
    def test_domain_events_clearing(self):
        """Test that domain events are cleared after retrieval"""
        username = Username("testuser")
        credentials = SecurityCredentials(hashed_password="a" * 64)
        user = User(username, credentials)
        user.set_user_id(123)
        
        # Generate some events
        user.record_login("192.168.1.1", "Mozilla/5.0")
        user.suspend_account("Test")
        
        # Get events (should clear them)
        events = user.get_domain_events()
        assert len(events) == 2
        
        # Get events again (should be empty)
        events2 = user.get_domain_events()
        assert len(events2) == 0


class TestUserSession:
    """Test UserSession entity"""
    
    def test_session_creation(self):
        """Test creating a valid user session"""
        now = datetime.now(timezone.utc)
        session_info = SessionInfo(
            session_id="session123",
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0",
            created_at=now,
            expires_at=now + timedelta(hours=24)
        )
        
        session = UserSession(
            session_id="session123",
            user_id=123,
            session_info=session_info
        )
        
        assert session.session_id == "session123"
        assert session.user_id == 123
        assert session.is_active is True
        assert not session.is_expired()
    
    def test_invalid_session_creation(self):
        """Test invalid session creation raises errors"""
        now = datetime.now(timezone.utc)
        session_info = SessionInfo(
            session_id="session123",
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0",
            created_at=now,
            expires_at=now + timedelta(hours=24)
        )
        
        # Empty session ID
        with pytest.raises(ValueError, match="Session ID cannot be empty"):
            UserSession("", 123, session_info)
        
        # Invalid user ID
        with pytest.raises(ValueError, match="User ID must be positive"):
            UserSession("session123", 0, session_info)
    
    def test_activity_recording(self):
        """Test activity recording in session"""
        now = datetime.now(timezone.utc)
        session_info = SessionInfo(
            session_id="session123",
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0",
            created_at=now,
            expires_at=now + timedelta(hours=24)
        )
        
        session = UserSession("session123", 123, session_info)
        
        # Record activity
        session.record_activity(ActivityType.TRADE_EXECUTED, {"amount": 100})
        
        assert len(session.activities) == 1
        assert session.last_activity_at > now
        
        # Should have emitted domain event
        events = session.get_domain_events()
        assert len(events) == 1
        assert events[0].event_type == "user_activity_recorded"
    
    def test_activity_recording_on_inactive_session_fails(self):
        """Test that activity recording fails on inactive session"""
        now = datetime.now(timezone.utc)
        session_info = SessionInfo(
            session_id="session123",
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0",
            created_at=now,
            expires_at=now + timedelta(hours=24)
        )
        
        session = UserSession("session123", 123, session_info)
        session.terminate("test")
        
        with pytest.raises(ValueError, match="Cannot record activity on inactive or expired session"):
            session.record_activity(ActivityType.LOGIN)
    
    def test_session_termination(self):
        """Test session termination"""
        now = datetime.now(timezone.utc)
        session_info = SessionInfo(
            session_id="session123",
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0",
            created_at=now,
            expires_at=now + timedelta(hours=24)
        )
        
        session = UserSession("session123", 123, session_info)
        
        # Terminate session
        session.terminate("user_logout")
        
        assert not session.is_active
        
        # Should have emitted domain event
        events = session.get_domain_events()
        assert len(events) == 1
        assert events[0].event_type == "session_terminated"
    
    def test_session_duration_calculation(self):
        """Test session duration calculation"""
        now = datetime.now(timezone.utc)
        session_info = SessionInfo(
            session_id="session123",
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0",
            created_at=now,
            expires_at=now + timedelta(hours=24)
        )
        
        session = UserSession("session123", 123, session_info)
        
        # Simulate 30 minutes of activity
        session.last_activity_at = now + timedelta(minutes=30)
        
        duration = session.get_session_duration_minutes()
        assert duration == 30
    
    def test_activity_list_truncation(self):
        """Test that activity list is truncated to prevent memory bloat"""
        now = datetime.now(timezone.utc)
        session_info = SessionInfo(
            session_id="session123",
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0",
            created_at=now,
            expires_at=now + timedelta(hours=24)
        )
        
        session = UserSession("session123", 123, session_info)
        
        # Record 60 activities (more than the 50 limit)
        for i in range(60):
            session.record_activity(ActivityType.LOGIN)
        
        # Should keep only the last 50
        assert len(session.activities) == 50


class TestUserActivity:
    """Test UserActivity entity"""
    
    def test_activity_creation(self):
        """Test creating user activity tracker"""
        today = datetime.now(timezone.utc)
        activity = UserActivity(user_id=123, date=today)
        
        assert activity.user_id == 123
        assert activity.date == today
        assert activity.login_count == 0
        assert activity.trade_count == 0
        assert activity.activity_score == Decimal('0')
    
    def test_invalid_user_id_raises_error(self):
        """Test that invalid user ID raises error"""
        today = datetime.now(timezone.utc)
        
        with pytest.raises(ValueError, match="User ID must be positive"):
            UserActivity(user_id=0, date=today)
    
    def test_login_recording(self):
        """Test login activity recording"""
        today = datetime.now(timezone.utc)
        activity = UserActivity(user_id=123, date=today)
        
        # Record login
        activity.record_login("192.168.1.1")
        
        assert activity.login_count == 1
        assert "192.168.1.1" in activity.unique_ip_addresses
        assert activity.activity_score > Decimal('0')
    
    def test_trade_recording(self):
        """Test trade activity recording"""
        today = datetime.now(timezone.utc)
        activity = UserActivity(user_id=123, date=today)
        
        # Record trade
        activity.record_trade()
        
        assert activity.trade_count == 1
        assert activity.activity_score == Decimal('5.0')  # Trade worth 5 points
    
    def test_profile_update_recording(self):
        """Test profile update recording"""
        today = datetime.now(timezone.utc)
        activity = UserActivity(user_id=123, date=today)
        
        # Record profile update
        activity.record_profile_update()
        
        assert activity.profile_updates == 1
        assert activity.activity_score == Decimal('2.0')  # Profile update worth 2 points
    
    def test_session_duration_tracking(self):
        """Test session duration tracking"""
        today = datetime.now(timezone.utc)
        activity = UserActivity(user_id=123, date=today)
        
        # Add session duration
        activity.add_session_duration(120)  # 2 hours
        
        assert activity.session_duration_minutes == 120
        assert activity.activity_score == Decimal('12.0')  # 120 * 0.1 = 12 points
    
    def test_activity_score_calculation(self):
        """Test comprehensive activity score calculation"""
        today = datetime.now(timezone.utc)
        activity = UserActivity(user_id=123, date=today)
        
        # Record various activities
        activity.record_login("192.168.1.1")  # 1 point
        activity.record_login("10.0.0.1")     # 1 point + IP diversity bonus
        activity.record_trade()               # 5 points
        activity.record_profile_update()     # 2 points
        activity.add_session_duration(60)    # 6 points (60 * 0.1)
        
        # Base score: 1 + 1 + 5 + 2 + 6 = 15
        # IP diversity bonus: 15 * 1.2 = 18
        expected_score = Decimal('18.0')
        assert activity.activity_score == expected_score
    
    def test_engagement_level_calculation(self):
        """Test engagement level calculation"""
        today = datetime.now(timezone.utc)
        
        # Inactive user
        inactive = UserActivity(user_id=123, date=today)
        assert inactive.get_engagement_level() == "inactive"
        
        # Low engagement
        low = UserActivity(user_id=123, date=today)
        low.record_login("192.168.1.1")
        low.add_session_duration(100)  # Total score: 11
        assert low.get_engagement_level() == "low"
        
        # Medium engagement
        medium = UserActivity(user_id=123, date=today)
        for _ in range(10):
            medium.record_login("192.168.1.1")
        medium.add_session_duration(400)  # Total score: 50
        assert medium.get_engagement_level() == "medium"
        
        # High engagement
        high = UserActivity(user_id=123, date=today)
        for _ in range(20):
            high.record_trade()  # 20 * 5 = 100 points
        assert high.get_engagement_level() == "high"
    
    def test_ip_diversity_bonus(self):
        """Test IP address diversity bonus"""
        today = datetime.now(timezone.utc)
        activity = UserActivity(user_id=123, date=today)
        
        # Single IP
        activity.record_login("192.168.1.1")
        single_ip_score = activity.activity_score
        
        # Multiple IPs
        activity.record_login("10.0.0.1")
        multiple_ip_score = activity.activity_score
        
        # Multiple IP score should be 20% higher
        expected_multiple = single_ip_score * Decimal('2') * Decimal('1.2')  # 2 logins with bonus
        assert multiple_ip_score == expected_multiple