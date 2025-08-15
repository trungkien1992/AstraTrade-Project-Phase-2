from typing import Dict, List, Optional
from datetime import datetime, timezone, timedelta
import asyncio
import json
from redis import Redis
from fastapi import FastAPI, HTTPException

from ...domains.shared.events import DomainEvent
from ...domains.shared.redis_streams import RedisStreamsEventBus
from ...infrastructure.monitoring.service_monitoring import monitor_service_health
from .ai_traders import AITradingEngine, MarketConditionAnalyzer
from .ai_trading_strategies import AITradingStrategies
from .scoring import TournamentScoringEngine
from .leaderboard import LeaderboardManager

class CompetitionService:
    """
    Manages daily trading tournaments with real-time scoring.
    Processes trade events and maintains leaderboards.
    """
    
    def __init__(self):
        self.redis_client = Redis(host='localhost', port=6379, decode_responses=True)
        self.event_bus = RedisStreamsEventBus()
        self.tournament_duration = timedelta(hours=24)
        
        # Initialize AI trading components
        self.market_analyzer = MarketConditionAnalyzer()
        self.ai_strategies = AITradingStrategies(self.market_analyzer)
        self.ai_engine = AITradingEngine(market_data_service=self.market_analyzer)
        
        # Initialize scoring and leaderboard components
        self.scoring_engine = TournamentScoringEngine(self.redis_client)
        self.leaderboard_manager = LeaderboardManager(self.redis_client)
        
        # AI trading cycle task
        self.ai_trading_task = None
        
    async def start(self):
        """Initialize service and start listening for events"""
        await self.event_bus.subscribe('trading.trade_executed', self.process_trade_event)
        await self.event_bus.subscribe('trading.position_closed', self.process_position_closed)
        await self.initialize_daily_tournament()
        
        # Start AI trading cycle
        await self.start_ai_trading_cycle()
        
    async def initialize_daily_tournament(self):
        """Create new daily tournament at midnight UTC"""
        tournament_id = self.get_current_tournament_id()
        tournament_key = f"tournament:{tournament_id}"
        
        # Initialize tournament metadata
        self.redis_client.hset(f"{tournament_key}:meta", mapping={
            "start_time": datetime.now(timezone.utc).isoformat(),
            "end_time": (datetime.now(timezone.utc) + self.tournament_duration).isoformat(),
            "status": "active",
            "total_participants": 0,
            "total_trades": 0
        })
        
        # Initialize AI traders in the tournament
        await self.initialize_ai_traders(tournament_id)
        
    def get_current_tournament_id(self) -> str:
        """Generate tournament ID based on current date"""
        return f"daily:{datetime.now(timezone.utc).strftime('%Y-%m-%d')}"
    
    async def process_trade_event(self, event: DomainEvent):
        """Process incoming trade events and update scores"""
        trade_data = event.data
        tournament_id = self.get_current_tournament_id()
        
        # Calculate composite score
        score_components = await self.calculate_score_components(trade_data)
        total_score = self.calculate_composite_score(score_components)
        
        # Update leaderboard atomically
        await self.update_leaderboard(tournament_id, trade_data['user_id'], total_score)
        
        # Record trade for audit/replay
        await self.record_tournament_trade(tournament_id, trade_data)
        
        # Publish leaderboard update event
        await self.publish_leaderboard_update(tournament_id, trade_data['user_id'])
    
    async def process_position_closed(self, event: DomainEvent):
        """Process position closed events"""
        position_data = event.data
        tournament_id = self.get_current_tournament_id()
        
        # Update user stats when position closes
        await self.update_user_tournament_stats(tournament_id, position_data)
        
        # Recalculate and update score
        score_components = await self.calculate_score_components(position_data)
        total_score = self.calculate_composite_score(score_components)
        await self.update_leaderboard(tournament_id, position_data['user_id'], total_score)
    
    async def initialize_ai_traders(self, tournament_id: str):
        """Initialize AI traders for the tournament"""
        print(f"🤖 Initializing AI traders for tournament {tournament_id}")
        
        # Initialize AI trader states for this tournament
        self.ai_engine.initialize_ai_states(tournament_id)
        
        # Register AI traders in the leaderboard with initial scores
        for ai_trader in self.ai_engine.get_active_ai_traders():
            await self.leaderboard_manager.update_score(
                tournament_id, 
                ai_trader.id, 
                0.0  # Starting score
            )
            
            # Initialize AI trader stats
            await self.initialize_ai_trader_stats(tournament_id, ai_trader.id)
        
        print(f"✅ Initialized {len(self.ai_engine.get_active_ai_traders())} AI traders")
    
    async def initialize_ai_trader_stats(self, tournament_id: str, ai_id: str):
        """Initialize AI trader tournament statistics"""
        stats_key = f"tournament:{tournament_id}:stats:{ai_id}"
        initial_stats = {
            'total_trades': '0',
            'winning_trades': '0',
            'total_profit': '0.0',
            'total_volume': '0.0',
            'initial_capital': '100000.0',
            'is_ai': 'true',
            'last_updated': datetime.now(timezone.utc).isoformat()
        }
        self.redis_client.hset(stats_key, mapping=initial_stats)
    
    async def start_ai_trading_cycle(self):
        """Start the AI trading cycle task"""
        if self.ai_trading_task is not None:
            self.ai_trading_task.cancel()
        
        self.ai_trading_task = asyncio.create_task(self._ai_trading_loop())
        print("🚀 AI trading cycle started")
    
    async def _ai_trading_loop(self):
        """Main AI trading loop - runs every 30 seconds"""
        while True:
            try:
                tournament_id = self.get_current_tournament_id()
                tournament_meta = await self.get_tournament_metadata(tournament_id)
                
                # Only run AI trading if tournament is active
                if tournament_meta.get('status') == 'active':
                    cycle_result = await self.ai_engine.run_ai_trading_cycle(tournament_id)
                    
                    if cycle_result['trades_generated'] > 0:
                        print(f"🤖 AI Cycle: {cycle_result['trades_generated']} trades from {cycle_result['active_traders']} active traders")
                        
                        # Update leaderboard for AI traders with new scores
                        await self._update_ai_leaderboard_scores(tournament_id)
                
                # Wait 30 seconds before next cycle
                await asyncio.sleep(30)
                
            except asyncio.CancelledError:
                print("🛑 AI trading cycle stopped")
                break
            except Exception as e:
                print(f"❌ Error in AI trading cycle: {e}")
                await asyncio.sleep(5)  # Shorter wait on error
    
    async def _update_ai_leaderboard_scores(self, tournament_id: str):
        """Update leaderboard scores for all AI traders"""
        ai_stats = self.ai_engine.get_ai_leaderboard_stats()
        
        for ai_stat in ai_stats:
            if ai_stat['daily_trades'] > 0:  # Only update if AI has made trades
                # Calculate score using the same scoring engine as human players
                score_components = await self.scoring_engine.calculate_score_components(
                    ai_stat['ai_id'], tournament_id
                )
                total_score = self.scoring_engine.calculate_composite_score(score_components)
                
                # Update leaderboard
                await self.leaderboard_manager.update_score(
                    tournament_id, ai_stat['ai_id'], total_score
                )
    
    async def calculate_score_components(self, trade_data: Dict) -> Dict[str, float]:
        """Calculate scoring components using the scoring engine"""
        tournament_id = self.get_current_tournament_id()
        user_id = trade_data.get('user_id')
        
        if not user_id:
            return {
                'profit_factor': 0.0,
                'win_rate': 0.0,
                'volume': 0.0,
                'consistency': 0.0
            }
        
        return await self.scoring_engine.calculate_score_components(user_id, tournament_id)
    
    def calculate_composite_score(self, components: Dict[str, float]) -> float:
        """Calculate final composite score using the scoring engine"""
        return self.scoring_engine.calculate_composite_score(components)
    
    async def update_leaderboard(self, tournament_id: str, user_id: str, score: float):
        """Update user's score in the leaderboard using the leaderboard manager"""
        await self.leaderboard_manager.update_score(tournament_id, user_id, score)
    
    async def record_tournament_trade(self, tournament_id: str, trade_data: Dict):
        """Record trade for tournament audit trail"""
        trade_record = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'user_id': trade_data['user_id'],
            'trade_data': trade_data
        }
        
        # Store in Redis list for the tournament
        trade_key = f"tournament:{tournament_id}:trades"
        self.redis_client.lpush(trade_key, json.dumps(trade_record))
        
        # Keep only last 10000 trades to prevent memory issues
        self.redis_client.ltrim(trade_key, 0, 9999)
    
    async def update_user_tournament_stats(self, tournament_id: str, position_data: Dict):
        """Update user's tournament statistics"""
        user_id = position_data['user_id']
        stats_key = f"tournament:{tournament_id}:stats:{user_id}"
        
        # Get current stats
        current_stats = self.redis_client.hgetall(stats_key)
        if not current_stats:
            current_stats = {
                'total_trades': '0',
                'winning_trades': '0',
                'total_profit': '0.0',
                'total_volume': '0.0',
                'initial_capital': '100000.0'  # Default starting capital
            }
        
        # Update stats based on position data
        total_trades = int(current_stats['total_trades']) + 1
        profit = float(position_data.get('profit', 0))
        winning_trades = int(current_stats['winning_trades'])
        if profit > 0:
            winning_trades += 1
        
        total_profit = float(current_stats['total_profit']) + profit
        total_volume = float(current_stats['total_volume']) + float(position_data.get('volume', 0))
        
        # Store updated stats
        updated_stats = {
            'total_trades': str(total_trades),
            'winning_trades': str(winning_trades),
            'total_profit': str(total_profit),
            'total_volume': str(total_volume),
            'initial_capital': current_stats['initial_capital'],
            'last_updated': datetime.now(timezone.utc).isoformat()
        }
        
        self.redis_client.hset(stats_key, mapping=updated_stats)
    
    async def publish_leaderboard_update(self, tournament_id: str, user_id: str):
        """Publish leaderboard update event for WebSocket clients"""
        # Get updated rank and score
        leaderboard_key = f"tournament:{tournament_id}:leaderboard"
        score = self.redis_client.zscore(leaderboard_key, user_id)
        rank = self.redis_client.zrevrank(leaderboard_key, user_id)
        
        if score is not None and rank is not None:
            update_event = {
                'tournament_id': tournament_id,
                'user_id': user_id,
                'score': score,
                'rank': rank + 1,  # Redis ranks are 0-indexed
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
            # Publish to Redis pub/sub for WebSocket manager
            self.redis_client.publish(
                f'tournament:{tournament_id}:leaderboard',
                json.dumps(update_event)
            )
    
    async def get_tournament_leaderboard(self, tournament_id: str, start: int = 0, end: int = 99) -> List[Dict]:
        """Get current tournament leaderboard using the leaderboard manager"""
        return await self.leaderboard_manager.get_leaderboard(tournament_id, start, end)
    
    async def get_tournament_metadata(self, tournament_id: str) -> Dict:
        """Get tournament metadata"""
        meta_key = f"tournament:{tournament_id}:meta"
        return self.redis_client.hgetall(meta_key)
    
    async def stop_ai_trading_cycle(self):
        """Stop the AI trading cycle"""
        if self.ai_trading_task is not None:
            self.ai_trading_task.cancel()
            try:
                await self.ai_trading_task
            except asyncio.CancelledError:
                pass
            self.ai_trading_task = None
            print("🛑 AI trading cycle stopped")
    
    async def get_ai_trader_info(self, ai_id: str) -> Optional[Dict]:
        """Get detailed information about a specific AI trader"""
        ai_trader = self.ai_engine.get_ai_trader(ai_id)
        if not ai_trader:
            return None
        
        # Get current state
        ai_state = self.ai_engine.ai_states.get(ai_id, {})
        
        return {
            'id': ai_trader.id,
            'name': ai_trader.name,
            'title': ai_trader.title,
            'strategy': ai_trader.strategy.value,
            'backstory': ai_trader.backstory,
            'risk_profile': ai_trader.risk_profile,
            'personality_traits': ai_trader.personality_traits,
            'preferred_symbols': ai_trader.preferred_symbols,
            'trading_hours': ai_trader.trading_hours,
            'current_state': {
                'total_trades': ai_state.get('daily_trades', 0),
                'total_profit': ai_state.get('total_profit', 0.0),
                'portfolio_value': ai_state.get('portfolio_value', 100000.0),
                'win_count': ai_state.get('win_count', 0),
                'loss_count': ai_state.get('loss_count', 0),
                'last_trade_time': ai_state.get('last_trade_time'),
                'active': ai_state.get('active', False)
            }
        }
    
    async def get_tournament_statistics(self, tournament_id: str) -> Dict:
        """Get comprehensive tournament statistics"""
        meta = await self.get_tournament_metadata(tournament_id)
        leaderboard = await self.get_tournament_leaderboard(tournament_id, 0, 100)
        
        # Count participants
        human_players = len([p for p in leaderboard if not p['is_ai']])
        ai_players = len([p for p in leaderboard if p['is_ai']])
        
        # Get trade count
        trades_key = f"tournament:{tournament_id}:trades"
        total_trades = self.redis_client.llen(trades_key)
        
        return {
            'tournament_id': tournament_id,
            'status': meta.get('status', 'unknown'),
            'start_time': meta.get('start_time'),
            'end_time': meta.get('end_time'),
            'total_participants': human_players + ai_players,
            'human_players': human_players,
            'ai_players': ai_players,
            'total_trades': total_trades,
            'top_performers': leaderboard[:10],  # Top 10
            'ai_trading_active': self.ai_trading_task is not None and not self.ai_trading_task.done()
        }
    
    async def health_check(self) -> Dict[str, str]:
        """Health check for monitoring"""
        try:
            # Test Redis connection
            self.redis_client.ping()
            
            # Check current tournament
            tournament_id = self.get_current_tournament_id()
            tournament_exists = self.redis_client.exists(f"tournament:{tournament_id}:meta")
            
            # Check AI trading status
            ai_trading_status = "running" if (
                self.ai_trading_task is not None and not self.ai_trading_task.done()
            ) else "stopped"
            
            return {
                "status": "healthy",
                "redis_connection": "ok",
                "current_tournament": tournament_id,
                "tournament_active": "yes" if tournament_exists else "no",
                "ai_trading_status": ai_trading_status,
                "active_ai_traders": str(len(self.ai_engine.get_active_ai_traders()))
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }