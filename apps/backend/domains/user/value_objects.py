"""
User Domain Value Objects

Value objects for the User Domain as defined in ADR-001.
These are immutable objects that describe characteristics of user-related concepts.
"""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional
from dataclasses import dataclass
import re


class UserStatus(Enum):
    """User account status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING_VERIFICATION = "pending_verification"


class VerificationTier(Enum):
    """User verification levels"""
    UNVERIFIED = "unverified"
    EMAIL_VERIFIED = "email_verified" 
    PHONE_VERIFIED = "phone_verified"
    IDENTITY_VERIFIED = "identity_verified"
    PREMIUM_VERIFIED = "premium_verified"


class PreferenceType(Enum):
    """Types of user preferences"""
    NOTIFICATION = "notification"
    TRADING = "trading"
    UI_THEME = "ui_theme"
    PRIVACY = "privacy"
    COMMUNICATION = "communication"


@dataclass(frozen=True)
class Email:
    """Value object for email addresses"""
    address: str
    
    def __post_init__(self):
        if not self._is_valid_email(self.address):
            raise ValueError(f"Invalid email address: {self.address}")
    
    def _is_valid_email(self, email: str) -> bool:
        """Basic email validation"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @property
    def domain(self) -> str:
        """Get email domain"""
        return self.address.split('@')[1]
    
    @property
    def local_part(self) -> str:
        """Get local part of email"""
        return self.address.split('@')[0]


@dataclass(frozen=True)
class Username:
    """Value object for usernames"""
    value: str
    
    def __post_init__(self):
        if not self._is_valid_username(self.value):
            raise ValueError(f"Invalid username: {self.value}")
    
    def _is_valid_username(self, username: str) -> bool:
        """Username validation rules"""
        if len(username) < 3 or len(username) > 30:
            return False
        
        # Allow alphanumeric, underscore, hyphen
        pattern = r'^[a-zA-Z0-9_-]+$'
        if not re.match(pattern, username):
            return False
        
        # Must start with alphanumeric
        if not username[0].isalnum():
            return False
        
        return True
    
    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class WalletAddress:
    """Value object for blockchain wallet addresses"""
    address: str
    network: str = "starknet"
    
    def __post_init__(self):
        if not self._is_valid_address(self.address, self.network):
            raise ValueError(f"Invalid {self.network} wallet address: {self.address}")
    
    def _is_valid_address(self, address: str, network: str) -> bool:
        """Basic wallet address validation"""
        if network.lower() == "starknet":
            # StarkNet addresses are hex strings, typically 64 characters
            if address.startswith('0x'):
                hex_part = address[2:]
            else:
                hex_part = address
            
            return len(hex_part) <= 64 and all(c in '0123456789abcdefABCDEF' for c in hex_part)
        
        # Add validation for other networks as needed
        return len(address) > 10  # Basic length check


@dataclass(frozen=True)
class UserPreference:
    """Value object for user preferences"""
    preference_type: PreferenceType
    key: str
    value: str
    is_encrypted: bool = False
    
    def __post_init__(self):
        if not self.key or len(self.key.strip()) == 0:
            raise ValueError("Preference key cannot be empty")
        if not self.value or len(self.value.strip()) == 0:
            raise ValueError("Preference value cannot be empty")


@dataclass(frozen=True)
class SecurityCredentials:
    """Value object for user security credentials"""
    hashed_password: str
    password_salt: Optional[str] = None
    two_factor_secret: Optional[str] = None
    recovery_codes: Optional[list] = None
    last_password_change: Optional[datetime] = None
    
    def __post_init__(self):
        if not self.hashed_password or len(self.hashed_password) < 32:
            raise ValueError("Invalid password hash")
    
    def needs_password_reset(self, max_age_days: int = 90) -> bool:
        """Check if password needs to be reset due to age"""
        if not self.last_password_change:
            return True
        
        # Ensure both timestamps are timezone-aware
        now = datetime.now(timezone.utc)
        last_change = self.last_password_change
        if last_change.tzinfo is None:
            last_change = last_change.replace(tzinfo=timezone.utc)
        
        age = now - last_change
        return age.days > max_age_days
    
    def has_two_factor_enabled(self) -> bool:
        """Check if two-factor authentication is enabled"""
        return self.two_factor_secret is not None


@dataclass(frozen=True)
class UserProfile:
    """Value object for user profile information"""
    display_name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    location: Optional[str] = None
    website: Optional[str] = None
    trading_experience_level: str = "beginner"
    
    def __post_init__(self):
        if self.display_name and len(self.display_name) > 50:
            raise ValueError("Display name too long")
        if self.bio and len(self.bio) > 500:
            raise ValueError("Bio too long")
        if self.trading_experience_level not in ["beginner", "intermediate", "advanced", "expert"]:
            raise ValueError("Invalid trading experience level")


@dataclass(frozen=True)
class SessionInfo:
    """Value object for user session information"""
    session_id: str
    ip_address: str
    user_agent: str
    created_at: datetime
    expires_at: datetime
    is_mobile: bool = False
    device_fingerprint: Optional[str] = None
    
    def __post_init__(self):
        if not self.session_id or len(self.session_id) < 16:
            raise ValueError("Invalid session ID")
        if self.expires_at <= self.created_at:
            raise ValueError("Session expiry must be after creation time")
    
    def is_expired(self) -> bool:
        """Check if session has expired"""
        now = datetime.now(timezone.utc)
        expires = self.expires_at
        if expires.tzinfo is None:
            expires = expires.replace(tzinfo=timezone.utc)
        return now > expires
    
    def time_until_expiry(self) -> Optional[int]:
        """Get seconds until session expires"""
        if self.is_expired():
            return 0
        
        now = datetime.now(timezone.utc)
        expires = self.expires_at
        if expires.tzinfo is None:
            expires = expires.replace(tzinfo=timezone.utc)
        
        return int((expires - now).total_seconds())


@dataclass(frozen=True)
class UserPermissions:
    """Value object for user permissions and roles"""
    role: str = "user"
    permissions: frozenset = frozenset()
    is_admin: bool = False
    is_moderator: bool = False
    can_real_trade: bool = False
    
    def __post_init__(self):
        valid_roles = ["user", "vip", "moderator", "admin"]
        if self.role not in valid_roles:
            raise ValueError(f"Invalid role: {self.role}")
    
    def has_permission(self, permission: str) -> bool:
        """Check if user has specific permission"""
        return permission in self.permissions or self.is_admin
    
    def can_perform_action(self, action: str) -> bool:
        """Check if user can perform specific action"""
        action_permissions = {
            "real_trading": self.can_real_trade,
            "moderate_content": self.is_moderator or self.is_admin,
            "admin_access": self.is_admin
        }
        return action_permissions.get(action, False)