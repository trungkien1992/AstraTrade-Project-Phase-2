"""
User Domain Services

Domain services for the User Domain that coordinate between entities and handle
complex business operations that don't naturally fit within a single entity.

Services implemented:
- UserAuthenticationService: Handle login, logout, session management
- UserManagementService: User registration, profile management, verification
- UserSecurityService: Security operations, password management, 2FA
- UserActivityService: Activity tracking and analytics
"""

from datetime import datetime, timezone, timedelta
from decimal import Decimal
from typing import Optional, List, Dict, Any
from abc import ABC, abstractmethod

from .entities import User, UserSession, UserActivity, ActivityType
from .value_objects import (
    Email, Username, WalletAddress, UserPreference, SecurityCredentials,
    UserProfile, SessionInfo, UserPermissions, UserStatus, VerificationTier
)
from ..shared.events import DomainEvent


class UserRepositoryInterface(ABC):
    """Repository interface for User persistence"""
    
    @abstractmethod
    def save(self, user: User) -> User:
        """Save user to persistence layer"""
        pass
    
    @abstractmethod
    def find_by_id(self, user_id: int) -> Optional[User]:
        """Find user by ID"""
        pass
    
    @abstractmethod
    def find_by_username(self, username: str) -> Optional[User]:
        """Find user by username"""
        pass
    
    @abstractmethod
    def find_by_email(self, email: str) -> Optional[User]:
        """Find user by email"""
        pass
    
    @abstractmethod
    def exists_username(self, username: str) -> bool:
        """Check if username exists"""
        pass
    
    @abstractmethod
    def exists_email(self, email: str) -> bool:
        """Check if email exists"""
        pass


class SessionRepositoryInterface(ABC):
    """Repository interface for Session persistence"""
    
    @abstractmethod
    def save(self, session: UserSession) -> UserSession:
        """Save session to persistence layer"""
        pass
    
    @abstractmethod
    def find_by_session_id(self, session_id: str) -> Optional[UserSession]:
        """Find session by session ID"""
        pass
    
    @abstractmethod
    def find_active_sessions_by_user(self, user_id: int) -> List[UserSession]:
        """Find all active sessions for a user"""
        pass
    
    @abstractmethod
    def cleanup_expired_sessions(self) -> int:
        """Remove expired sessions, return count removed"""
        pass


class PasswordServiceInterface(ABC):
    """Service interface for password operations"""
    
    @abstractmethod
    def hash_password(self, plain_password: str) -> str:
        """Hash a plain password"""
        pass
    
    @abstractmethod
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        pass
    
    @abstractmethod
    def generate_salt(self) -> str:
        """Generate password salt"""
        pass


class UserAuthenticationService:
    """
    Domain service for user authentication operations.
    
    Handles login, logout, session management, and authentication validation.
    """
    
    def __init__(
        self,
        user_repository: UserRepositoryInterface,
        session_repository: SessionRepositoryInterface,
        password_service: PasswordServiceInterface
    ):
        self._user_repository = user_repository
        self._session_repository = session_repository
        self._password_service = password_service
    
    def authenticate_user(
        self,
        username_or_email: str,
        password: str,
        ip_address: str,
        user_agent: str
    ) -> Optional[UserSession]:
        """Authenticate user and create session"""
        
        # Find user by username or email
        user = self._find_user_by_credentials(username_or_email)
        if not user:
            return None
        
        # Verify password
        if not self._password_service.verify_password(password, user._security_credentials.hashed_password):
            return None
        
        # Check if user is active
        if not user.is_active():
            return None
        
        # Record login and create session
        session_info = user.record_login(ip_address, user_agent)
        
        # Save user with updated login information
        self._user_repository.save(user)
        
        # Create and save session
        session = UserSession(
            session_id=session_info.session_id,
            user_id=user.user_id,
            session_info=session_info
        )
        
        self._session_repository.save(session)
        
        return session
    
    def logout_user(self, session_id: str) -> bool:
        """Logout user by terminating session"""
        session = self._session_repository.find_by_session_id(session_id)
        if not session or not session.is_active:
            return False
        
        session.terminate("user_logout")
        self._session_repository.save(session)
        
        return True
    
    def validate_session(self, session_id: str) -> Optional[User]:
        """Validate session and return associated user"""
        session = self._session_repository.find_by_session_id(session_id)
        if not session or not session.is_active or session.is_expired():
            return None
        
        # Update last activity
        session.record_activity(ActivityType.LOGIN)
        self._session_repository.save(session)
        
        # Return user
        return self._user_repository.find_by_id(session.user_id)
    
    def terminate_all_user_sessions(self, user_id: int) -> int:
        """Terminate all active sessions for a user"""
        sessions = self._session_repository.find_active_sessions_by_user(user_id)
        
        for session in sessions:
            session.terminate("security_logout")
            self._session_repository.save(session)
        
        return len(sessions)
    
    def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions"""
        return self._session_repository.cleanup_expired_sessions()
    
    def _find_user_by_credentials(self, username_or_email: str) -> Optional[User]:
        """Find user by username or email"""
        # Try username first
        user = self._user_repository.find_by_username(username_or_email)
        if user:
            return user
        
        # Try email if it looks like an email
        if '@' in username_or_email:
            return self._user_repository.find_by_email(username_or_email)
        
        return None


class UserManagementService:
    """
    Domain service for user management operations.
    
    Handles user registration, profile management, and verification processes.
    """
    
    def __init__(
        self,
        user_repository: UserRepositoryInterface,
        password_service: PasswordServiceInterface
    ):
        self._user_repository = user_repository
        self._password_service = password_service
    
    def register_user(
        self,
        username: str,
        password: str,
        email: Optional[str] = None
    ) -> User:
        """Register a new user"""
        
        # Validate username uniqueness
        username_obj = Username(username)
        if self._user_repository.exists_username(username):
            raise ValueError(f"Username '{username}' already exists")
        
        # Validate email uniqueness if provided
        email_obj = None
        if email:
            email_obj = Email(email)
            if self._user_repository.exists_email(email):
                raise ValueError(f"Email '{email}' already registered")
        
        # Create security credentials
        hashed_password = self._password_service.hash_password(password)
        security_credentials = SecurityCredentials(
            hashed_password=hashed_password,
            password_salt=self._password_service.generate_salt(),
            last_password_change=datetime.now(timezone.utc)
        )
        
        # Create user
        user = User(
            username=username_obj,
            security_credentials=security_credentials,
            email=email_obj
        )
        
        # Save user
        saved_user = self._user_repository.save(user)
        
        return saved_user
    
    def update_user_profile(self, user_id: int, profile_data: Dict[str, Any]) -> User:
        """Update user profile"""
        user = self._user_repository.find_by_id(user_id)
        if not user:
            raise ValueError(f"User with ID {user_id} not found")
        
        # Create new profile with updated data
        new_profile = UserProfile(
            display_name=profile_data.get('display_name', user.profile.display_name),
            bio=profile_data.get('bio', user.profile.bio),
            avatar_url=profile_data.get('avatar_url', user.profile.avatar_url),
            location=profile_data.get('location', user.profile.location),
            website=profile_data.get('website', user.profile.website),
            trading_experience_level=profile_data.get('trading_experience_level', user.profile.trading_experience_level)
        )
        
        user.update_profile(new_profile)
        return self._user_repository.save(user)
    
    def connect_wallet_to_user(self, user_id: int, wallet_address: str, network: str = "starknet") -> User:
        """Connect blockchain wallet to user"""
        user = self._user_repository.find_by_id(user_id)
        if not user:
            raise ValueError(f"User with ID {user_id} not found")
        
        wallet = WalletAddress(wallet_address, network)
        user.connect_wallet(wallet)
        
        return self._user_repository.save(user)
    
    def update_user_email(self, user_id: int, new_email: str) -> User:
        """Update user email address"""
        user = self._user_repository.find_by_id(user_id)
        if not user:
            raise ValueError(f"User with ID {user_id} not found")
        
        # Check email uniqueness
        email_obj = Email(new_email)
        if self._user_repository.exists_email(new_email):
            raise ValueError(f"Email '{new_email}' already registered")
        
        user.update_email(email_obj)
        return self._user_repository.save(user)
    
    def verify_user_tier(self, user_id: int, tier: str) -> User:
        """Update user verification tier"""
        user = self._user_repository.find_by_id(user_id)
        if not user:
            raise ValueError(f"User with ID {user_id} not found")
        
        verification_tier = VerificationTier(tier)
        user.verify_tier(verification_tier)
        
        return self._user_repository.save(user)
    
    def set_user_preference(
        self,
        user_id: int,
        preference_type: str,
        key: str,
        value: str,
        is_encrypted: bool = False
    ) -> User:
        """Set user preference"""
        user = self._user_repository.find_by_id(user_id)
        if not user:
            raise ValueError(f"User with ID {user_id} not found")
        
        from .value_objects import PreferenceType
        pref_type = PreferenceType(preference_type)
        preference = UserPreference(pref_type, key, value, is_encrypted)
        
        user.set_preference(preference)
        return self._user_repository.save(user)


class UserSecurityService:
    """
    Domain service for user security operations.
    
    Handles password changes, two-factor authentication, and security monitoring.
    """
    
    def __init__(
        self,
        user_repository: UserRepositoryInterface,
        session_repository: SessionRepositoryInterface,
        password_service: PasswordServiceInterface
    ):
        self._user_repository = user_repository
        self._session_repository = session_repository
        self._password_service = password_service
    
    def change_user_password(self, user_id: int, current_password: str, new_password: str) -> User:
        """Change user password with validation"""
        user = self._user_repository.find_by_id(user_id)
        if not user:
            raise ValueError(f"User with ID {user_id} not found")
        
        # Verify current password
        if not self._password_service.verify_password(current_password, user._security_credentials.hashed_password):
            raise ValueError("Current password is incorrect")
        
        # Hash new password
        new_password_hash = self._password_service.hash_password(new_password)
        
        # Update password
        user.change_password(new_password_hash, current_password)
        
        # Terminate all other sessions for security
        self.terminate_all_user_sessions_except_current(user_id, None)
        
        return self._user_repository.save(user)
    
    def suspend_user_account(self, user_id: int, reason: str) -> User:
        """Suspend user account for security reasons"""
        user = self._user_repository.find_by_id(user_id)
        if not user:
            raise ValueError(f"User with ID {user_id} not found")
        
        user.suspend_account(reason)
        
        # Terminate all active sessions
        self.terminate_all_user_sessions_except_current(user_id, None)
        
        return self._user_repository.save(user)
    
    def reactivate_user_account(self, user_id: int) -> User:
        """Reactivate suspended user account"""
        user = self._user_repository.find_by_id(user_id)
        if not user:
            raise ValueError(f"User with ID {user_id} not found")
        
        user.reactivate_account()
        return self._user_repository.save(user)
    
    def get_user_security_score(self, user_id: int) -> int:
        """Get user security score"""
        user = self._user_repository.find_by_id(user_id)
        if not user:
            raise ValueError(f"User with ID {user_id} not found")
        
        return user.get_security_score()
    
    def terminate_all_user_sessions_except_current(self, user_id: int, current_session_id: Optional[str]) -> int:
        """Terminate all user sessions except the current one"""
        sessions = self._session_repository.find_active_sessions_by_user(user_id)
        terminated_count = 0
        
        for session in sessions:
            if session.session_id != current_session_id:
                session.terminate("security_logout")
                self._session_repository.save(session)
                terminated_count += 1
        
        return terminated_count


class UserActivityService:
    """
    Domain service for user activity tracking and analytics.
    
    Tracks user behavior patterns for insights and engagement metrics.
    """
    
    def __init__(self, user_repository: UserRepositoryInterface):
        self._user_repository = user_repository
        self._daily_activities: Dict[str, UserActivity] = {}  # In-memory cache
    
    def record_user_activity(
        self,
        user_id: int,
        activity_type: ActivityType,
        session_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """Record user activity"""
        today = datetime.now(timezone.utc).date()
        activity_key = f"{user_id}:{today}"
        
        # Get or create daily activity
        if activity_key not in self._daily_activities:
            self._daily_activities[activity_key] = UserActivity(
                user_id=user_id,
                date=datetime.combine(today, datetime.min.time().replace(tzinfo=timezone.utc))
            )
        
        activity = self._daily_activities[activity_key]
        
        # Record specific activity
        if activity_type == ActivityType.LOGIN:
            ip_address = details.get('ip_address', '0.0.0.0') if details else '0.0.0.0'
            activity.record_login(ip_address)
        elif activity_type == ActivityType.TRADE_EXECUTED:
            activity.record_trade()
        elif activity_type == ActivityType.PROFILE_UPDATED:
            activity.record_profile_update()
    
    def get_user_engagement_level(self, user_id: int) -> str:
        """Get user engagement level for today"""
        today = datetime.now(timezone.utc).date()
        activity_key = f"{user_id}:{today}"
        
        if activity_key in self._daily_activities:
            return self._daily_activities[activity_key].get_engagement_level()
        
        return "inactive"
    
    def get_user_activity_summary(self, user_id: int, days: int = 7) -> Dict[str, Any]:
        """Get user activity summary for specified number of days"""
        summary = {
            "total_logins": 0,
            "total_trades": 0,
            "total_session_minutes": 0,
            "unique_days_active": 0,
            "average_engagement": "inactive"
        }
        
        engagement_levels = []
        current_date = datetime.now(timezone.utc).date()
        
        for i in range(days):
            check_date = current_date - timedelta(days=i)
            activity_key = f"{user_id}:{check_date}"
            
            if activity_key in self._daily_activities:
                activity = self._daily_activities[activity_key]
                summary["total_logins"] += activity.login_count
                summary["total_trades"] += activity.trade_count
                summary["total_session_minutes"] += activity.session_duration_minutes
                summary["unique_days_active"] += 1
                engagement_levels.append(activity.get_engagement_level())
        
        # Calculate average engagement
        if engagement_levels:
            engagement_scores = {
                "inactive": 0,
                "low": 1,
                "medium": 2,
                "high": 3
            }
            avg_score = sum(engagement_scores[level] for level in engagement_levels) / len(engagement_levels)
            
            if avg_score >= 2.5:
                summary["average_engagement"] = "high"
            elif avg_score >= 1.5:
                summary["average_engagement"] = "medium"
            elif avg_score >= 0.5:
                summary["average_engagement"] = "low"
        
        return summary