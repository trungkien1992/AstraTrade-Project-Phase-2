"""
Clan Battle Monitor Background Task
Automatically updates battle scores and completes expired battles
"""

import asyncio
import logging
from datetime import datetime
from typing import List
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..services.clan_trading_service import clan_trading_service
from ..models.game_models import ConstellationBattle

logger = logging.getLogger(__name__)


class ClanBattleMonitor:
    """Background service for monitoring and updating clan battles."""
    
    def __init__(self, update_interval: int = 900):  # 15 minutes default
        self.update_interval = update_interval
        self.is_running = False
        self._task = None
    
    async def start(self):
        """Start the battle monitoring service."""
        if self.is_running:
            logger.warning("Battle monitor is already running")
            return
        
        self.is_running = True
        self._task = asyncio.create_task(self._monitor_loop())
        logger.info(f"Clan battle monitor started (update interval: {self.update_interval}s)")
    
    async def stop(self):
        """Stop the battle monitoring service."""
        if not self.is_running:
            return
        
        self.is_running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        
        logger.info("Clan battle monitor stopped")
    
    async def _monitor_loop(self):
        """Main monitoring loop."""
        while self.is_running:
            try:
                await self._update_all_battles()
                await asyncio.sleep(self.update_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in battle monitor loop: {e}")
                await asyncio.sleep(30)  # Short delay before retry
    
    async def _update_all_battles(self):
        """Update scores for all active battles."""
        db = next(get_db())
        try:
            results = await clan_trading_service.auto_update_active_battles(db)
            
            if results:
                logger.info(f"Updated {len(results)} battles")
                for result in results:
                    if result["action"] == "completed":
                        logger.info(f"Auto-completed battle {result['battle_id']}: {result['reason']}")
                    elif result["action"] == "scores_updated":
                        logger.debug(f"Updated scores for battle {result['battle_id']}")
                    elif result["action"] == "error":
                        logger.error(f"Error updating battle {result['battle_id']}: {result['error']}")
            
        except Exception as e:
            logger.error(f"Failed to update battles: {e}")
        finally:
            db.close()
    
    async def force_update(self, battle_id: int = None) -> List[dict]:
        """Force an immediate update of all battles or a specific battle."""
        db = next(get_db())
        try:
            if battle_id:
                # Update specific battle
                result = await clan_trading_service.update_battle_scores(battle_id, db)
                return [{"battle_id": battle_id, "action": "force_updated", **result}]
            else:
                # Update all battles
                results = await clan_trading_service.auto_update_active_battles(db)
                return results
        except Exception as e:
            logger.error(f"Failed to force update battles: {e}")
            raise
        finally:
            db.close()


# Global battle monitor instance
battle_monitor = ClanBattleMonitor()


# Startup and shutdown handlers
async def start_battle_monitor():
    """Start the battle monitor on application startup."""
    await battle_monitor.start()


async def stop_battle_monitor():
    """Stop the battle monitor on application shutdown."""
    await battle_monitor.stop()


# Manual control functions
async def trigger_battle_update(battle_id: int = None):
    """Manually trigger a battle update."""
    return await battle_monitor.force_update(battle_id)


async def get_monitor_status():
    """Get the current status of the battle monitor."""
    return {
        "is_running": battle_monitor.is_running,
        "update_interval": battle_monitor.update_interval,
        "last_check": datetime.utcnow().isoformat()
    }