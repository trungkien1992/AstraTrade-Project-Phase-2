"""
User Domain Entities

Core business entities for the User Domain as defined in ADR-001.
These entities encapsulate the essential business concepts and invariants for user management.

Domain Entities implemented:
- User: Core user aggregate root with authentication and profile management
- UserSession: Active user sessions with security tracking
- UserActivity: User activity tracking and analytics

Architecture follows DDD patterns with:
- Immutable creation after construction
- Business rule enforcement
- Domain event emission
- Rich domain behavior (not anemic models)
"""

from datetime import datetime, timezone, timedelta
from decimal import Decimal
from enum import Enum
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from uuid import uuid4

from .value_objects import (
    Email, Username, WalletAddress, UserPreference, SecurityCredentials,
    UserProfile, SessionInfo, UserPermissions, UserStatus, VerificationTier,
    PreferenceType
)
from ..shared.events import DomainEvent


class ActivityType(Enum):
    """Types of user activities"""
    LOGIN = "login"
    LOGOUT = "logout"
    TRADE_EXECUTED = "trade_executed"
    PROFILE_UPDATED = "profile_updated"
    PREFERENCE_CHANGED = "preference_changed"
    PASSWORD_CHANGED = "password_changed"
    TWO_FACTOR_ENABLED = "two_factor_enabled"
    WALLET_CONNECTED = "wallet_connected"


