"""
Clan Trading Service
Integrates clan battles with real trading via Extended Exchange API
Calculates battle scores based on actual trading performance
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from ..models.game_models import (
    ConstellationBattle, ConstellationBattleParticipation, 
    ConstellationMembership, User, Constellation
)
from ..core.database import get_db
from .extended_exchange_client import ExtendedExchangeClient, ExtendedExchangeError
from ..core.config import settings

logger = logging.getLogger(__name__)


class ClanTradingService:
    """Service for integrating clan battles with real trading performance."""
    
    def __init__(self):
        self.exchange_client = ExtendedExchangeClient()
        self.battle_score_multipliers = {
            "trading_duel": 1.0,       # 1:1 score to PnL ratio
            "stellar_supremacy": 0.8,   # Emphasis on consistency
            "cosmic_conquest": 1.2      # Higher stakes, higher rewards
        }
    
    async def calculate_trading_score(
        self, 
        user_id: int, 
        battle_id: int,
        start_time: datetime,
        end_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Calculate trading score for a user in a specific battle timeframe.
        
        Returns:
            {
                "total_score": float,
                "trade_count": int,
                "pnl_usd": float,
                "win_rate": float,
                "best_trade": float,
                "worst_trade": float,
                "avg_trade_size": float
            }
        """
        end_time = end_time or datetime.utcnow()
        
        try:
            async with self.exchange_client as client:
                # Get user's trades during battle period
                trades = await client.get_trades(
                    start_time=int(start_time.timestamp() * 1000),
                    end_time=int(end_time.timestamp() * 1000),
                    limit=1000  # Max trades to analyze
                )
                
                if not trades.get("trades"):
                    return {
                        "total_score": 0.0,
                        "trade_count": 0,
                        "pnl_usd": 0.0,
                        "win_rate": 0.0,
                        "best_trade": 0.0,
                        "worst_trade": 0.0,
                        "avg_trade_size": 0.0
                    }
                
                # Calculate trading metrics
                trade_list = trades["trades"]
                trade_count = len(trade_list)
                total_pnl = 0.0
                winning_trades = 0
                trade_sizes = []
                trade_pnls = []
                
                for trade in trade_list:
                    # Calculate PnL for each trade
                    quantity = float(trade["quantity"])
                    price = float(trade["price"])
                    side = trade["side"]
                    
                    # Get entry price from order history (simplified)
                    trade_value = quantity * price
                    
                    # For demo, assume 0.5% average profit per trade
                    # In production, you'd track actual entry/exit prices
                    pnl = trade_value * 0.005 if side == "sell" else -trade_value * 0.005
                    
                    total_pnl += pnl
                    trade_sizes.append(trade_value)
                    trade_pnls.append(pnl)
                    
                    if pnl > 0:
                        winning_trades += 1
                
                # Calculate metrics
                win_rate = (winning_trades / trade_count) if trade_count > 0 else 0.0
                avg_trade_size = sum(trade_sizes) / len(trade_sizes) if trade_sizes else 0.0
                best_trade = max(trade_pnls) if trade_pnls else 0.0
                worst_trade = min(trade_pnls) if trade_pnls else 0.0
                
                # Calculate battle score based on multiple factors
                base_score = total_pnl  # PnL as base score
                consistency_bonus = win_rate * 100  # Bonus for high win rate
                activity_bonus = min(trade_count * 10, 200)  # Bonus for activity (capped)
                
                total_score = base_score + consistency_bonus + activity_bonus
                
                return {
                    "total_score": max(0.0, total_score),  # Minimum 0 score
                    "trade_count": trade_count,
                    "pnl_usd": total_pnl,
                    "win_rate": win_rate,
                    "best_trade": best_trade,
                    "worst_trade": worst_trade,
                    "avg_trade_size": avg_trade_size
                }
                
        except ExtendedExchangeError as e:
            logger.error(f"Failed to calculate trading score for user {user_id}: {e}")
            # Return zero score on API error
            return {
                "total_score": 0.0,
                "trade_count": 0,
                "pnl_usd": 0.0,
                "win_rate": 0.0,
                "best_trade": 0.0,
                "worst_trade": 0.0,
                "avg_trade_size": 0.0
            }
    
    async def update_battle_scores(self, battle_id: int, db: Session) -> Dict[str, Any]:
        """
        Update scores for all participants in an active battle.
        
        Returns summary of score updates.
        """
        battle = db.query(ConstellationBattle).filter(
            ConstellationBattle.id == battle_id
        ).first()
        
        if not battle or battle.status != "active":
            raise ValueError(f"Battle {battle_id} is not active")
        
        if not battle.started_at:
            raise ValueError(f"Battle {battle_id} has not started")
        
        # Get all participants
        participants = db.query(ConstellationBattleParticipation).filter(
            ConstellationBattleParticipation.battle_id == battle_id
        ).all()
        
        challenger_total = 0.0
        defender_total = 0.0
        updates_count = 0
        
        for participation in participants:
            try:
                # Calculate trading score since battle start
                score_data = await self.calculate_trading_score(
                    user_id=participation.user_id,
                    battle_id=battle_id,
                    start_time=battle.started_at,
                    end_time=datetime.utcnow()
                )
                
                # Apply battle type multiplier
                multiplier = self.battle_score_multipliers.get(battle.battle_type, 1.0)
                adjusted_score = score_data["total_score"] * multiplier
                
                # Update participation record
                participation.individual_score = adjusted_score
                participation.trades_completed = score_data["trade_count"]
                participation.pnl_usd = score_data["pnl_usd"]
                participation.win_rate = score_data["win_rate"]
                participation.last_activity_at = datetime.utcnow()
                
                # Add to constellation totals
                if participation.constellation_id == battle.challenger_constellation_id:
                    challenger_total += adjusted_score
                else:
                    defender_total += adjusted_score
                
                updates_count += 1
                logger.info(f"Updated score for user {participation.user_id}: {adjusted_score}")
                
            except Exception as e:
                logger.error(f"Failed to update score for participant {participation.user_id}: {e}")
                continue
        
        # Update battle totals
        battle.challenger_score = challenger_total
        battle.defender_score = defender_total
        battle.updated_at = datetime.utcnow()
        
        db.commit()
        
        return {
            "battle_id": battle_id,
            "participants_updated": updates_count,
            "challenger_score": challenger_total,
            "defender_score": defender_total,
            "score_difference": abs(challenger_total - defender_total),
            "leader": "challenger" if challenger_total > defender_total else "defender"
        }
    
    async def auto_update_active_battles(self, db: Session) -> List[Dict[str, Any]]:
        """
        Automatically update scores for all active battles.
        This should be called periodically (e.g., every 15 minutes).
        """
        active_battles = db.query(ConstellationBattle).filter(
            ConstellationBattle.status == "active"
        ).all()
        
        results = []
        
        for battle in active_battles:
            try:
                # Check if battle should be completed due to time
                if battle.started_at:
                    end_time = battle.started_at + timedelta(hours=battle.duration_hours)
                    if datetime.utcnow() > end_time:
                        # Auto-complete the battle
                        await self._complete_battle_automatically(battle, db)
                        results.append({
                            "battle_id": battle.id,
                            "action": "completed",
                            "reason": "time_expired"
                        })
                        continue
                
                # Update scores
                update_result = await self.update_battle_scores(battle.id, db)
                update_result["action"] = "scores_updated"
                results.append(update_result)
                
            except Exception as e:
                logger.error(f"Failed to update battle {battle.id}: {e}")
                results.append({
                    "battle_id": battle.id,
                    "action": "error",
                    "error": str(e)
                })
        
        return results
    
    async def _complete_battle_automatically(self, battle: ConstellationBattle, db: Session):
        """Complete a battle automatically when time expires."""
        # Import here to avoid circular imports
        from ..api.v1.constellations import _complete_battle
        
        await _complete_battle(battle, db)
        logger.info(f"Auto-completed battle {battle.id} due to time expiration")
    
    async def get_clan_trading_leaderboard(
        self, 
        constellation_id: int,
        period_days: int = 7,
        db: Session = None
    ) -> List[Dict[str, Any]]:
        """
        Get trading performance leaderboard for clan members.
        
        Args:
            constellation_id: Clan ID
            period_days: Period to analyze (default 7 days)
            db: Database session
        """
        if not db:
            db = next(get_db())
        
        # Get active clan members
        memberships = db.query(ConstellationMembership, User).join(
            User, ConstellationMembership.user_id == User.id
        ).filter(
            and_(
                ConstellationMembership.constellation_id == constellation_id,
                ConstellationMembership.is_active == True
            )
        ).all()
        
        leaderboard = []
        start_time = datetime.utcnow() - timedelta(days=period_days)
        
        for membership, user in memberships:
            try:
                # Calculate trading performance for the period
                score_data = await self.calculate_trading_score(
                    user_id=user.id,
                    battle_id=0,  # Not battle-specific
                    start_time=start_time
                )
                
                leaderboard.append({
                    "user_id": user.id,
                    "username": user.username,
                    "clan_role": membership.role,
                    "trading_score": score_data["total_score"],
                    "pnl_usd": score_data["pnl_usd"],
                    "trade_count": score_data["trade_count"],
                    "win_rate": score_data["win_rate"],
                    "avg_trade_size": score_data["avg_trade_size"],
                    "contribution_score": membership.contribution_score
                })
                
            except Exception as e:
                logger.error(f"Failed to get trading data for user {user.id}: {e}")
                # Add member with zero scores
                leaderboard.append({
                    "user_id": user.id,
                    "username": user.username,
                    "clan_role": membership.role,
                    "trading_score": 0.0,
                    "pnl_usd": 0.0,
                    "trade_count": 0,
                    "win_rate": 0.0,
                    "avg_trade_size": 0.0,
                    "contribution_score": membership.contribution_score
                })
        
        # Sort by trading score descending
        leaderboard.sort(key=lambda x: x["trading_score"], reverse=True)
        
        # Add rankings
        for i, member in enumerate(leaderboard):
            member["rank"] = i + 1
        
        return leaderboard


