"""
Test suite for User Domain Services

Comprehensive tests for domain services ensuring business logic
coordination and complex operations work correctly.
"""

import pytest
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from typing import Optional, List, Dict, Any
from unittest.mock import Mock, MagicMock

from ..services import (
    UserAuthenticationService, UserManagementService, UserSecurityService,
    UserActivityService, UserRepositoryInterface, SessionRepositoryInterface,
    PasswordServiceInterface
)
from ..entities import User, UserSession, UserActivity, ActivityType
from ..value_objects import (
    Email, Username, WalletAddress, UserPreference, SecurityCredentials,
    UserProfile, SessionInfo, UserPermissions, UserStatus, VerificationTier,
    PreferenceType
)


class TestUserAuthenticationService:
    """Test UserAuthenticationService"""
    
    def setup_method(self):
        """Set up test dependencies"""
        self.user_repo = Mock(spec=UserRepositoryInterface)
        self.session_repo = Mock(spec=SessionRepositoryInterface)
        self.password_service = Mock(spec=PasswordServiceInterface)
        
        self.auth_service = UserAuthenticationService(
            self.user_repo,
            self.session_repo,
            self.password_service
        )
    
    def test_successful_user_authentication(self):
        """Test successful user authentication"""
        # Setup
        username = Username("testuser")
        credentials = SecurityCredentials(hashed_password="a" * 64)
        user = User(username, credentials)
        user.set_user_id(123)
        
        self.user_repo.find_by_username.return_value = user
        self.password_service.verify_password.return_value = True
        self.user_repo.save.return_value = user
        self.session_repo.save.return_value = None
        
        # Execute
        session = self.auth_service.authenticate_user(
            "testuser", "password", "192.168.1.1", "Mozilla/5.0"
        )
        
        # Verify
        assert session is not None
        assert session.user_id == 123
        assert session.is_active
        
        self.user_repo.find_by_username.assert_called_once_with("testuser")
        self.password_service.verify_password.assert_called_once()
        self.user_repo.save.assert_called_once()
        self.session_repo.save.assert_called_once()
    
    def test_authentication_with_email(self):
        """Test authentication using email address"""
        # Setup
        username = Username("testuser")
        email = Email("test@example.com")
        credentials = SecurityCredentials(hashed_password="a" * 64)
        user = User(username, credentials, email)
        user.set_user_id(123)
        
        self.user_repo.find_by_username.return_value = None
        self.user_repo.find_by_email.return_value = user
        self.password_service.verify_password.return_value = True
        self.user_repo.save.return_value = user
        
        # Execute
        session = self.auth_service.authenticate_user(
            "test@example.com", "password", "192.168.1.1", "Mozilla/5.0"
        )
        
        # Verify
        assert session is not None
        self.user_repo.find_by_username.assert_called_once_with("test@example.com")
        self.user_repo.find_by_email.assert_called_once_with("test@example.com")
    
    def test_authentication_fails_user_not_found(self):
        """Test authentication fails when user not found"""
        self.user_repo.find_by_username.return_value = None
        self.user_repo.find_by_email.return_value = None
        
        session = self.auth_service.authenticate_user(
            "nonexistent", "password", "192.168.1.1", "Mozilla/5.0"
        )
        
        assert session is None
        self.password_service.verify_password.assert_not_called()
    
    def test_authentication_fails_wrong_password(self):
        """Test authentication fails with wrong password"""
        username = Username("testuser")
        credentials = SecurityCredentials(hashed_password="a" * 64)
        user = User(username, credentials)
        
        self.user_repo.find_by_username.return_value = user
        self.password_service.verify_password.return_value = False
        
        session = self.auth_service.authenticate_user(
            "testuser", "wrongpassword", "192.168.1.1", "Mozilla/5.0"
        )
        
        assert session is None
        self.user_repo.save.assert_not_called()
    
    def test_authentication_fails_inactive_user(self):
        """Test authentication fails for inactive user"""
        username = Username("testuser")
        credentials = SecurityCredentials(hashed_password="a" * 64)
        user = User(username, credentials)
        user.set_user_id(123)
        user.suspend_account("Test suspension")
        
        self.user_repo.find_by_username.return_value = user
        self.password_service.verify_password.return_value = True
        
        session = self.auth_service.authenticate_user(
            "testuser", "password", "192.168.1.1", "Mozilla/5.0"
        )
        
        assert session is None
    
    def test_successful_logout(self):
        """Test successful user logout"""
        # Setup active session
        now = datetime.now(timezone.utc)
        session_info = SessionInfo(
            "session123", "192.168.1.1", "Mozilla/5.0",
            now, now + timedelta(hours=24)
        )
        session = UserSession("session123", 123, session_info)
        
        self.session_repo.find_by_session_id.return_value = session
        self.session_repo.save.return_value = None
        
        # Execute
        result = self.auth_service.logout_user("session123")
        
        # Verify
        assert result is True
        assert not session.is_active
        self.session_repo.save.assert_called_once()
    
    def test_logout_fails_session_not_found(self):
        """Test logout fails when session not found"""
        self.session_repo.find_by_session_id.return_value = None
        
        result = self.auth_service.logout_user("nonexistent")
        
        assert result is False
        self.session_repo.save.assert_not_called()
    
    def test_session_validation_success(self):
        """Test successful session validation"""
        # Setup
        username = Username("testuser")
        credentials = SecurityCredentials(hashed_password="a" * 64)
        user = User(username, credentials)
        user.set_user_id(123)
        
        now = datetime.now(timezone.utc)
        session_info = SessionInfo(
            "session123", "192.168.1.1", "Mozilla/5.0",
            now, now + timedelta(hours=24)
        )
        session = UserSession("session123", 123, session_info)
        
        self.session_repo.find_by_session_id.return_value = session
        self.session_repo.save.return_value = None
        self.user_repo.find_by_id.return_value = user
        
        # Execute
        validated_user = self.auth_service.validate_session("session123")
        
        # Verify
        assert validated_user == user
        self.session_repo.save.assert_called_once()  # For activity update
    
    def test_session_validation_fails_expired(self):
        """Test session validation fails for expired session"""
        now = datetime.now(timezone.utc)
        session_info = SessionInfo(
            "session123", "192.168.1.1", "Mozilla/5.0",
            now - timedelta(hours=25), now - timedelta(hours=1)  # Expired
        )
        session = UserSession("session123", 123, session_info)
        
        self.session_repo.find_by_session_id.return_value = session
        
        validated_user = self.auth_service.validate_session("session123")
        
        assert validated_user is None
    
    def test_terminate_all_user_sessions(self):
        """Test terminating all user sessions"""
        # Setup multiple sessions
        now = datetime.now(timezone.utc)
        sessions = []
        for i in range(3):
            session_info = SessionInfo(
                f"session{i}", "192.168.1.1", "Mozilla/5.0",
                now, now + timedelta(hours=24)
            )
            session = UserSession(f"session{i}", 123, session_info)
            sessions.append(session)
        
        self.session_repo.find_active_sessions_by_user.return_value = sessions
        self.session_repo.save.return_value = None
        
        # Execute
        count = self.auth_service.terminate_all_user_sessions(123)
        
        # Verify
        assert count == 3
        assert self.session_repo.save.call_count == 3
        for session in sessions:
            assert not session.is_active
    
    def test_cleanup_expired_sessions(self):
        """Test cleanup of expired sessions"""
        self.session_repo.cleanup_expired_sessions.return_value = 5
        
        count = self.auth_service.cleanup_expired_sessions()
        
        assert count == 5
        self.session_repo.cleanup_expired_sessions.assert_called_once()


class TestUserManagementService:
    """Test UserManagementService"""
    
    def setup_method(self):
        """Set up test dependencies"""
        self.user_repo = Mock(spec=UserRepositoryInterface)
        self.password_service = Mock(spec=PasswordServiceInterface)
        
        self.management_service = UserManagementService(
            self.user_repo,
            self.password_service
        )
    
    def test_successful_user_registration(self):
        """Test successful user registration"""
        # Setup
        self.user_repo.exists_username.return_value = False
        self.user_repo.exists_email.return_value = False
        self.password_service.hash_password.return_value = "hashed_password_123"
        self.password_service.generate_salt.return_value = "salt123"
        
        created_user = User(
            Username("testuser"),
            SecurityCredentials(hashed_password="hashed_password_123")
        )
        created_user.set_user_id(123)
        self.user_repo.save.return_value = created_user
        
        # Execute
        user = self.management_service.register_user(
            "testuser", "password123", "test@example.com"
        )
        
        # Verify
        assert user.user_id == 123
        self.user_repo.exists_username.assert_called_once_with("testuser")
        self.user_repo.exists_email.assert_called_once_with("test@example.com")
        self.password_service.hash_password.assert_called_once_with("password123")
        self.user_repo.save.assert_called_once()
    
    def test_registration_fails_duplicate_username(self):
        """Test registration fails with duplicate username"""
        self.user_repo.exists_username.return_value = True
        
        with pytest.raises(ValueError, match="Username 'testuser' already exists"):
            self.management_service.register_user("testuser", "password123")
    
    def test_registration_fails_duplicate_email(self):
        """Test registration fails with duplicate email"""
        self.user_repo.exists_username.return_value = False
        self.user_repo.exists_email.return_value = True
        
        with pytest.raises(ValueError, match="Email 'test@example.com' already registered"):
            self.management_service.register_user("testuser", "password123", "test@example.com")
    
    def test_update_user_profile(self):
        """Test updating user profile"""
        # Setup
        username = Username("testuser")
        credentials = SecurityCredentials(hashed_password="a" * 64)
        user = User(username, credentials)
        user.set_user_id(123)
        
        self.user_repo.find_by_id.return_value = user
        self.user_repo.save.return_value = user
        
        profile_data = {
            "display_name": "John Doe",
            "bio": "Trading expert",
            "trading_experience_level": "advanced"
        }
        
        # Execute
        updated_user = self.management_service.update_user_profile(123, profile_data)
        
        # Verify
        assert updated_user.profile.display_name == "John Doe"
        assert updated_user.profile.bio == "Trading expert"
        assert updated_user.profile.trading_experience_level == "advanced"
        self.user_repo.save.assert_called_once()
    
    def test_update_profile_user_not_found(self):
        """Test profile update fails when user not found"""
        self.user_repo.find_by_id.return_value = None
        
        with pytest.raises(ValueError, match="User with ID 123 not found"):
            self.management_service.update_user_profile(123, {})
    
    def test_connect_wallet_to_user(self):
        """Test connecting wallet to user"""
        # Setup
        username = Username("testuser")
        credentials = SecurityCredentials(hashed_password="a" * 64)
        user = User(username, credentials)
        user.set_user_id(123)
        
        self.user_repo.find_by_id.return_value = user
        self.user_repo.save.return_value = user
        
        # Execute
        updated_user = self.management_service.connect_wallet_to_user(
            123, "0x1234567890abcdef", "starknet"
        )
        
        # Verify
        assert updated_user.wallet_address is not None
        assert updated_user.wallet_address.address == "0x1234567890abcdef"
        assert updated_user.wallet_address.network == "starknet"
        self.user_repo.save.assert_called_once()
    
    def test_update_user_email(self):
        """Test updating user email"""
        # Setup
        username = Username("testuser")
        credentials = SecurityCredentials(hashed_password="a" * 64)
        old_email = Email("old@example.com")
        user = User(username, credentials, old_email)
        user.set_user_id(123)
        
        self.user_repo.find_by_id.return_value = user
        self.user_repo.exists_email.return_value = False
        self.user_repo.save.return_value = user
        
        # Execute
        updated_user = self.management_service.update_user_email(123, "new@example.com")
        
        # Verify
        assert updated_user.email.address == "new@example.com"
        assert updated_user.verification_tier == VerificationTier.UNVERIFIED
        self.user_repo.save.assert_called_once()
    
    def test_update_email_duplicate_fails(self):
        """Test email update fails with duplicate email"""
        username = Username("testuser")
        credentials = SecurityCredentials(hashed_password="a" * 64)
        user = User(username, credentials)
        user.set_user_id(123)
        
        self.user_repo.find_by_id.return_value = user
        self.user_repo.exists_email.return_value = True
        
        with pytest.raises(ValueError, match="Email 'new@example.com' already registered"):
            self.management_service.update_user_email(123, "new@example.com")
    
    def test_verify_user_tier(self):
        """Test user verification tier update"""
        # Setup
        username = Username("testuser")
        credentials = SecurityCredentials(hashed_password="a" * 64)
        user = User(username, credentials)
        user.set_user_id(123)
        
        self.user_repo.find_by_id.return_value = user
        self.user_repo.save.return_value = user
        
        # Execute
        updated_user = self.management_service.verify_user_tier(123, "identity_verified")
        
        # Verify
        assert updated_user.verification_tier == VerificationTier.IDENTITY_VERIFIED
        assert updated_user.permissions.can_real_trade is True
        self.user_repo.save.assert_called_once()
    
    def test_set_user_preference(self):
        """Test setting user preference"""
        # Setup
        username = Username("testuser")
        credentials = SecurityCredentials(hashed_password="a" * 64)
        user = User(username, credentials)
        user.set_user_id(123)
        
        self.user_repo.find_by_id.return_value = user
        self.user_repo.save.return_value = user
        
        # Execute
        updated_user = self.management_service.set_user_preference(
            123, "notification", "email_alerts", "enabled"
        )
        
        # Verify
        pref = updated_user.get_preference(PreferenceType.NOTIFICATION, "email_alerts")
        assert pref is not None
        assert pref.value == "enabled"
        self.user_repo.save.assert_called_once()


