from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload
import redis.asyncio as redis
from datetime import datetime, timedelta
import json

from models.user import User
from core.cache import CacheKeys, cache_key_builder

class UserRepository:
    def __init__(self, db: AsyncSession, cache: redis.Redis):
        self.db = db
        self.cache = cache
        
    async def create(self, user_data: dict) -> User:
        """Create a new user with automatic caching"""
        user = User(**user_data)
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        
        # Cache the user
        await self._cache_user(user)
        
        return user
    
    async def get_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID with caching"""
        # Check cache first
        cache_key = cache_key_builder(CacheKeys.USER_BY_ID, user_id)
        cached = await self.cache.get(cache_key)
        
        if cached:
            return User.from_json(json.loads(cached))
        
        # Query database
        result = await self.db.execute(
            select(User)
            .where(User.id == user_id)
            .options(selectinload(User.achievements))
        )
        user = result.scalar_one_or_none()
        
        if user:
            await self._cache_user(user)
        
        return user
    
    async def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username with caching"""
        cache_key = cache_key_builder(CacheKeys.USER_BY_USERNAME, username)
        cached = await self.cache.get(cache_key)
        
        if cached:
            user_id = int(cached)
            return await self.get_by_id(user_id)
        
        result = await self.db.execute(
            select(User).where(User.username == username)
        )
        user = result.scalar_one_or_none()
        
        if user:
            await self.cache.setex(cache_key, 3600, str(user.id))
            await self._cache_user(user)
        
        return user
    
    async def update_xp(self, user_id: int, xp_delta: int) -> User:
        """Update user XP with level calculation"""
        user = await self.get_by_id(user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")
        
        # Update XP and calculate new level
        user.xp += xp_delta
        user.level = self._calculate_level(user.xp)
        user.updated_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(user)
        
        # Update cache
        await self._cache_user(user)
        await self._invalidate_leaderboard_cache()
        
        return user
    
    async def get_leaderboard(
        self,
        limit: int = 100,
        offset: int = 0
    ) -> List[dict]:
        """Get leaderboard with caching"""
        cache_key = cache_key_builder(
            CacheKeys.LEADERBOARD,
            f"{limit}:{offset}"
        )
        cached = await self.cache.get(cache_key)
        
        if cached:
            return json.loads(cached)
        
        # Use raw SQL for performance
        query = """
            WITH ranked_users AS (
                SELECT 
                    u.id,
                    u.username,
                    u.xp,
                    u.level,
                    u.avatar_url,
                    RANK() OVER (ORDER BY u.xp DESC) as rank,
                    COUNT(DISTINCT t.id) as total_trades,
                    COALESCE(SUM(t.profit_amount), 0) as total_profit,
                    MAX(t.created_at) as last_trade_at
                FROM users u
                LEFT JOIN trades t ON u.id = t.user_id
                GROUP BY u.id, u.username, u.xp, u.level, u.avatar_url
            )
            SELECT * FROM ranked_users
            ORDER BY rank
            LIMIT :limit OFFSET :offset
        """
        
        result = await self.db.execute(
            text(query),
            {"limit": limit, "offset": offset}
        )
        
        leaderboard = [dict(row) for row in result]
        
        # Cache for 5 minutes
        await self.cache.setex(cache_key, 300, json.dumps(leaderboard))
        
        return leaderboard
    
    async def update_daily_streak(self, user_id: int) -> User:
        """Update user's daily streak"""
        user = await self.get_by_id(user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")
        
        now = datetime.utcnow()
        
        if user.last_active_at:
            days_diff = (now.date() - user.last_active_at.date()).days
            
            if days_diff == 0:
                # Already updated today
                return user
            elif days_diff == 1:
                # Consecutive day
                user.current_streak += 1
                if user.current_streak > user.longest_streak:
                    user.longest_streak = user.current_streak
            else:
                # Streak broken
                user.current_streak = 1
        else:
            # First activity
            user.current_streak = 1
            user.longest_streak = 1
        
        user.last_active_at = now
        
        await self.db.commit()
        await self.db.refresh(user)
        await self._cache_user(user)
        
        return user
    
    async def _cache_user(self, user: User):
        """Cache user data"""
        cache_key = cache_key_builder(CacheKeys.USER_BY_ID, user.id)
        user_data = user.to_dict()
        await self.cache.setex(cache_key, 3600, json.dumps(user_data))
    
    async def _invalidate_leaderboard_cache(self):
        """Invalidate all leaderboard cache entries"""
        pattern = f"{CacheKeys.LEADERBOARD}:*"
        cursor = 0
        
        while True:
            cursor, keys = await self.cache.scan(
                cursor,
                match=pattern,
                count=100
            )
            
            if keys:
                await self.cache.delete(*keys)
            
            if cursor == 0:
                break
    
    @staticmethod
    def _calculate_level(xp: int) -> int:
        """Calculate level based on XP"""
        # Level formula: level = floor(sqrt(xp / 100))
        import math
        return int(math.sqrt(xp / 100))
