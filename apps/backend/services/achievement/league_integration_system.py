#!/usr/bin/env python3
"""
League Integration System for Achievements

Integrates the achievement system with the tournament league progression
from Week 1, creating achievement-driven advancement through the cosmic
trading leagues with scaled rewards and challenges.

League Progression:
- Cadet League (Novice traders)
- Rising Star League (Intermediate traders)  
- Champion League (Advanced traders)
- Elite League (Expert traders)
- Galactic Master League (Elite masters)

Integration Features:
- Achievement-based league advancement
- League-specific achievement scaling
- Season-based progression tracking
- AI opponent difficulty scaling per league
- Exclusive league achievement categories
- Cross-league achievement comparisons
"""

import asyncio
import time
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Set, Any
from dataclasses import dataclass, field
from enum import Enum
import redis.asyncio as redis

from .research_driven_categories import (
    ResearchDrivenAchievements, AchievementDefinition, 
    AchievementCategory, SkillLevel
)
from .dopamine_timing_engine import AchievementPriority


logger = logging.getLogger(__name__)


class LeagueLevel(Enum):
    """Cosmic trading league levels"""
    CADET = 1                    # Entry level - learning basics
    RISING_STAR = 2             # Intermediate - building skills  
    CHAMPION = 3                # Advanced - proven competence
    ELITE = 4                   # Expert - mastery demonstrated
    GALACTIC_MASTER = 5         # Legendary - teaching others


class LeagueStatus(Enum):
    """Player status within league"""
    ACTIVE = "active"           # Currently competing in league
    PROMOTION_ELIGIBLE = "promotion_eligible"    # Can advance to next league
    DEMOTION_WARNING = "demotion_warning"       # Risk of demotion
    DEMOTED = "demoted"         # Demoted to lower league
    PROMOTED = "promoted"       # Advanced to higher league
    LOCKED = "locked"           # Temporarily locked from league changes


@dataclass
class LeagueRequirements:
    """Requirements for league advancement and maintenance"""
    league: LeagueLevel
    
    # Achievement requirements
    required_achievements: List[str] = field(default_factory=list)
    minimum_achievement_points: int = 0
    educational_achievements_required: int = 0
    risk_management_achievements_required: int = 0
    
    # Performance requirements
    minimum_tournaments_participated: int = 0
    minimum_win_rate: float = 0.0
    minimum_consistency_score: float = 0.0
    maximum_risk_violations: int = 0
    
    # Time requirements
    minimum_days_in_previous_league: int = 7
    minimum_active_days: int = 5
    
    # Social requirements (for higher leagues)
    minimum_mentoring_sessions: int = 0
    minimum_community_contributions: int = 0


@dataclass
class LeagueProgression:
    """User's progression through leagues"""
    user_id: str
    current_league: LeagueLevel
    league_status: LeagueStatus
    
    # Progression tracking
    league_entry_date: datetime
    days_in_current_league: int = 0
    league_points: int = 0
    season_achievements: int = 0
    
    # Performance metrics
    tournament_participation_rate: float = 0.0
    average_tournament_rank: float = 0.0
    win_rate: float = 0.0
    consistency_score: float = 0.0
    risk_violations_count: int = 0
    
    # Achievement progress
    completed_achievements: Set[str] = field(default_factory=set)
    educational_achievement_count: int = 0
    risk_management_achievement_count: int = 0
    performance_achievement_count: int = 0
    social_achievement_count: int = 0
    
    # Next league requirements
    promotion_progress: Dict[str, float] = field(default_factory=dict)  # requirement -> progress %
    
    @property
    def league_name(self) -> str:
        """Get cosmic name for current league"""
        league_names = {
            LeagueLevel.CADET: "Cadet League",
            LeagueLevel.RISING_STAR: "Rising Star League", 
            LeagueLevel.CHAMPION: "Champion League",
            LeagueLevel.ELITE: "Elite League",
            LeagueLevel.GALACTIC_MASTER: "Galactic Master League"
        }
        return league_names[self.current_league]
    
    @property
    def next_league_name(self) -> Optional[str]:
        """Get name of next league"""
        if self.current_league.value >= LeagueLevel.GALACTIC_MASTER.value:
            return None
        
        next_league = LeagueLevel(self.current_league.value + 1)
        league_names = {
            LeagueLevel.CADET: "Cadet League",
            LeagueLevel.RISING_STAR: "Rising Star League",
            LeagueLevel.CHAMPION: "Champion League", 
            LeagueLevel.ELITE: "Elite League",
            LeagueLevel.GALACTIC_MASTER: "Galactic Master League"
        }
        return league_names[next_league]