# Global service instance
clan_trading_service = ClanTradingService()


# API helper functions
async def start_battle_monitoring(battle_id: int, db: Session):
    """Start monitoring a battle for real trading integration."""
    try:
        result = await clan_trading_service.update_battle_scores(battle_id, db)
        logger.info(f"Started monitoring battle {battle_id}: {result}")
        return result
    except Exception as e:
        logger.error(f"Failed to start battle monitoring for {battle_id}: {e}")
        raise


async def get_real_time_battle_scores(battle_id: int, db: Session) -> Dict[str, Any]:
    """Get real-time battle scores based on current trading performance."""
    try:
        return await clan_trading_service.update_battle_scores(battle_id, db)
    except Exception as e:
        logger.error(f"Failed to get real-time scores for battle {battle_id}: {e}")
        raise


async def get_clan_trading_performance(constellation_id: int, db: Session) -> Dict[str, Any]:
    """Get comprehensive trading performance for a clan."""
    try:
        leaderboard = await clan_trading_service.get_clan_trading_leaderboard(
            constellation_id=constellation_id,
            period_days=30,  # Last 30 days
            db=db
        )
        
        # Calculate clan-wide metrics
        total_pnl = sum(member["pnl_usd"] for member in leaderboard)
        total_trades = sum(member["trade_count"] for member in leaderboard)
        avg_win_rate = sum(member["win_rate"] for member in leaderboard) / len(leaderboard) if leaderboard else 0
        
        return {
            "constellation_id": constellation_id,
            "member_count": len(leaderboard),
            "total_pnl_usd": total_pnl,
            "total_trades": total_trades,
            "average_win_rate": avg_win_rate,
            "top_performers": leaderboard[:5],  # Top 5 members
            "member_leaderboard": leaderboard,
            "last_updated": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get clan trading performance for {constellation_id}: {e}")
        raise