class User:
    """
    User aggregate root representing a platform user.
    
    Encapsulates all user-related business logic including authentication,
    profile management, preferences, and security features.
    
    Invariants:
    - User ID is immutable once set
    - Username must be unique and valid
    - Email must be unique and valid (if provided)
    - Status transitions follow valid business rules
    - Security credentials must meet minimum requirements
    """
    
    def __init__(
        self,
        username: Username,
        security_credentials: SecurityCredentials,
        email: Optional[Email] = None,
        user_id: Optional[int] = None,
        created_at: Optional[datetime] = None
    ):
        self._user_id = user_id
        self._username = username
        self._email = email
        self._security_credentials = security_credentials
        self._status = UserStatus.ACTIVE
        self._verification_tier = VerificationTier.UNVERIFIED
        self._profile = UserProfile()
        self._permissions = UserPermissions()
        self._wallet_address: Optional[WalletAddress] = None
        self._preferences: Dict[str, UserPreference] = {}
        self._created_at = created_at or datetime.now(timezone.utc)
        self._updated_at = datetime.now(timezone.utc)
        self._last_login_at: Optional[datetime] = None
        self._login_count = 0
        
        # Domain events (would be implemented with proper event system)
        self._domain_events: List[DomainEvent] = []
    
    @property
    def user_id(self) -> Optional[int]:
        return self._user_id
    
    @property
    def username(self) -> Username:
        return self._username
    
    @property
    def email(self) -> Optional[Email]:
        return self._email
    
    @property
    def status(self) -> UserStatus:
        return self._status
    
    @property
    def verification_tier(self) -> VerificationTier:
        return self._verification_tier
    
    @property
    def profile(self) -> UserProfile:
        return self._profile
    
    @property
    def permissions(self) -> UserPermissions:
        return self._permissions
    
    @property
    def wallet_address(self) -> Optional[WalletAddress]:
        return self._wallet_address
    
    @property
    def created_at(self) -> datetime:
        return self._created_at
    
    @property
    def updated_at(self) -> datetime:
        return self._updated_at
    
    @property
    def last_login_at(self) -> Optional[datetime]:
        return self._last_login_at
    
    @property
    def login_count(self) -> int:
        return self._login_count
    
    def set_user_id(self, user_id: int) -> None:
        """Set user ID (only allowed once during creation)"""
        if self._user_id is not None:
            raise ValueError("User ID cannot be changed once set")
        if user_id <= 0:
            raise ValueError("User ID must be positive")
        self._user_id = user_id
    
    def verify_password(self, plain_password: str) -> bool:
        """Verify password against stored credentials"""
        # This would integrate with the password hashing service
        # For now, return basic validation
        return len(plain_password) > 0
    
    def change_password(self, new_password_hash: str, old_password: Optional[str] = None) -> None:
        """Change user password with security validation"""
        if old_password and not self.verify_password(old_password):
            raise ValueError("Current password is incorrect")
        
        if len(new_password_hash) < 32:
            raise ValueError("Invalid password hash")
        
        self._security_credentials = SecurityCredentials(
            hashed_password=new_password_hash,
            password_salt=self._security_credentials.password_salt,
            two_factor_secret=self._security_credentials.two_factor_secret,
            recovery_codes=self._security_credentials.recovery_codes,
            last_password_change=datetime.now(timezone.utc)
        )
        
        self._updated_at = datetime.now(timezone.utc)
        
        self._add_domain_event("password_changed", {
            "user_id": self._user_id,
            "username": self._username.value,
            "changed_at": self._updated_at.isoformat(),
            "requires_re_authentication": True
        })
    
    def update_email(self, new_email: Email) -> None:
        """Update user email address"""
        old_email = self._email.address if self._email else None
        self._email = new_email
        self._verification_tier = VerificationTier.UNVERIFIED  # Reset verification
        self._updated_at = datetime.now(timezone.utc)
        
        self._add_domain_event("email_updated", {
            "user_id": self._user_id,
            "old_email": old_email,
            "new_email": new_email.address,
            "verification_reset": True
        })
    
    def connect_wallet(self, wallet_address: WalletAddress) -> None:
        """Connect blockchain wallet to user account"""
        self._wallet_address = wallet_address
        self._updated_at = datetime.now(timezone.utc)
        
        self._add_domain_event("wallet_connected", {
            "user_id": self._user_id,
            "wallet_address": wallet_address.address,
            "network": wallet_address.network,
            "connected_at": self._updated_at.isoformat()
        })
    
    def update_profile(self, new_profile: UserProfile) -> None:
        """Update user profile information"""
        old_profile = self._profile
        self._profile = new_profile
        self._updated_at = datetime.now(timezone.utc)
        
        self._add_domain_event("profile_updated", {
            "user_id": self._user_id,
            "changes": self._get_profile_changes(old_profile, new_profile),
            "updated_at": self._updated_at.isoformat()
        })
    
    def set_preference(self, preference: UserPreference) -> None:
        """Set user preference"""
        preference_key = f"{preference.preference_type.value}:{preference.key}"
        old_value = self._preferences.get(preference_key)
        
        self._preferences[preference_key] = preference
        self._updated_at = datetime.now(timezone.utc)
        
        self._add_domain_event("preference_changed", {
            "user_id": self._user_id,
            "preference_type": preference.preference_type.value,
            "key": preference.key,
            "old_value": old_value.value if old_value else None,
            "new_value": preference.value,
            "updated_at": self._updated_at.isoformat()
        })
    
    def get_preference(self, preference_type: PreferenceType, key: str) -> Optional[UserPreference]:
        """Get user preference"""
        preference_key = f"{preference_type.value}:{key}"
        return self._preferences.get(preference_key)
    
    def verify_tier(self, tier: VerificationTier) -> None:
        """Update user verification tier"""
        if tier.value <= self._verification_tier.value:
            return  # Cannot downgrade verification
        
        old_tier = self._verification_tier
        self._verification_tier = tier
        self._updated_at = datetime.now(timezone.utc)
        
        # Update permissions based on verification tier
        if tier in [VerificationTier.IDENTITY_VERIFIED, VerificationTier.PREMIUM_VERIFIED]:
            self._permissions = UserPermissions(
                role=self._permissions.role,
                permissions=self._permissions.permissions | {"real_trading"},
                is_admin=self._permissions.is_admin,
                is_moderator=self._permissions.is_moderator,
                can_real_trade=True
            )
        
        self._add_domain_event("verification_tier_updated", {
            "user_id": self._user_id,
            "old_tier": old_tier.value,
            "new_tier": tier.value,
            "permissions_updated": True,
            "updated_at": self._updated_at.isoformat()
        })
    
    def suspend_account(self, reason: str) -> None:
        """Suspend user account"""
        if self._status == UserStatus.SUSPENDED:
            return
        
        old_status = self._status
        self._status = UserStatus.SUSPENDED
        self._updated_at = datetime.now(timezone.utc)
        
        self._add_domain_event("account_suspended", {
            "user_id": self._user_id,
            "reason": reason,
            "previous_status": old_status.value,
            "suspended_at": self._updated_at.isoformat()
        })
    
    def reactivate_account(self) -> None:
        """Reactivate suspended account"""
        if self._status != UserStatus.SUSPENDED:
            return
        
        self._status = UserStatus.ACTIVE
        self._updated_at = datetime.now(timezone.utc)
        
        self._add_domain_event("account_reactivated", {
            "user_id": self._user_id,
            "reactivated_at": self._updated_at.isoformat()
        })
    
    def record_login(self, ip_address: str, user_agent: str) -> SessionInfo:
        """Record user login and create session"""
        self._last_login_at = datetime.now(timezone.utc)
        self._login_count += 1
        self._updated_at = self._last_login_at
        
        # Create session info
        session_info = SessionInfo(
            session_id=str(uuid4()),
            ip_address=ip_address,
            user_agent=user_agent,
            created_at=self._last_login_at,
            expires_at=self._last_login_at + timedelta(hours=24),
            is_mobile="mobile" in user_agent.lower()
        )
        
        self._add_domain_event("user_logged_in", {
            "user_id": self._user_id,
            "session_id": session_info.session_id,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "login_count": self._login_count,
            "logged_in_at": self._last_login_at.isoformat()
        })
        
        return session_info
    
    def is_active(self) -> bool:
        """Check if user account is active"""
        return self._status == UserStatus.ACTIVE
    
    def can_real_trade(self) -> bool:
        """Check if user can perform real trading"""
        return (
            self.is_active() and 
            self._permissions.can_real_trade and 
            self._verification_tier in [VerificationTier.IDENTITY_VERIFIED, VerificationTier.PREMIUM_VERIFIED]
        )
    
    def get_security_score(self) -> int:
        """Calculate user security score (0-100)"""
        score = 0
        
        # Email verification
        if self._email and self._verification_tier != VerificationTier.UNVERIFIED:
            score += 20
        
        # Two-factor authentication
        if self._security_credentials.has_two_factor_enabled():
            score += 30
        
        # Password age
        if not self._security_credentials.needs_password_reset():
            score += 20
        
        # Wallet connected
        if self._wallet_address:
            score += 15
        
        # Identity verification
        if self._verification_tier in [VerificationTier.IDENTITY_VERIFIED, VerificationTier.PREMIUM_VERIFIED]:
            score += 15
        
        return min(score, 100)
    
    def _get_profile_changes(self, old_profile: UserProfile, new_profile: UserProfile) -> Dict[str, Any]:
        """Get changes between old and new profile"""
        changes = {}
        
        if old_profile.display_name != new_profile.display_name:
            changes["display_name"] = {
                "old": old_profile.display_name,
                "new": new_profile.display_name
            }
        
        if old_profile.bio != new_profile.bio:
            changes["bio"] = {
                "old": old_profile.bio,
                "new": new_profile.bio
            }
        
        if old_profile.trading_experience_level != new_profile.trading_experience_level:
            changes["trading_experience_level"] = {
                "old": old_profile.trading_experience_level,
                "new": new_profile.trading_experience_level
            }
        
        return changes
    
    def _add_domain_event(self, event_type: str, event_data: Dict[str, Any]) -> None:
        """Add domain event for eventual publication"""
        self._domain_events.append(DomainEvent(
            event_type=event_type,
            entity_id=str(self._user_id) if self._user_id else "unknown",
            data=event_data,
            timestamp=datetime.now(timezone.utc)
        ))
    
    def get_domain_events(self) -> List[DomainEvent]:
        """Get all domain events and clear the list"""
        events = self._domain_events.copy()
        self._domain_events.clear()
        return events