class TestUserSecurityService:
    """Test UserSecurityService"""
    
    def setup_method(self):
        """Set up test dependencies"""
        self.user_repo = Mock(spec=UserRepositoryInterface)
        self.session_repo = Mock(spec=SessionRepositoryInterface)
        self.password_service = Mock(spec=PasswordServiceInterface)
        
        self.security_service = UserSecurityService(
            self.user_repo,
            self.session_repo,
            self.password_service
        )
    
    def test_successful_password_change(self):
        """Test successful password change"""
        # Setup
        username = Username("testuser")
        credentials = SecurityCredentials(hashed_password="old_hash" + "a" * 56)
        user = User(username, credentials)
        user.set_user_id(123)
        
        self.user_repo.find_by_id.return_value = user
        self.password_service.verify_password.return_value = True
        self.password_service.hash_password.return_value = "new_hash" + "a" * 56
        self.user_repo.save.return_value = user
        self.session_repo.find_active_sessions_by_user.return_value = []
        
        # Execute
        updated_user = self.security_service.change_user_password(
            123, "old_password", "new_password"
        )
        
        # Verify
        assert updated_user._security_credentials.hashed_password == "new_hash" + "a" * 56
        self.password_service.verify_password.assert_called_once_with(
            "old_password", "old_hash" + "a" * 56
        )
        self.password_service.hash_password.assert_called_once_with("new_password")
        self.user_repo.save.assert_called_once()
    
    def test_password_change_fails_wrong_current_password(self):
        """Test password change fails with wrong current password"""
        username = Username("testuser")
        credentials = SecurityCredentials(hashed_password="a" * 64)
        user = User(username, credentials)
        user.set_user_id(123)
        
        self.user_repo.find_by_id.return_value = user
        self.password_service.verify_password.return_value = False
        
        with pytest.raises(ValueError, match="Current password is incorrect"):
            self.security_service.change_user_password(123, "wrong_password", "new_password")
    
    def test_suspend_user_account(self):
        """Test user account suspension"""
        # Setup
        username = Username("testuser")
        credentials = SecurityCredentials(hashed_password="a" * 64)
        user = User(username, credentials)
        user.set_user_id(123)
        
        self.user_repo.find_by_id.return_value = user
        self.user_repo.save.return_value = user
        self.session_repo.find_active_sessions_by_user.return_value = []
        
        # Execute
        suspended_user = self.security_service.suspend_user_account(123, "Terms violation")
        
        # Verify
        assert suspended_user.status == UserStatus.SUSPENDED
        assert not suspended_user.is_active()
        self.user_repo.save.assert_called_once()
    
    def test_reactivate_user_account(self):
        """Test user account reactivation"""
        # Setup
        username = Username("testuser")
        credentials = SecurityCredentials(hashed_password="a" * 64)
        user = User(username, credentials)
        user.set_user_id(123)
        user.suspend_account("Test")
        
        self.user_repo.find_by_id.return_value = user
        self.user_repo.save.return_value = user
        
        # Execute
        reactivated_user = self.security_service.reactivate_user_account(123)
        
        # Verify
        assert reactivated_user.status == UserStatus.ACTIVE
        assert reactivated_user.is_active()
        self.user_repo.save.assert_called_once()
    
    def test_get_user_security_score(self):
        """Test getting user security score"""
        # Setup user with various security features
        username = Username("testuser")
        credentials = SecurityCredentials(
            hashed_password="a" * 64,
            two_factor_secret="secret123",
            last_password_change=datetime.now(timezone.utc)
        )
        email = Email("test@example.com")
        user = User(username, credentials, email)
        user.set_user_id(123)
        user.verify_tier(VerificationTier.EMAIL_VERIFIED)
        
        wallet = WalletAddress("0x1234567890abcdef", "starknet")
        user.connect_wallet(wallet)
        
        self.user_repo.find_by_id.return_value = user
        
        # Execute
        score = self.security_service.get_user_security_score(123)
        
        # Verify - should have email (20) + 2FA (30) + password age (20) + wallet (15) = 85
        assert score == 85
    
    def test_terminate_all_sessions_except_current(self):
        """Test terminating all user sessions except current"""
        # Setup multiple sessions
        now = datetime.now(timezone.utc)
        sessions = []
        for i in range(3):
            session_info = SessionInfo(
                f"session{i}", "192.168.1.1", "Mozilla/5.0",
                now, now + timedelta(hours=24)
            )
            session = UserSession(f"session{i}", 123, session_info)
            sessions.append(session)
        
        self.session_repo.find_active_sessions_by_user.return_value = sessions
        self.session_repo.save.return_value = None
        
        # Execute - keep session1, terminate others
        count = self.security_service.terminate_all_user_sessions_except_current(123, "session1")
        
        # Verify
        assert count == 2  # Should terminate 2 out of 3 sessions
        assert sessions[1].is_active  # session1 should remain active
        assert not sessions[0].is_active  # session0 should be terminated
        assert not sessions[2].is_active  # session2 should be terminated


