import asyncio
from typing import List, Dict, Optional
import json
import redis

class LeaderboardManager:
    """
    Manages tournament leaderboards using Redis sorted sets.
    Provides atomic updates and real-time queries.
    """
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.update_lua_script = """
        local key = KEYS[1]
        local member = ARGV[1]
        local score = ARGV[2]
        local old_score = redis.call('ZSCORE', key, member)
        local new_score = redis.call('ZADD', key, score, member)
        
        -- Publish position change event
        local new_rank = redis.call('ZREVRANK', key, member)
        local event_data = cjson.encode({
            user_id = member,
            score = tonumber(score),
            rank = new_rank + 1,
            old_score = old_score and tonumber(old_score) or nil
        })
        redis.call('PUBLISH', 'leaderboard:updates', event_data)
        
        return {new_score, new_rank + 1}
        """
        
        # Register the Lua script
        self.update_script_sha = self.redis.script_load(self.update_lua_script)
        
    async def update_score(self, tournament_id: str, user_id: str, score: float):
        """Atomically update user score and publish change event"""
        leaderboard_key = f"tournament:{tournament_id}:leaderboard"
        
        try:
            # Execute Lua script for atomic update
            result = self.redis.evalsha(
                self.update_script_sha,
                1,  # Number of keys
                leaderboard_key,  # Key
                user_id,  # Member
                score   # Score
            )
            return result
        except redis.exceptions.NoScriptError:
            # Script not loaded, reload and retry
            self.update_script_sha = self.redis.script_load(self.update_lua_script)
            result = self.redis.evalsha(
                self.update_script_sha,
                1,
                leaderboard_key,
                user_id,
                score
            )
            return result
    
    async def get_leaderboard(self, tournament_id: str, start: int = 0, end: int = 99) -> List[Dict]:
        """Get leaderboard with ranks, scores, and user details"""
        leaderboard_key = f"tournament:{tournament_id}:leaderboard"
        
        # Get top users with scores
        raw_leaderboard = self.redis.zrevrange(
            leaderboard_key, start, end, withscores=True
        )
        
        # Enrich with user details
        leaderboard = []
        for rank, (user_id, score) in enumerate(raw_leaderboard, start=start+1):
            user_data = await self.get_user_display_data(user_id)
            leaderboard.append({
                'rank': rank,
                'user_id': user_id,
                'username': user_data['username'],
                'avatar': user_data['avatar'],
                'score': float(score),
                'is_ai': user_id.startswith('ai:'),
                'league': user_data.get('league', 'Cadet')
            })
            
        return leaderboard
    
    async def get_user_rank(self, tournament_id: str, user_id: str) -> Optional[int]:
        """Get specific user's rank in tournament"""
        leaderboard_key = f"tournament:{tournament_id}:leaderboard"
        rank = self.redis.zrevrank(leaderboard_key, user_id)
        
        return rank + 1 if rank is not None else None
    
    async def get_user_score(self, tournament_id: str, user_id: str) -> Optional[float]:
        """Get specific user's score in tournament"""
        leaderboard_key = f"tournament:{tournament_id}:leaderboard"
        score = self.redis.zscore(leaderboard_key, user_id)
        
        return float(score) if score is not None else None
    
    async def get_nearby_competitors(self, tournament_id: str, user_id: str, radius: int = 5):
        """Get users ranked near the specified user"""
        rank = await self.get_user_rank(tournament_id, user_id)
        if not rank:
            return []
            
        start = max(0, rank - radius - 1)
        end = rank + radius - 1
        
        return await self.get_leaderboard(tournament_id, start, end)
    
    async def get_top_performers(self, tournament_id: str, count: int = 10) -> List[Dict]:
        """Get top performers in the tournament"""
        return await self.get_leaderboard(tournament_id, 0, count - 1)
    
    async def get_leaderboard_size(self, tournament_id: str) -> int:
        """Get total number of participants in tournament"""
        leaderboard_key = f"tournament:{tournament_id}:leaderboard"
        return self.redis.zcard(leaderboard_key)
    
    async def get_score_distribution(self, tournament_id: str) -> Dict[str, float]:
        """Get statistical distribution of scores"""
        leaderboard_key = f"tournament:{tournament_id}:leaderboard"
        
        # Get all scores
        all_scores = [float(score) for _, score in self.redis.zrange(leaderboard_key, 0, -1, withscores=True)]
        
        if not all_scores:
            return {
                'count': 0,
                'min': 0,
                'max': 0,
                'average': 0,
                'median': 0
            }
        
        all_scores.sort()
        count = len(all_scores)
        
        return {
            'count': count,
            'min': all_scores[0],
            'max': all_scores[-1],
            'average': sum(all_scores) / count,
            'median': all_scores[count // 2] if count % 2 == 1 else (all_scores[count // 2 - 1] + all_scores[count // 2]) / 2
        }
    
    async def get_user_display_data(self, user_id: str) -> Dict[str, str]:
        """Get user display information (username, avatar, etc.)"""
        if user_id.startswith('ai:'):
            # AI trader display data
            ai_name = user_id.replace('ai:', '').replace('_', ' ').title()
            return {
                'username': ai_name,
                'avatar': f'ai_avatars/{user_id.replace("ai:", "")}.png',
                'league': 'AI Legends'
            }
        else:
            # Human user display data
            # In production, this would fetch from user service
            user_key = f"user:{user_id}:profile"
            user_data = self.redis.hgetall(user_key)
            
            if user_data:
                return {
                    'username': user_data.get('username', f'User_{user_id[-6:]}'),
                    'avatar': user_data.get('avatar', 'default_avatar.png'),
                    'league': user_data.get('league', 'Cadet')
                }
            else:
                # Fallback for users not in cache
                return {
                    'username': f'User_{user_id[-6:]}',
                    'avatar': 'default_avatar.png',
                    'league': 'Cadet'
                }
    
    async def get_rank_changes(self, tournament_id: str, user_id: str, timeframe_minutes: int = 60) -> Dict:
        """Get user's rank changes over specified timeframe"""
        # This would typically be implemented with time-series data
        # For now, return a simple structure
        current_rank = await self.get_user_rank(tournament_id, user_id)
        current_score = await self.get_user_score(tournament_id, user_id)
        
        return {
            'current_rank': current_rank,
            'current_score': current_score,
            'rank_change': 0,  # Would be calculated from historical data
            'score_change': 0.0,  # Would be calculated from historical data
            'trend': 'stable'  # Would be 'rising', 'falling', or 'stable'
        }
    
    async def archive_tournament_leaderboard(self, tournament_id: str) -> bool:
        """Archive tournament leaderboard for historical reference"""
        try:
            leaderboard_key = f"tournament:{tournament_id}:leaderboard"
            archive_key = f"tournament:{tournament_id}:leaderboard:archived"
            
            # Copy leaderboard to archive
            leaderboard_data = self.redis.zrange(leaderboard_key, 0, -1, withscores=True)
            
            if leaderboard_data:
                # Store as JSON for easier querying later
                archive_data = {
                    'tournament_id': tournament_id,
                    'archived_at': asyncio.get_event_loop().time(),
                    'leaderboard': [{'user_id': user_id, 'score': float(score)} for user_id, score in leaderboard_data]
                }
                
                self.redis.set(archive_key, json.dumps(archive_data))
                
                # Set expiry for archive (e.g., 30 days)
                self.redis.expire(archive_key, 30 * 24 * 60 * 60)
                
            return True
        except Exception as e:
            print(f"Error archiving tournament {tournament_id}: {e}")
            return False
    
    async def get_user_tournament_history(self, user_id: str, limit: int = 10) -> List[Dict]:
        """Get user's historical tournament performance"""
        # This would query archived tournaments
        # For now, return empty list
        return []
    
    async def cleanup_expired_tournaments(self, days_old: int = 7) -> int:
        """Clean up old tournament leaderboards"""
        import time
        from datetime import datetime, timedelta
        
        cutoff_date = datetime.now() - timedelta(days=days_old)
        cutoff_timestamp = cutoff_date.timestamp()
        
        # Find tournament keys older than cutoff
        pattern = "tournament:daily:*:leaderboard"
        keys = self.redis.keys(pattern)
        
        cleaned_count = 0
        for key in keys:
            # Extract date from tournament key
            try:
                # tournament:daily:YYYY-MM-DD:leaderboard
                date_str = key.decode('utf-8').split(':')[2]
                tournament_date = datetime.strptime(date_str, '%Y-%m-%d')
                
                if tournament_date.timestamp() < cutoff_timestamp:
                    # Archive before deleting
                    tournament_id = f"daily:{date_str}"
                    await self.archive_tournament_leaderboard(tournament_id)
                    
                    # Delete the leaderboard
                    self.redis.delete(key)
                    cleaned_count += 1
                    
            except (ValueError, IndexError):
                # Invalid key format, skip
                continue
        
        return cleaned_count
    
    def get_leaderboard_stats(self, tournament_id: str) -> Dict:
        """Get comprehensive leaderboard statistics"""
        leaderboard_key = f"tournament:{tournament_id}:leaderboard"
        
        total_users = self.redis.zcard(leaderboard_key)
        if total_users == 0:
            return {'total_users': 0, 'active_users': 0, 'ai_users': 0}
        
        # Count AI vs human users
        all_members = self.redis.zrange(leaderboard_key, 0, -1)
        ai_users = sum(1 for member in all_members if member.decode('utf-8').startswith('ai:'))
        human_users = total_users - ai_users
        
        return {
            'total_users': total_users,
            'human_users': human_users,
            'ai_users': ai_users,
            'ai_percentage': (ai_users / total_users) * 100 if total_users > 0 else 0
        }