@dataclass
class UserSession:
    """
    Entity representing an active user session.
    
    Manages session lifecycle, security validation, and activity tracking.
    """
    session_id: str
    user_id: int
    session_info: SessionInfo
    is_active: bool = True
    last_activity_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    activities: List[str] = field(default_factory=list)
    _domain_events: List[DomainEvent] = field(default_factory=list, init=False)
    
    def __post_init__(self):
        if not self.session_id:
            raise ValueError("Session ID cannot be empty")
        if self.user_id <= 0:
            raise ValueError("User ID must be positive")
    
    def is_expired(self) -> bool:
        """Check if session has expired"""
        return self.session_info.is_expired()
    
    def record_activity(self, activity_type: ActivityType, details: Optional[Dict[str, Any]] = None) -> None:
        """Record user activity in this session"""
        if not self.is_active or self.is_expired():
            raise ValueError("Cannot record activity on inactive or expired session")
        
        self.last_activity_at = datetime.now(timezone.utc)
        activity_record = f"{activity_type.value}:{self.last_activity_at.isoformat()}"
        self.activities.append(activity_record)
        
        # Keep only last 50 activities to prevent memory bloat
        if len(self.activities) > 50:
            self.activities = self.activities[-50:]
        
        self._domain_events.append(DomainEvent(
            event_type="user_activity_recorded",
            entity_id=str(self.user_id),
            data={
                "session_id": self.session_id,
                "activity_type": activity_type.value,
                "details": details or {},
                "timestamp": self.last_activity_at.isoformat()
            }
        ))
    
    def terminate(self, reason: str = "user_logout") -> None:
        """Terminate the session"""
        self.is_active = False
        
        self._domain_events.append(DomainEvent(
            event_type="session_terminated",
            entity_id=str(self.user_id),
            data={
                "session_id": self.session_id,
                "reason": reason,
                "terminated_at": datetime.now(timezone.utc).isoformat(),
                "session_duration_minutes": self.get_session_duration_minutes()
            }
        ))
    
    def get_session_duration_minutes(self) -> int:
        """Get session duration in minutes"""
        duration = self.last_activity_at - self.session_info.created_at
        return int(duration.total_seconds() / 60)
    
    def get_domain_events(self) -> List[DomainEvent]:
        """Get all domain events and clear the list"""
        events = self._domain_events.copy()
        self._domain_events.clear()
        return events