class TestUserActivityService:
    """Test UserActivityService"""
    
    def setup_method(self):
        """Set up test dependencies"""
        self.user_repo = Mock(spec=UserRepositoryInterface)
        self.activity_service = UserActivityService(self.user_repo)
    
    def test_record_login_activity(self):
        """Test recording login activity"""
        # Execute
        self.activity_service.record_user_activity(
            123, ActivityType.LOGIN, details={"ip_address": "192.168.1.1"}
        )
        
        # Verify
        today = datetime.now(timezone.utc).date()
        activity_key = f"123:{today}"
        
        assert activity_key in self.activity_service._daily_activities
        activity = self.activity_service._daily_activities[activity_key]
        assert activity.login_count == 1
        assert "192.168.1.1" in activity.unique_ip_addresses
    
    def test_record_trade_activity(self):
        """Test recording trade activity"""
        # Execute
        self.activity_service.record_user_activity(123, ActivityType.TRADE_EXECUTED)
        
        # Verify
        today = datetime.now(timezone.utc).date()
        activity_key = f"123:{today}"
        
        assert activity_key in self.activity_service._daily_activities
        activity = self.activity_service._daily_activities[activity_key]
        assert activity.trade_count == 1
    
    def test_record_profile_update_activity(self):
        """Test recording profile update activity"""
        # Execute
        self.activity_service.record_user_activity(123, ActivityType.PROFILE_UPDATED)
        
        # Verify
        today = datetime.now(timezone.utc).date()
        activity_key = f"123:{today}"
        
        assert activity_key in self.activity_service._daily_activities
        activity = self.activity_service._daily_activities[activity_key]
        assert activity.profile_updates == 1
    
    def test_get_user_engagement_level(self):
        """Test getting user engagement level"""
        # Record some activities
        self.activity_service.record_user_activity(123, ActivityType.LOGIN)
        self.activity_service.record_user_activity(123, ActivityType.TRADE_EXECUTED)
        
        # Execute
        engagement = self.activity_service.get_user_engagement_level(123)
        
        # Verify - should be "low" with login (1) + trade (5) = 6 points
        assert engagement == "low"
    
    def test_get_user_engagement_inactive_user(self):
        """Test engagement level for inactive user"""
        engagement = self.activity_service.get_user_engagement_level(999)
        assert engagement == "inactive"
    
    def test_get_user_activity_summary(self):
        """Test getting user activity summary"""
        # Record activities over multiple calls
        for _ in range(3):
            self.activity_service.record_user_activity(123, ActivityType.LOGIN)
        for _ in range(2):
            self.activity_service.record_user_activity(123, ActivityType.TRADE_EXECUTED)
        self.activity_service.record_user_activity(123, ActivityType.PROFILE_UPDATED)
        
        # Execute
        summary = self.activity_service.get_user_activity_summary(123, days=1)
        
        # Verify
        assert summary["total_logins"] == 3
        assert summary["total_trades"] == 2
        assert summary["unique_days_active"] == 1
        # 3 logins (3) + 2 trades (10) + 1 profile update (2) = 15 points = "medium"
        assert summary["average_engagement"] == "medium"
    
    def test_activity_summary_no_activity(self):
        """Test activity summary for user with no activity"""
        summary = self.activity_service.get_user_activity_summary(999, days=7)
        
        assert summary["total_logins"] == 0
        assert summary["total_trades"] == 0
        assert summary["unique_days_active"] == 0
        assert summary["average_engagement"] == "inactive"