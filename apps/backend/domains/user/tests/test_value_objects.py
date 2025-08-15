"""
Test suite for User Domain Value Objects

Comprehensive tests ensuring all value objects maintain their invariants
and behave correctly under all conditions.
"""

import pytest
from datetime import datetime, timezone, timedelta
from decimal import Decimal

from ..value_objects import (
    Email, Username, WalletAddress, UserPreference, SecurityCredentials,
    UserProfile, SessionInfo, UserPermissions, UserStatus, VerificationTier,
    PreferenceType
)


class TestEmail:
    """Test Email value object"""
    
    def test_valid_email_creation(self):
        """Test creating valid email addresses"""
        valid_emails = [
            "user@example.com",
            "test.user+123@domain.co.uk",
            "admin@sub.domain.org",
            "user123@example.io"
        ]
        
        for email_str in valid_emails:
            email = Email(email_str)
            assert email.address == email_str
    
    def test_invalid_email_raises_error(self):
        """Test that invalid emails raise ValueError"""
        invalid_emails = [
            "invalid",
            "@domain.com",
            "user@",
            "user..double@domain.com",
            "user@domain",
            "",
            "user name@domain.com"
        ]
        
        for email_str in invalid_emails:
            with pytest.raises(ValueError, match="Invalid email address"):
                Email(email_str)
    
    def test_email_domain_extraction(self):
        """Test domain extraction from email"""
        email = Email("user@example.com")
        assert email.domain == "example.com"
        
        email2 = Email("test@sub.domain.org")
        assert email2.domain == "sub.domain.org"
    
    def test_email_local_part_extraction(self):
        """Test local part extraction from email"""
        email = Email("user123@example.com")
        assert email.local_part == "user123"
        
        email2 = Email("test.user+tag@domain.com")
        assert email2.local_part == "test.user+tag"
    
    def test_email_immutability(self):
        """Test that email is immutable"""
        email = Email("user@example.com")
        with pytest.raises(AttributeError):
            email.address = "new@example.com"


class TestUsername:
    """Test Username value object"""
    
    def test_valid_username_creation(self):
        """Test creating valid usernames"""
        valid_usernames = [
            "user123",
            "test_user",
            "admin-user",
            "a1b2c3",
            "validusername"
        ]
        
        for username_str in valid_usernames:
            username = Username(username_str)
            assert username.value == username_str
            assert str(username) == username_str
    
    def test_invalid_username_raises_error(self):
        """Test that invalid usernames raise ValueError"""
        invalid_usernames = [
            "ab",  # too short
            "a" * 31,  # too long
            "_user",  # starts with underscore
            "-user",  # starts with hyphen
            "user@name",  # invalid character
            "user name",  # space
            "",  # empty
            "123user!",  # special character
        ]
        
        for username_str in invalid_usernames:
            with pytest.raises(ValueError, match="Invalid username"):
                Username(username_str)
    
    def test_username_length_boundaries(self):
        """Test username length boundaries"""
        # Minimum valid length
        Username("abc")
        
        # Maximum valid length
        Username("a" * 30)
        
        # Too short
        with pytest.raises(ValueError):
            Username("ab")
        
        # Too long
        with pytest.raises(ValueError):
            Username("a" * 31)


class TestWalletAddress:
    """Test WalletAddress value object"""
    
    def test_valid_starknet_address(self):
        """Test valid StarkNet wallet addresses"""
        valid_addresses = [
            "0x1234567890abcdef",
            "0x" + "a" * 64,
            "1234567890abcdef",
            "0x123"
        ]
        
        for addr in valid_addresses:
            wallet = WalletAddress(addr, "starknet")
            assert wallet.address == addr
            assert wallet.network == "starknet"
    
    def test_invalid_starknet_address(self):
        """Test invalid StarkNet addresses raise error"""
        invalid_addresses = [
            "0x" + "z" * 64,  # invalid hex
            "0x" + "a" * 65,  # too long
            "",  # empty
            "not_hex_at_all"
        ]
        
        for addr in invalid_addresses:
            with pytest.raises(ValueError, match="Invalid starknet wallet address"):
                WalletAddress(addr, "starknet")
    
    def test_other_network_basic_validation(self):
        """Test basic validation for other networks"""
        # Should accept any address > 10 characters for unknown networks
        WalletAddress("1234567890abc", "ethereum")
        
        # Should reject very short addresses
        with pytest.raises(ValueError):
            WalletAddress("short", "ethereum")