class LeagueAchievementScaler:
    """Scales achievement rewards and difficulty based on league level"""
    
    def __init__(self):
        # League-based scaling factors
        self.league_scaling = {
            LeagueLevel.CADET: {
                "xp_multiplier": 1.0,
                "difficulty_modifier": 0.8,  # 20% easier
                "ai_opponent_level": "novice",
                "tournament_competition": "relaxed"
            },
            LeagueLevel.RISING_STAR: {
                "xp_multiplier": 1.2,
                "difficulty_modifier": 1.0,  # Standard difficulty
                "ai_opponent_level": "intermediate",
                "tournament_competition": "competitive"
            },
            LeagueLevel.CHAMPION: {
                "xp_multiplier": 1.5,
                "difficulty_modifier": 1.2,  # 20% harder
                "ai_opponent_level": "advanced",
                "tournament_competition": "intense"
            },
            LeagueLevel.ELITE: {
                "xp_multiplier": 1.8,
                "difficulty_modifier": 1.5,  # 50% harder
                "ai_opponent_level": "expert",
                "tournament_competition": "elite"
            },
            LeagueLevel.GALACTIC_MASTER: {
                "xp_multiplier": 2.5,
                "difficulty_modifier": 2.0,  # 100% harder
                "ai_opponent_level": "master",
                "tournament_competition": "legendary"
            }
        }
    
    def scale_achievement_reward(
        self,
        base_xp: int,
        league: LeagueLevel,
        achievement_category: AchievementCategory
    ) -> int:
        """Scale achievement XP reward based on league"""
        
        scaling_factors = self.league_scaling[league]
        base_multiplier = scaling_factors["xp_multiplier"]
        
        # Additional scaling for different achievement types
        category_multipliers = {
            AchievementCategory.EDUCATIONAL: 1.2,    # Education always valued highly
            AchievementCategory.RISK_MANAGEMENT: 1.1,  # Safety slightly boosted
            AchievementCategory.PERFORMANCE: 1.0,    # Standard performance rewards
            AchievementCategory.SOCIAL: 1.3         # Social contributions highly valued
        }
        
        final_multiplier = base_multiplier * category_multipliers[achievement_category]
        return int(base_xp * final_multiplier)
    
    def get_ai_opponents_for_league(self, league: LeagueLevel) -> List[str]:
        """Get appropriate AI opponents for league level"""
        
        # AI opponents from Week 1 system, filtered by league
        league_ai_opponents = {
            LeagueLevel.CADET: [
                "ai:commander_luna",     # Conservative, good for learning
                "ai:cadet_zara",         # Beginner-friendly AI
                "ai:mentor_kai",         # Teaching-focused AI
            ],
            LeagueLevel.RISING_STAR: [
                "ai:captain_vega",       # Balanced approach
                "ai:navigator_orion",    # Intermediate challenge
                "ai:scout_nova",         # Pattern recognition focus
            ],
            LeagueLevel.CHAMPION: [
                "ai:admiral_nexus",      # High-frequency trading
                "ai:strategist_cosmos",  # Advanced strategies
                "ai:warrior_phoenix",    # Aggressive but calculated
            ],
            LeagueLevel.ELITE: [
                "ai:grandmaster_stellan", # Legendary skill level
                "ai:oracle_andromeda",    # Market prediction expert
                "ai:titan_quasar",        # Maximum challenge
            ],
            LeagueLevel.GALACTIC_MASTER: [
                "ai:cosmic_entity_alpha",  # Ultimate challenge
                "ai:universe_guardian",     # Teaching master level
                "ai:eternal_trader",        # Perfection benchmark
            ]
        }
        
        return league_ai_opponents[league]


