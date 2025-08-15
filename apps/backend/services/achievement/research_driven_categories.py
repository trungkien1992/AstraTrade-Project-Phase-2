#!/usr/bin/env python3
"""
Research-Driven Achievement Categories System

Implements achievement categories based on neuroscience research and
responsible gamification principles, prioritizing education and risk
management over pure performance metrics.

Category Distribution (Research-Based):
- Educational: 60% - Learning-focused achievements that build trading skills
- Risk Management: 20% - Safety-focused achievements promoting responsible trading  
- Performance: 15% - Skill-based milestones that demonstrate competency
- Social: 5% - Community engagement without promoting harmful competition

Design Principles:
- Achievements promote learning over speculation
- Safety behaviors are heavily rewarded  
- Performance metrics focus on consistency over profits
- Social elements encourage collaboration, not competition
- Progressive skill building through achievement chains
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

from .dopamine_timing_engine import AchievementPriority


logger = logging.getLogger(__name__)


class AchievementCategory(Enum):
    """Research-driven achievement categories"""
    EDUCATIONAL = "educational"          # 60% - Learning and skill development
    RISK_MANAGEMENT = "risk_management"  # 20% - Safety and responsible trading
    PERFORMANCE = "performance"          # 15% - Skill-based milestones
    SOCIAL = "social"                   # 5% - Community engagement


class SkillLevel(Enum):
    """Progressive skill levels for educational achievements"""
    NOVICE = 1          # Basic concepts
    APPRENTICE = 2      # Intermediate understanding
    PRACTITIONER = 3    # Applied knowledge
    EXPERT = 4          # Advanced mastery
    MASTER = 5          # Teaching others


class RiskLevel(Enum):
    """Risk management achievement levels"""
    AWARENESS = 1       # Understanding risks
    PREVENTION = 2      # Implementing safeguards  
    MANAGEMENT = 3      # Active risk control
    OPTIMIZATION = 4    # Advanced risk techniques


@dataclass
class AchievementDefinition:
    """Complete achievement definition with research-based categorization"""
    achievement_id: str
    name: str
    description: str
    category: AchievementCategory
    priority: AchievementPriority
    
    # Educational metadata
    skill_level: Optional[SkillLevel] = None
    learning_objectives: List[str] = field(default_factory=list)
    educational_content_ids: List[str] = field(default_factory=list)
    
    # Risk management metadata
    risk_level: Optional[RiskLevel] = None
    safety_behaviors: List[str] = field(default_factory=list)
    risk_reduction_impact: float = 0.0  # 0-1 scale
    
    # Trigger conditions
    trigger_conditions: Dict[str, Any] = field(default_factory=dict)
    prerequisite_achievements: List[str] = field(default_factory=list)
    
    # Rewards and motivation
    xp_reward: int = 100
    badge_rarity: str = "common"
    celebration_level: str = "standard"  # subtle, standard, celebrate
    
    # Metadata
    cosmic_theme: str = ""
    storyline_connection: str = ""
    estimated_difficulty: str = "medium"  # easy, medium, hard, expert
    
    @property
    def is_educational(self) -> bool:
        return self.category == AchievementCategory.EDUCATIONAL
    
    @property 
    def promotes_safety(self) -> bool:
        return self.category == AchievementCategory.RISK_MANAGEMENT
    
    @property
    def builds_skills(self) -> bool:
        return self.category in [AchievementCategory.EDUCATIONAL, AchievementCategory.RISK_MANAGEMENT]


class ResearchDrivenAchievements:
    """
    Achievement system implementing research-based categories that promote
    learning, safety, and responsible trading behaviors.
    """
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.achievements = self._initialize_achievements()
        self.category_distribution = self._calculate_category_distribution()
        
    def _initialize_achievements(self) -> Dict[str, AchievementDefinition]:
        """Initialize all research-driven achievements"""
        achievements = {}
        
        # EDUCATIONAL ACHIEVEMENTS (60% of total)
        educational_achievements = self._create_educational_achievements()
        achievements.update(educational_achievements)
        
        # RISK MANAGEMENT ACHIEVEMENTS (20% of total)
        risk_management_achievements = self._create_risk_management_achievements()
        achievements.update(risk_management_achievements)
        
        # PERFORMANCE ACHIEVEMENTS (15% of total)  
        performance_achievements = self._create_performance_achievements()
        achievements.update(performance_achievements)
        
        # SOCIAL ACHIEVEMENTS (5% of total)
        social_achievements = self._create_social_achievements()
        achievements.update(social_achievements)
        
        return achievements
    
    def _create_educational_achievements(self) -> Dict[str, AchievementDefinition]:
        """Create educational achievements (60% of total) - Learning focused"""
        achievements = {}
        
        # === NOVICE LEVEL EDUCATIONAL ACHIEVEMENTS ===
        achievements["stellar_academy_graduate"] = AchievementDefinition(
            achievement_id="stellar_academy_graduate",
            name="Stellar Academy Graduate",
            description="Complete all basic trading tutorials and pass the fundamentals quiz",
            category=AchievementCategory.EDUCATIONAL,
            priority=AchievementPriority.EDUCATIONAL,
            skill_level=SkillLevel.NOVICE,
            learning_objectives=[
                "Understand basic trading terminology",
                "Learn order types and execution",
                "Grasp market structure concepts",
                "Master platform navigation"
            ],
            educational_content_ids=["tutorial_basics", "quiz_fundamentals", "platform_tour"],
            trigger_conditions={
                "type": "content_completion",
                "required_modules": ["basics", "orders", "platform"],
                "minimum_quiz_score": 80
            },
            xp_reward=200,
            badge_rarity="common",
            celebration_level="celebrate",
            cosmic_theme="Graduation from the Galactic Trading Academy",
            storyline_connection="First step in becoming a certified Star Trader",
            estimated_difficulty="easy"
        )
        
        achievements["chart_navigator"] = AchievementDefinition(
            achievement_id="chart_navigator",
            name="Chart Navigator",
            description="Learn to read charts and identify 5 basic technical patterns",
            category=AchievementCategory.EDUCATIONAL,
            priority=AchievementPriority.EDUCATIONAL,
            skill_level=SkillLevel.NOVICE,
            learning_objectives=[
                "Read candlestick charts",
                "Identify support and resistance",
                "Recognize basic patterns",
                "Understand timeframes"
            ],
            educational_content_ids=["chart_reading", "pattern_guide", "technical_analysis_basics"],
            trigger_conditions={
                "type": "knowledge_demonstration",
                "patterns_identified": 5,
                "chart_analysis_sessions": 10,
                "accuracy_threshold": 70
            },
            xp_reward=150,
            badge_rarity="common",
            cosmic_theme="Master of stellar chart navigation",
            estimated_difficulty="medium"
        )
        
        achievements["risk_awareness_pioneer"] = AchievementDefinition(
            achievement_id="risk_awareness_pioneer",
            name="Risk Awareness Pioneer",
            description="Complete comprehensive risk education and demonstrate understanding",
            category=AchievementCategory.EDUCATIONAL,
            priority=AchievementPriority.EDUCATIONAL,
            skill_level=SkillLevel.NOVICE,
            learning_objectives=[
                "Understand market risks",
                "Learn position sizing principles", 
                "Grasp risk-reward ratios",
                "Master stop-loss concepts"
            ],
            educational_content_ids=["risk_education", "position_sizing", "risk_reward"],
            trigger_conditions={
                "type": "educational_completion",
                "modules_completed": ["risk_basics", "position_sizing", "stop_losses"],
                "practical_exercises": 5
            },
            xp_reward=250,
            badge_rarity="uncommon",
            celebration_level="celebrate",
            cosmic_theme="Guardian of the Risk Management Constellation",
            estimated_difficulty="medium"
        )
        
        # === APPRENTICE LEVEL EDUCATIONAL ACHIEVEMENTS ===
        achievements["market_psychology_scholar"] = AchievementDefinition(
            achievement_id="market_psychology_scholar", 
            name="Market Psychology Scholar",
            description="Master the psychology of trading and emotional discipline",
            category=AchievementCategory.EDUCATIONAL,
            priority=AchievementPriority.EDUCATIONAL,
            skill_level=SkillLevel.APPRENTICE,
            learning_objectives=[
                "Understand emotional trading traps",
                "Learn discipline techniques",
                "Master mindfulness for traders",
                "Develop emotional intelligence"
            ],
            educational_content_ids=["psychology_course", "discipline_training", "mindfulness_guide"],
            prerequisite_achievements=["stellar_academy_graduate"],
            trigger_conditions={
                "type": "advanced_learning",
                "psychology_modules_completed": 8,
                "reflection_journal_entries": 20,
                "stress_management_practices": 5
            },
            xp_reward=300,
            badge_rarity="rare",
            cosmic_theme="Keeper of the Mental Discipline Codex",
            estimated_difficulty="hard"
        )
        
        achievements["fundamental_analyst"] = AchievementDefinition(
            achievement_id="fundamental_analyst",
            name="Fundamental Analyst",
            description="Master fundamental analysis and economic interpretation",
            category=AchievementCategory.EDUCATIONAL,
            priority=AchievementPriority.EDUCATIONAL,
            skill_level=SkillLevel.APPRENTICE,
            learning_objectives=[
                "Read financial statements",
                "Understand economic indicators",
                "Analyze company valuations", 
                "Interpret market news impact"
            ],
            educational_content_ids=["fundamental_analysis", "economics", "financial_statements"],
            prerequisite_achievements=["stellar_academy_graduate", "chart_navigator"],
            trigger_conditions={
                "type": "analysis_mastery",
                "financial_statements_analyzed": 10,
                "economic_reports_interpreted": 15,
                "analysis_accuracy": 75
            },
            xp_reward=350,
            badge_rarity="rare",
            cosmic_theme="Oracle of the Economic Nebula",
            estimated_difficulty="hard"
        )
        
        # === PRACTITIONER LEVEL EDUCATIONAL ACHIEVEMENTS ===
        achievements["strategy_architect"] = AchievementDefinition(
            achievement_id="strategy_architect",
            name="Strategy Architect",
            description="Design and backtest your own trading strategy",
            category=AchievementCategory.EDUCATIONAL,
            priority=AchievementPriority.EDUCATIONAL,
            skill_level=SkillLevel.PRACTITIONER,
            learning_objectives=[
                "Design systematic strategies",
                "Conduct proper backtesting",
                "Understand strategy optimization",
                "Learn forward testing methods"
            ],
            educational_content_ids=["strategy_design", "backtesting", "optimization"],
            prerequisite_achievements=["market_psychology_scholar", "fundamental_analyst"],
            trigger_conditions={
                "type": "strategy_creation",
                "strategies_designed": 1,
                "backtest_periods": 12,
                "forward_test_duration_days": 30,
                "strategy_sharpe_ratio": 1.2
            },
            xp_reward=500,
            badge_rarity="epic",
            celebration_level="celebrate",
            cosmic_theme="Architect of the Strategic Constellation",
            estimated_difficulty="expert"
        )
        
        # === EXPERT LEVEL EDUCATIONAL ACHIEVEMENTS ===  
        achievements["galactic_mentor"] = AchievementDefinition(
            achievement_id="galactic_mentor",
            name="Galactic Mentor",
            description="Help 10 new traders complete their basic education",
            category=AchievementCategory.EDUCATIONAL,
            priority=AchievementPriority.EDUCATIONAL,
            skill_level=SkillLevel.EXPERT,
            learning_objectives=[
                "Teach fundamental concepts",
                "Guide strategy development",
                "Provide constructive feedback",
                "Foster learning communities"
            ],
            prerequisite_achievements=["strategy_architect"],
            trigger_conditions={
                "type": "mentoring",
                "traders_mentored": 10,
                "mentoring_sessions": 50,
                "mentee_success_rate": 80
            },
            xp_reward=1000,
            badge_rarity="legendary",
            celebration_level="celebrate",
            cosmic_theme="Grand Master of the Teaching Order",
            estimated_difficulty="expert"
        )
        
        return achievements
    
    def _create_risk_management_achievements(self) -> Dict[str, AchievementDefinition]:
        """Create risk management achievements (20% of total) - Safety focused"""
        achievements = {}
        
        # === AWARENESS LEVEL RISK MANAGEMENT ===
        achievements["stop_loss_guardian"] = AchievementDefinition(
            achievement_id="stop_loss_guardian",
            name="Stop Loss Guardian",
            description="Set stop losses on 50 consecutive trades",
            category=AchievementCategory.RISK_MANAGEMENT,
            priority=AchievementPriority.CRITICAL,
            risk_level=RiskLevel.AWARENESS,
            safety_behaviors=["consistent_stop_loss_usage"],
            risk_reduction_impact=0.6,
            trigger_conditions={
                "type": "safety_behavior",
                "consecutive_trades_with_stops": 50,
                "stop_loss_percentage": 100
            },
            xp_reward=200,
            badge_rarity="uncommon",
            celebration_level="celebrate",
            cosmic_theme="Protector of Capital Integrity",
            estimated_difficulty="medium"
        )
        
        achievements["position_size_master"] = AchievementDefinition(
            achievement_id="position_size_master",
            name="Position Size Master", 
            description="Never risk more than 2% per trade for 100 trades",
            category=AchievementCategory.RISK_MANAGEMENT,
            priority=AchievementPriority.CRITICAL,
            risk_level=RiskLevel.PREVENTION,
            safety_behaviors=["proper_position_sizing"],
            risk_reduction_impact=0.8,
            trigger_conditions={
                "type": "risk_discipline",
                "trades_count": 100,
                "max_risk_percentage": 2.0,
                "compliance_rate": 100
            },
            xp_reward=300,
            badge_rarity="rare",
            celebration_level="celebrate",
            cosmic_theme="Keeper of the Sacred Risk Limits",
            estimated_difficulty="hard"
        )
        
        # === MANAGEMENT LEVEL RISK MANAGEMENT ===
        achievements["drawdown_recovery_expert"] = AchievementDefinition(
            achievement_id="drawdown_recovery_expert",
            name="Drawdown Recovery Expert",
            description="Successfully recover from a 10% drawdown using proper risk management",
            category=AchievementCategory.RISK_MANAGEMENT,
            priority=AchievementPriority.CRITICAL,
            risk_level=RiskLevel.MANAGEMENT,
            safety_behaviors=["disciplined_recovery", "reduced_position_sizing"],
            risk_reduction_impact=0.7,
            trigger_conditions={
                "type": "recovery_demonstration",
                "drawdown_percentage": 10,
                "recovery_achieved": True,
                "recovery_method": "risk_reduction"
            },
            xp_reward=400,
            badge_rarity="epic",
            cosmic_theme="Phoenix of Capital Resurrection", 
            estimated_difficulty="expert"
        )
        
        # === OPTIMIZATION LEVEL RISK MANAGEMENT ===
        achievements["portfolio_optimizer"] = AchievementDefinition(
            achievement_id="portfolio_optimizer",
            name="Portfolio Optimizer",
            description="Maintain optimal risk-adjusted returns for 6 months",
            category=AchievementCategory.RISK_MANAGEMENT,
            priority=AchievementPriority.CRITICAL,
            risk_level=RiskLevel.OPTIMIZATION,
            safety_behaviors=["diversification", "correlation_management", "dynamic_hedging"],
            risk_reduction_impact=0.9,
            trigger_conditions={
                "type": "advanced_optimization",
                "duration_months": 6,
                "sharpe_ratio": 1.5,
                "max_drawdown": 5,
                "consistency_score": 85
            },
            xp_reward=750,
            badge_rarity="legendary",
            celebration_level="celebrate",
            cosmic_theme="Master of the Risk-Reward Equilibrium",
            estimated_difficulty="expert"
        )
        
        return achievements
    
    def _create_performance_achievements(self) -> Dict[str, AchievementDefinition]:
        """Create performance achievements (15% of total) - Skill demonstration"""
        achievements = {}
        
        # Focus on CONSISTENCY over profits
        achievements["consistent_trader"] = AchievementDefinition(
            achievement_id="consistent_trader",
            name="Consistent Trader", 
            description="Achieve 70% win rate over 100 trades with proper risk management",
            category=AchievementCategory.PERFORMANCE,
            priority=AchievementPriority.PERFORMANCE,
            trigger_conditions={
                "type": "performance_milestone",
                "trades_count": 100,
                "win_rate": 70,
                "risk_compliance": True,
                "average_risk_per_trade": 2
            },
            xp_reward=400,
            badge_rarity="rare",
            cosmic_theme="Harbinger of Consistent Excellence",
            estimated_difficulty="hard"
        )
        
        achievements["patience_virtuoso"] = AchievementDefinition(
            achievement_id="patience_virtuoso",
            name="Patience Virtuoso",
            description="Wait for 5+ high-probability setups and execute perfectly",
            category=AchievementCategory.PERFORMANCE,
            priority=AchievementPriority.PERFORMANCE,
            trigger_conditions={
                "type": "discipline_demonstration", 
                "high_probability_trades": 5,
                "setup_patience_hours": 20,
                "execution_accuracy": 95
            },
            xp_reward=300,
            badge_rarity="epic",
            cosmic_theme="Master of Strategic Patience",
            estimated_difficulty="expert"
        )
        
        achievements["adaptation_specialist"] = AchievementDefinition(
            achievement_id="adaptation_specialist",
            name="Adaptation Specialist",
            description="Successfully trade in 3 different market conditions",
            category=AchievementCategory.PERFORMANCE,
            priority=AchievementPriority.PERFORMANCE,
            trigger_conditions={
                "type": "adaptability_test",
                "market_conditions": ["trending", "ranging", "volatile"],
                "profitable_in_each": True,
                "strategy_adjustments": 3
            },
            xp_reward=500,
            badge_rarity="epic",
            cosmic_theme="Shapeshifter of Market Conditions",
            estimated_difficulty="expert"
        )
        
        return achievements
    
    def _create_social_achievements(self) -> Dict[str, AchievementDefinition]:
        """Create social achievements (5% of total) - Community focused"""
        achievements = {}
        
        # Focus on COLLABORATION over competition
        achievements["knowledge_sharer"] = AchievementDefinition(
            achievement_id="knowledge_sharer",
            name="Knowledge Sharer",
            description="Share 10 educational insights that help other traders learn",
            category=AchievementCategory.SOCIAL,
            priority=AchievementPriority.SOCIAL,
            trigger_conditions={
                "type": "knowledge_sharing",
                "insights_shared": 10,
                "helpful_votes": 50,
                "educational_quality_score": 80
            },
            xp_reward=200,
            badge_rarity="uncommon",
            cosmic_theme="Beacon of Shared Wisdom",
            estimated_difficulty="medium"
        )
        
        achievements["community_supporter"] = AchievementDefinition(
            achievement_id="community_supporter",
            name="Community Supporter",
            description="Help 25 traders by answering questions and providing guidance",
            category=AchievementCategory.SOCIAL,
            priority=AchievementPriority.SOCIAL,
            trigger_conditions={
                "type": "community_support",
                "traders_helped": 25,
                "questions_answered": 50,
                "helpfulness_rating": 85
            },
            xp_reward=300,
            badge_rarity="rare",
            cosmic_theme="Guardian of Community Harmony",
            estimated_difficulty="hard"
        )
        
        return achievements
    
    def _calculate_category_distribution(self) -> Dict[AchievementCategory, float]:
        """Calculate actual category distribution to ensure research compliance"""
        category_counts = {category: 0 for category in AchievementCategory}
        
        for achievement in self.achievements.values():
            category_counts[achievement.category] += 1
        
        total_achievements = len(self.achievements)
        distribution = {
            category: count / total_achievements 
            for category, count in category_counts.items()
        }
        
        # Log distribution for monitoring
        logger.info("Achievement category distribution:")
        for category, percentage in distribution.items():
            logger.info(f"  {category.value}: {percentage:.1%}")
        
        # Verify research compliance
        target_distribution = {
            AchievementCategory.EDUCATIONAL: 0.60,
            AchievementCategory.RISK_MANAGEMENT: 0.20,
            AchievementCategory.PERFORMANCE: 0.15,
            AchievementCategory.SOCIAL: 0.05
        }
        
        for category, target_pct in target_distribution.items():
            actual_pct = distribution.get(category, 0)
            if abs(actual_pct - target_pct) > 0.05:  # 5% tolerance
                logger.warning(
                    f"Category distribution deviation: {category.value} "
                    f"actual={actual_pct:.1%}, target={target_pct:.1%}"
                )
        
        return distribution
    
    async def get_recommended_achievements(
        self,
        user_id: str,
        user_skill_level: SkillLevel = SkillLevel.NOVICE,
        completed_achievements: Set[str] = None
    ) -> List[AchievementDefinition]:
        """Get personalized achievement recommendations based on user profile"""
        
        if completed_achievements is None:
            completed_achievements = await self._get_user_completed_achievements(user_id)
        
        recommendations = []
        
        # Prioritize educational achievements (research-driven)
        educational_achievements = [
            achievement for achievement in self.achievements.values()
            if (achievement.category == AchievementCategory.EDUCATIONAL and
                achievement.achievement_id not in completed_achievements and
                self._meets_prerequisites(achievement, completed_achievements) and
                self._appropriate_skill_level(achievement, user_skill_level))
        ]
        
        # Prioritize risk management achievements
        risk_achievements = [
            achievement for achievement in self.achievements.values()
            if (achievement.category == AchievementCategory.RISK_MANAGEMENT and
                achievement.achievement_id not in completed_achievements and
                self._meets_prerequisites(achievement, completed_achievements))
        ]
        
        # Add performance achievements (limited)
        performance_achievements = [
            achievement for achievement in self.achievements.values()
            if (achievement.category == AchievementCategory.PERFORMANCE and
                achievement.achievement_id not in completed_achievements and
                self._meets_prerequisites(achievement, completed_achievements))
        ]
        
        # Sort by priority and add to recommendations
        recommendations.extend(sorted(educational_achievements[:3], key=lambda x: x.priority.value))
        recommendations.extend(sorted(risk_achievements[:2], key=lambda x: x.priority.value))
        recommendations.extend(sorted(performance_achievements[:1], key=lambda x: x.priority.value))
        
        return recommendations[:5]  # Return top 5 recommendations
    
    def _meets_prerequisites(
        self,
        achievement: AchievementDefinition,
        completed_achievements: Set[str]
    ) -> bool:
        """Check if user meets achievement prerequisites"""
        return all(
            prereq in completed_achievements 
            for prereq in achievement.prerequisite_achievements
        )
    
    def _appropriate_skill_level(
        self,
        achievement: AchievementDefinition,
        user_skill_level: SkillLevel
    ) -> bool:
        """Check if achievement is appropriate for user's skill level"""
        if not achievement.skill_level:
            return True
        
        # Allow achievements at or slightly above user's current level
        return achievement.skill_level.value <= user_skill_level.value + 1
    
    async def _get_user_completed_achievements(self, user_id: str) -> Set[str]:
        """Get user's completed achievements from database"""
        # This would query the user's achievement records
        # For now, return empty set
        return set()
    
    def get_achievement_by_id(self, achievement_id: str) -> Optional[AchievementDefinition]:
        """Get achievement definition by ID"""
        return self.achievements.get(achievement_id)
    
    def get_achievements_by_category(
        self,
        category: AchievementCategory
    ) -> List[AchievementDefinition]:
        """Get all achievements in a specific category"""
        return [
            achievement for achievement in self.achievements.values()
            if achievement.category == category
        ]
    
    def get_learning_path(self, target_skill_level: SkillLevel) -> List[AchievementDefinition]:
        """Get ordered learning path to reach target skill level"""
        path_achievements = []
        
        # Get educational achievements up to target level
        for skill_level in range(1, target_skill_level.value + 1):
            level_achievements = [
                achievement for achievement in self.achievements.values()
                if (achievement.category == AchievementCategory.EDUCATIONAL and
                    achievement.skill_level and
                    achievement.skill_level.value == skill_level)
            ]
            
            # Sort by estimated difficulty and prerequisite chain
            level_achievements.sort(key=lambda x: len(x.prerequisite_achievements))
            path_achievements.extend(level_achievements)
        
        return path_achievements
    
    async def get_category_progress(self, user_id: str) -> Dict[str, Dict]:
        """Get user's progress in each achievement category"""
        completed_achievements = await self._get_user_completed_achievements(user_id)
        
        progress = {}
        for category in AchievementCategory:
            category_achievements = self.get_achievements_by_category(category)
            completed_in_category = [
                ach for ach in category_achievements
                if ach.achievement_id in completed_achievements
            ]
            
            progress[category.value] = {
                "total_achievements": len(category_achievements),
                "completed": len(completed_in_category),
                "completion_percentage": len(completed_in_category) / len(category_achievements) * 100,
                "next_recommended": await self.get_recommended_achievements(user_id)
            }
        
        return progress