class TestUserPreference:
    """Test UserPreference value object"""
    
    def test_valid_preference_creation(self):
        """Test creating valid user preferences"""
        pref = UserPreference(
            PreferenceType.NOTIFICATION,
            "email_alerts",
            "enabled"
        )
        assert pref.preference_type == PreferenceType.NOTIFICATION
        assert pref.key == "email_alerts"
        assert pref.value == "enabled"
        assert pref.is_encrypted is False
    
    def test_encrypted_preference(self):
        """Test encrypted preference creation"""
        pref = UserPreference(
            PreferenceType.PRIVACY,
            "api_key",
            "encrypted_value",
            is_encrypted=True
        )
        assert pref.is_encrypted is True
    
    def test_empty_key_raises_error(self):
        """Test that empty key raises ValueError"""
        with pytest.raises(ValueError, match="Preference key cannot be empty"):
            UserPreference(PreferenceType.NOTIFICATION, "", "value")
        
        with pytest.raises(ValueError, match="Preference key cannot be empty"):
            UserPreference(PreferenceType.NOTIFICATION, "   ", "value")
    
    def test_empty_value_raises_error(self):
        """Test that empty value raises ValueError"""
        with pytest.raises(ValueError, match="Preference value cannot be empty"):
            UserPreference(PreferenceType.NOTIFICATION, "key", "")
        
        with pytest.raises(ValueError, match="Preference value cannot be empty"):
            UserPreference(PreferenceType.NOTIFICATION, "key", "   ")


class TestSecurityCredentials:
    """Test SecurityCredentials value object"""
    
    def test_valid_credentials_creation(self):
        """Test creating valid security credentials"""
        creds = SecurityCredentials(
            hashed_password="a" * 64,
            password_salt="salt123",
            two_factor_secret="secret123",
            recovery_codes=["code1", "code2"],
            last_password_change=datetime.now(timezone.utc)
        )
        assert len(creds.hashed_password) == 64
        assert creds.password_salt == "salt123"
        assert creds.has_two_factor_enabled() is True
    
    def test_invalid_password_hash_raises_error(self):
        """Test that invalid password hash raises error"""
        with pytest.raises(ValueError, match="Invalid password hash"):
            SecurityCredentials(hashed_password="too_short")
        
        with pytest.raises(ValueError, match="Invalid password hash"):
            SecurityCredentials(hashed_password="")
    
    def test_password_reset_check(self):
        """Test password reset requirement check"""
        # Recent password change
        recent_creds = SecurityCredentials(
            hashed_password="a" * 64,
            last_password_change=datetime.now(timezone.utc) - timedelta(days=30)
        )
        assert recent_creds.needs_password_reset(90) is False
        
        # Old password change
        old_creds = SecurityCredentials(
            hashed_password="a" * 64,
            last_password_change=datetime.now(timezone.utc) - timedelta(days=100)
        )
        assert old_creds.needs_password_reset(90) is True
        
        # No password change recorded
        no_change_creds = SecurityCredentials(hashed_password="a" * 64)
        assert no_change_creds.needs_password_reset() is True
    
    def test_two_factor_detection(self):
        """Test two-factor authentication detection"""
        # Without 2FA
        no_2fa = SecurityCredentials(hashed_password="a" * 64)
        assert no_2fa.has_two_factor_enabled() is False
        
        # With 2FA
        with_2fa = SecurityCredentials(
            hashed_password="a" * 64,
            two_factor_secret="secret123"
        )
        assert with_2fa.has_two_factor_enabled() is True


class TestUserProfile:
    """Test UserProfile value object"""
    
    def test_valid_profile_creation(self):
        """Test creating valid user profile"""
        profile = UserProfile(
            display_name="John Doe",
            bio="Trading enthusiast",
            avatar_url="https://example.com/avatar.jpg",
            location="New York",
            website="https://johndoe.com",
            trading_experience_level="intermediate"
        )
        assert profile.display_name == "John Doe"
        assert profile.trading_experience_level == "intermediate"
    
    def test_default_profile_creation(self):
        """Test creating profile with defaults"""
        profile = UserProfile()
        assert profile.display_name is None
        assert profile.bio is None
        assert profile.trading_experience_level == "beginner"
    
    def test_display_name_too_long_raises_error(self):
        """Test that long display name raises error"""
        with pytest.raises(ValueError, match="Display name too long"):
            UserProfile(display_name="a" * 51)
    
    def test_bio_too_long_raises_error(self):
        """Test that long bio raises error"""
        with pytest.raises(ValueError, match="Bio too long"):
            UserProfile(bio="a" * 501)
    
    def test_invalid_experience_level_raises_error(self):
        """Test that invalid experience level raises error"""
        with pytest.raises(ValueError, match="Invalid trading experience level"):
            UserProfile(trading_experience_level="invalid")