class LeagueIntegrationSystem:
    """
    Integrates achievement system with league progression,
    creating achievement-driven advancement through cosmic trading leagues.
    """
    
    def __init__(
        self,
        redis_client: redis.Redis,
        achievement_system: ResearchDrivenAchievements
    ):
        self.redis = redis_client
        self.achievement_system = achievement_system
        self.scaler = LeagueAchievementScaler()
        
        # Redis keys
        self.league_progression_key = "league_progression"
        self.league_requirements_key = "league_requirements"
        self.league_seasons_key = "league_seasons"
        
        # Initialize league requirements
        self.league_requirements = self._initialize_league_requirements()
    
    def _initialize_league_requirements(self) -> Dict[LeagueLevel, LeagueRequirements]:
        """Initialize requirements for each league level"""
        
        requirements = {}
        
        # CADET LEAGUE - Entry level, focus on learning
        requirements[LeagueLevel.CADET] = LeagueRequirements(
            league=LeagueLevel.CADET,
            required_achievements=[],  # No requirements to enter
            minimum_achievement_points=0,
            educational_achievements_required=0,
            risk_management_achievements_required=0,
            minimum_tournaments_participated=0,
            minimum_active_days=0
        )
        
        # RISING STAR LEAGUE - Basic competency demonstrated
        requirements[LeagueLevel.RISING_STAR] = LeagueRequirements(
            league=LeagueLevel.RISING_STAR,
            required_achievements=[
                "stellar_academy_graduate",
                "chart_navigator", 
                "stop_loss_guardian"
            ],
            minimum_achievement_points=500,
            educational_achievements_required=3,
            risk_management_achievements_required=2,
            minimum_tournaments_participated=10,
            minimum_win_rate=0.3,  # 30% win rate
            minimum_consistency_score=60,
            minimum_days_in_previous_league=7,
            minimum_active_days=5
        )
        
        # CHAMPION LEAGUE - Intermediate mastery
        requirements[LeagueLevel.CHAMPION] = LeagueRequirements(
            league=LeagueLevel.CHAMPION,
            required_achievements=[
                "market_psychology_scholar",
                "fundamental_analyst",
                "position_size_master",
                "consistent_trader"
            ],
            minimum_achievement_points=1500,
            educational_achievements_required=6,
            risk_management_achievements_required=4,
            minimum_tournaments_participated=25,
            minimum_win_rate=0.45,  # 45% win rate
            minimum_consistency_score=70,
            maximum_risk_violations=2,
            minimum_days_in_previous_league=14,
            minimum_active_days=10
        )
        
        # ELITE LEAGUE - Advanced expertise
        requirements[LeagueLevel.ELITE] = LeagueRequirements(
            league=LeagueLevel.ELITE,
            required_achievements=[
                "strategy_architect",
                "drawdown_recovery_expert", 
                "patience_virtuoso",
                "adaptation_specialist"
            ],
            minimum_achievement_points=3000,
            educational_achievements_required=10,
            risk_management_achievements_required=6,
            minimum_tournaments_participated=50,
            minimum_win_rate=0.55,  # 55% win rate
            minimum_consistency_score=80,
            maximum_risk_violations=1,
            minimum_days_in_previous_league=21,
            minimum_active_days=15,
            minimum_community_contributions=5
        )
        
        # GALACTIC MASTER LEAGUE - Teaching and mentorship
        requirements[LeagueLevel.GALACTIC_MASTER] = LeagueRequirements(
            league=LeagueLevel.GALACTIC_MASTER,
            required_achievements=[
                "galactic_mentor",
                "portfolio_optimizer",
                "knowledge_sharer",
                "community_supporter"
            ],
            minimum_achievement_points=5000,
            educational_achievements_required=15,
            risk_management_achievements_required=8,
            minimum_tournaments_participated=100,
            minimum_win_rate=0.65,  # 65% win rate
            minimum_consistency_score=85,
            maximum_risk_violations=0,
            minimum_days_in_previous_league=30,
            minimum_active_days=20,
            minimum_mentoring_sessions=10,
            minimum_community_contributions=15
        )
        
        return requirements
    
    async def get_user_league_progression(self, user_id: str) -> LeagueProgression:
        """Get user's current league progression status"""
        
        progression_key = f"{self.league_progression_key}:{user_id}"
        progression_data = await self.redis.hgetall(progression_key)
        
        if not progression_data:
            # Initialize new user in Cadet League
            progression = LeagueProgression(
                user_id=user_id,
                current_league=LeagueLevel.CADET,
                league_status=LeagueStatus.ACTIVE,
                league_entry_date=datetime.now()
            )
            
            await self._store_league_progression(progression)
            return progression
        
        # Deserialize stored progression
        progression = LeagueProgression(
            user_id=user_id,
            current_league=LeagueLevel(int(progression_data["current_league"])),
            league_status=LeagueStatus(progression_data["league_status"]),
            league_entry_date=datetime.fromisoformat(progression_data["league_entry_date"]),
            days_in_current_league=int(progression_data.get("days_in_current_league", "0")),
            league_points=int(progression_data.get("league_points", "0")),
            season_achievements=int(progression_data.get("season_achievements", "0")),
            tournament_participation_rate=float(progression_data.get("tournament_participation_rate", "0")),
            average_tournament_rank=float(progression_data.get("average_tournament_rank", "0")),
            win_rate=float(progression_data.get("win_rate", "0")),
            consistency_score=float(progression_data.get("consistency_score", "0")),
            risk_violations_count=int(progression_data.get("risk_violations_count", "0")),
            completed_achievements=set(json.loads(progression_data.get("completed_achievements", "[]"))),
            educational_achievement_count=int(progression_data.get("educational_achievement_count", "0")),
            risk_management_achievement_count=int(progression_data.get("risk_management_achievement_count", "0")),
            performance_achievement_count=int(progression_data.get("performance_achievement_count", "0")),
            social_achievement_count=int(progression_data.get("social_achievement_count", "0")),
            promotion_progress=json.loads(progression_data.get("promotion_progress", "{}"))
        )
        
        return progression
    
    async def process_achievement_for_league(
        self,
        user_id: str,
        achievement_id: str,
        achievement_data: Dict
    ) -> Dict[str, Any]:
        """Process achievement unlock and update league progression"""
        
        # Get achievement definition
        achievement_def = self.achievement_system.get_achievement_by_id(achievement_id)
        if not achievement_def:
            return {"error": "Achievement not found"}
        
        # Get user's league progression
        progression = await self.get_user_league_progression(user_id)
        
        # Add achievement to completed set
        progression.completed_achievements.add(achievement_id)
        progression.season_achievements += 1
        
        # Update category counts
        if achievement_def.category == AchievementCategory.EDUCATIONAL:
            progression.educational_achievement_count += 1
        elif achievement_def.category == AchievementCategory.RISK_MANAGEMENT:
            progression.risk_management_achievement_count += 1
        elif achievement_def.category == AchievementCategory.PERFORMANCE:
            progression.performance_achievement_count += 1
        elif achievement_def.category == AchievementCategory.SOCIAL:
            progression.social_achievement_count += 1
        
        # Calculate scaled league points
        scaled_xp = self.scaler.scale_achievement_reward(
            achievement_def.xp_reward,
            progression.current_league,
            achievement_def.category
        )
        progression.league_points += scaled_xp
        
        # Check for league advancement eligibility
        promotion_result = await self._check_promotion_eligibility(progression)
        
        # Update progression
        await self._store_league_progression(progression)
        
        result = {
            "achievement_processed": True,
            "scaled_xp_reward": scaled_xp,
            "new_league_points": progression.league_points,
            "current_league": progression.league_name,
            "league_status": progression.league_status.value
        }
        
        # Add promotion information if eligible
        if promotion_result["eligible"]:
            result.update(promotion_result)
        
        return result
    
    async def _check_promotion_eligibility(self, progression: LeagueProgression) -> Dict[str, Any]:
        """Check if user is eligible for league promotion"""
        
        current_league = progression.current_league
        
        # Can't promote from highest league
        if current_league == LeagueLevel.GALACTIC_MASTER:
            return {"eligible": False, "reason": "Already at highest league"}
        
        # Get requirements for next league
        next_league = LeagueLevel(current_league.value + 1)
        requirements = self.league_requirements[next_league]
        
        # Check all requirements
        eligibility_check = {
            "eligible": True,
            "requirements_met": {},
            "requirements_missing": {},
            "overall_progress": 0.0
        }
        
        total_requirements = 0
        met_requirements = 0
        
        # Check required achievements
        for required_achievement in requirements.required_achievements:
            total_requirements += 1
            if required_achievement in progression.completed_achievements:
                met_requirements += 1
                eligibility_check["requirements_met"]["achievement_" + required_achievement] = True
            else:
                eligibility_check["eligible"] = False
                eligibility_check["requirements_missing"]["achievement_" + required_achievement] = True
        
        # Check achievement counts by category
        category_checks = [
            ("educational_achievements", progression.educational_achievement_count, requirements.educational_achievements_required),
            ("risk_management_achievements", progression.risk_management_achievement_count, requirements.risk_management_achievements_required)
        ]
        
        for check_name, current_count, required_count in category_checks:
            total_requirements += 1
            if current_count >= required_count:
                met_requirements += 1
                eligibility_check["requirements_met"][check_name] = f"{current_count}/{required_count}"
            else:
                eligibility_check["eligible"] = False
                eligibility_check["requirements_missing"][check_name] = f"{current_count}/{required_count}"
        
        # Check performance metrics
        performance_checks = [
            ("minimum_win_rate", progression.win_rate, requirements.minimum_win_rate),
            ("minimum_consistency_score", progression.consistency_score, requirements.minimum_consistency_score),
            ("minimum_days_in_league", progression.days_in_current_league, requirements.minimum_days_in_previous_league)
        ]
        
        for check_name, current_value, required_value in performance_checks:
            if required_value > 0:  # Only check if requirement is set
                total_requirements += 1
                if current_value >= required_value:
                    met_requirements += 1
                    eligibility_check["requirements_met"][check_name] = f"{current_value:.2f}>={required_value:.2f}"
                else:
                    eligibility_check["eligible"] = False
                    eligibility_check["requirements_missing"][check_name] = f"{current_value:.2f}<{required_value:.2f}"
        
        # Calculate overall progress
        if total_requirements > 0:
            eligibility_check["overall_progress"] = met_requirements / total_requirements
        
        # Update progression status based on eligibility
        if eligibility_check["eligible"]:
            progression.league_status = LeagueStatus.PROMOTION_ELIGIBLE
            eligibility_check["next_league"] = LeagueLevel(current_league.value + 1).name
        else:
            progression.league_status = LeagueStatus.ACTIVE
        
        return eligibility_check
    
    async def promote_user_to_next_league(self, user_id: str) -> Dict[str, Any]:
        """Promote user to the next league level"""
        
        progression = await self.get_user_league_progression(user_id)
        
        if progression.league_status != LeagueStatus.PROMOTION_ELIGIBLE:
            return {
                "success": False,
                "error": "User not eligible for promotion",
                "current_status": progression.league_status.value
            }
        
        # Get current and next league
        current_league = progression.current_league
        next_league = LeagueLevel(current_league.value + 1)
        
        # Update progression
        progression.current_league = next_league
        progression.league_status = LeagueStatus.PROMOTED
        progression.league_entry_date = datetime.now()
        progression.days_in_current_league = 0
        
        # Reset some metrics for new league
        progression.season_achievements = 0
        progression.promotion_progress = {}
        
        # Store updated progression
        await self._store_league_progression(progression)
        
        # Log promotion event
        promotion_event = {
            "user_id": user_id,
            "promoted_from": current_league.name,
            "promoted_to": next_league.name,
            "promotion_timestamp": datetime.now().isoformat(),
            "achievement_count": len(progression.completed_achievements),
            "league_points": progression.league_points
        }
        
        promotion_log_key = f"league_promotions:{user_id}"
        await self.redis.lpush(promotion_log_key, json.dumps(promotion_event))
        await self.redis.expire(promotion_log_key, 86400 * 365)  # Keep for 1 year
        
        logger.info(f"User {user_id} promoted from {current_league.name} to {next_league.name}")
        
        return {
            "success": True,
            "promoted_from": current_league.name,
            "promoted_to": next_league.name,
            "new_league_level": next_league.value,
            "ai_opponents": self.scaler.get_ai_opponents_for_league(next_league),
            "xp_multiplier": self.scaler.league_scaling[next_league]["xp_multiplier"]
        }
    
    async def get_league_leaderboard(
        self,
        league: LeagueLevel,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get leaderboard for specific league"""
        
        # Get all users in league
        league_users_key = f"league_users:{league.value}"
        
        # This would query users in the league and rank by league points
        # For now, return empty list
        return []
    
    async def _store_league_progression(self, progression: LeagueProgression):
        """Store league progression in Redis"""
        
        progression_key = f"{self.league_progression_key}:{progression.user_id}"
        
        progression_data = {
            "current_league": str(progression.current_league.value),
            "league_status": progression.league_status.value,
            "league_entry_date": progression.league_entry_date.isoformat(),
            "days_in_current_league": str(progression.days_in_current_league),
            "league_points": str(progression.league_points),
            "season_achievements": str(progression.season_achievements),
            "tournament_participation_rate": str(progression.tournament_participation_rate),
            "average_tournament_rank": str(progression.average_tournament_rank),
            "win_rate": str(progression.win_rate),
            "consistency_score": str(progression.consistency_score),
            "risk_violations_count": str(progression.risk_violations_count),
            "completed_achievements": json.dumps(list(progression.completed_achievements)),
            "educational_achievement_count": str(progression.educational_achievement_count),
            "risk_management_achievement_count": str(progression.risk_management_achievement_count),
            "performance_achievement_count": str(progression.performance_achievement_count),
            "social_achievement_count": str(progression.social_achievement_count),
            "promotion_progress": json.dumps(progression.promotion_progress)
        }
        
        await self.redis.hset(progression_key, mapping=progression_data)
        await self.redis.expire(progression_key, 86400 * 365)  # Expire after 1 year
        
        # Add user to league index
        league_users_key = f"league_users:{progression.current_league.value}"
        await self.redis.zadd(
            league_users_key,
            {progression.user_id: progression.league_points}
        )
        await self.redis.expire(league_users_key, 86400 * 365)
    
    async def get_achievement_recommendations_for_league(
        self,
        user_id: str
    ) -> List[AchievementDefinition]:
        """Get achievement recommendations tailored to user's league"""
        
        progression = await self.get_user_league_progression(user_id)
        
        # Get general recommendations from achievement system
        recommendations = await self.achievement_system.get_recommended_achievements(
            user_id=user_id,
            completed_achievements=progression.completed_achievements
        )
        
        # Filter and prioritize based on league requirements
        current_league = progression.current_league
        
        # If user is eligible for promotion, prioritize next league requirements
        if progression.league_status == LeagueStatus.PROMOTION_ELIGIBLE:
            next_league = LeagueLevel(current_league.value + 1)
            next_requirements = self.league_requirements[next_league]
            
            # Prioritize required achievements for next league
            priority_achievements = [
                self.achievement_system.get_achievement_by_id(ach_id)
                for ach_id in next_requirements.required_achievements
                if (ach_id not in progression.completed_achievements and
                    self.achievement_system.get_achievement_by_id(ach_id))
            ]
            
            # Combine with general recommendations
            all_recommendations = priority_achievements + [
                ach for ach in recommendations if ach not in priority_achievements
            ]
            
            return all_recommendations[:5]  # Top 5 recommendations
        
        return recommendations
    
    async def get_league_statistics(self, league: LeagueLevel) -> Dict[str, Any]:
        """Get statistics for a specific league"""
        
        league_users_key = f"league_users:{league.value}"
        
        # Get user count in league
        user_count = await self.redis.zcard(league_users_key)
        
        # Get top performers
        top_performers = await self.redis.zrevrange(
            league_users_key, 0, 9, withscores=True
        )
        
        # Calculate average league points
        if user_count > 0:
            all_scores = await self.redis.zrange(
                league_users_key, 0, -1, withscores=True
            )
            average_points = sum(score for _, score in all_scores) / len(all_scores)
        else:
            average_points = 0
        
        return {
            "league": league.name,
            "total_users": user_count,
            "average_league_points": average_points,
            "top_performers": [
                {"user_id": user_id, "league_points": int(score)}
                for user_id, score in top_performers
            ],
            "ai_opponents": self.scaler.get_ai_opponents_for_league(league),
            "xp_multiplier": self.scaler.league_scaling[league]["xp_multiplier"]
        }