@dataclass  
class UserActivity:
    """
    Entity representing user activity tracking and analytics.
    
    Aggregates user behavior patterns for insights and security monitoring.
    """
    user_id: int
    date: datetime
    login_count: int = 0
    trade_count: int = 0
    profile_updates: int = 0
    session_duration_minutes: int = 0
    unique_ip_addresses: set = field(default_factory=set)
    activity_score: Decimal = field(default_factory=lambda: Decimal('0'))
    _domain_events: List[DomainEvent] = field(default_factory=list, init=False)
    
    def __post_init__(self):
        if self.user_id <= 0:
            raise ValueError("User ID must be positive")
    
    def record_login(self, ip_address: str) -> None:
        """Record user login activity"""
        self.login_count += 1
        self.unique_ip_addresses.add(ip_address)
        self._recalculate_activity_score()
    
    def record_trade(self) -> None:
        """Record trading activity"""
        self.trade_count += 1
        self._recalculate_activity_score()
    
    def record_profile_update(self) -> None:
        """Record profile update activity"""
        self.profile_updates += 1
        self._recalculate_activity_score()
    
    def add_session_duration(self, minutes: int) -> None:
        """Add session duration to total"""
        self.session_duration_minutes += minutes
        self._recalculate_activity_score()
    
    def _recalculate_activity_score(self) -> None:
        """Recalculate user activity score"""
        # Weight different activities
        score = (
            Decimal(self.login_count) * Decimal('1.0') +
            Decimal(self.trade_count) * Decimal('5.0') +
            Decimal(self.profile_updates) * Decimal('2.0') +
            Decimal(self.session_duration_minutes) * Decimal('0.1')
        )
        
        # Bonus for multiple IP addresses (indicates real usage)
        if len(self.unique_ip_addresses) > 1:
            score *= Decimal('1.2')
        
        self.activity_score = score
    
    def get_engagement_level(self) -> str:
        """Get user engagement level based on activity score"""
        if self.activity_score >= Decimal('100'):
            return "high"
        elif self.activity_score >= Decimal('50'):
            return "medium"
        elif self.activity_score >= Decimal('10'):
            return "low"
        else:
            return "inactive"
    
    def get_domain_events(self) -> List[DomainEvent]:
        """Get all domain events and clear the list"""
        events = self._domain_events.copy()
        self._domain_events.clear()
        return events