class TestSessionInfo:
    """Test SessionInfo value object"""
    
    def test_valid_session_creation(self):
        """Test creating valid session info"""
        now = datetime.now(timezone.utc)
        expires = now + timedelta(hours=24)
        
        session = SessionInfo(
            session_id="a" * 32,
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0",
            created_at=now,
            expires_at=expires,
            is_mobile=False
        )
        assert session.session_id == "a" * 32
        assert session.is_expired() is False
    
    def test_invalid_session_id_raises_error(self):
        """Test that invalid session ID raises error"""
        now = datetime.now(timezone.utc)
        expires = now + timedelta(hours=24)
        
        with pytest.raises(ValueError, match="Invalid session ID"):
            SessionInfo("short", "192.168.1.1", "Mozilla/5.0", now, expires)
    
    def test_invalid_expiry_raises_error(self):
        """Test that invalid expiry time raises error"""
        now = datetime.now(timezone.utc)
        past = now - timedelta(hours=1)
        
        with pytest.raises(ValueError, match="Session expiry must be after creation time"):
            SessionInfo("a" * 32, "192.168.1.1", "Mozilla/5.0", now, past)
    
    def test_session_expiry_check(self):
        """Test session expiry check"""
        now = datetime.now(timezone.utc)
        
        # Future expiry - not expired
        future_session = SessionInfo(
            "a" * 32, "192.168.1.1", "Mozilla/5.0",
            now, now + timedelta(hours=24)
        )
        assert future_session.is_expired() is False
        
        # Past expiry - expired
        past_session = SessionInfo(
            "b" * 32, "192.168.1.1", "Mozilla/5.0",
            now - timedelta(hours=25), now - timedelta(hours=1)
        )
        assert past_session.is_expired() is True
    
    def test_time_until_expiry(self):
        """Test time until expiry calculation"""
        now = datetime.now(timezone.utc)
        expires = now + timedelta(seconds=3600)  # 1 hour
        
        session = SessionInfo(
            "a" * 32, "192.168.1.1", "Mozilla/5.0", now, expires
        )
        
        time_left = session.time_until_expiry()
        assert time_left is not None
        assert 3590 <= time_left <= 3600  # Allow for small time differences
        
        # Expired session
        expired_session = SessionInfo(
            "b" * 32, "192.168.1.1", "Mozilla/5.0",
            now - timedelta(hours=2), now - timedelta(hours=1)
        )
        assert expired_session.time_until_expiry() == 0


class TestUserPermissions:
    """Test UserPermissions value object"""
    
    def test_valid_permissions_creation(self):
        """Test creating valid user permissions"""
        perms = UserPermissions(
            role="admin",
            permissions=frozenset(["read", "write", "delete"]),
            is_admin=True,
            is_moderator=True,
            can_real_trade=True
        )
        assert perms.role == "admin"
        assert perms.is_admin is True
        assert perms.can_real_trade is True
    
    def test_default_permissions(self):
        """Test default permissions"""
        perms = UserPermissions()
        assert perms.role == "user"
        assert perms.is_admin is False
        assert perms.can_real_trade is False
    
    def test_invalid_role_raises_error(self):
        """Test that invalid role raises error"""
        with pytest.raises(ValueError, match="Invalid role"):
            UserPermissions(role="invalid_role")
    
    def test_permission_checking(self):
        """Test permission checking logic"""
        # Regular user
        user_perms = UserPermissions(
            permissions=frozenset(["read"])
        )
        assert user_perms.has_permission("read") is True
        assert user_perms.has_permission("write") is False
        
        # Admin user (has all permissions)
        admin_perms = UserPermissions(
            role="admin",
            is_admin=True
        )
        assert admin_perms.has_permission("read") is True
        assert admin_perms.has_permission("write") is True
        assert admin_perms.has_permission("delete") is True
    
    def test_action_permissions(self):
        """Test action-based permissions"""
        # Regular user
        user_perms = UserPermissions()
        assert user_perms.can_perform_action("real_trading") is False
        assert user_perms.can_perform_action("moderate_content") is False
        assert user_perms.can_perform_action("admin_access") is False
        
        # User with real trading
        trader_perms = UserPermissions(can_real_trade=True)
        assert trader_perms.can_perform_action("real_trading") is True
        
        # Moderator
        mod_perms = UserPermissions(is_moderator=True)
        assert mod_perms.can_perform_action("moderate_content") is True
        
        # Admin
        admin_perms = UserPermissions(is_admin=True)
        assert admin_perms.can_perform_action("admin_access") is True
        assert admin_perms.can_perform_action("moderate_content") is True