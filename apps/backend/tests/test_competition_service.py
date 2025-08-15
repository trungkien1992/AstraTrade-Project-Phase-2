import pytest
import asyncio
from datetime import datetime, timezone, timedelta
from unittest.mock import Mock, AsyncMock, patch
import redis
import json
from typing import Dict, Any

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from services.competition.competition_service import CompetitionService
from services.competition.scoring import TournamentScoringEngine
from services.competition.leaderboard import LeaderboardManager
from services.competition.ai_traders import AITradingEngine, AITraderPersonality, TradingStrategy
from domains.shared.events import DomainEvent

@pytest.fixture
def redis_client():
    """Mock Redis client for testing"""
    mock_redis = Mock(spec=redis.Redis)
    mock_redis.ping.return_value = True
    mock_redis.hset.return_value = True
    mock_redis.hgetall.return_value = {}
    mock_redis.zadd.return_value = 1
    mock_redis.zrevrange.return_value = []
    mock_redis.zrevrank.return_value = None
    mock_redis.zscore.return_value = None
    mock_redis.zcard.return_value = 0
    mock_redis.exists.return_value = True
    mock_redis.lpush.return_value = 1
    mock_redis.ltrim.return_value = True
    mock_redis.llen.return_value = 0
    mock_redis.publish.return_value = 1
    return mock_redis

@pytest.fixture
def competition_service(redis_client):
    """Create CompetitionService instance with mocked dependencies"""
    with patch('services.competition.competition_service.Redis', return_value=redis_client):
        service = CompetitionService()
        service.redis_client = redis_client
        return service

@pytest.fixture
def sample_trade_event():
    """Sample trade event for testing"""
    return DomainEvent(
        event_type="trade_executed",
        domain="trading", 
        entity_id="trade_123",
        data={
            'user_id': 'user_456',
            'symbol': 'BTC-USD',
            'side': 'BUY',
            'amount': 1000.0,
            'profit': 50.0,
            'profit_percentage': 5.0,
            'volume': 1000.0,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
    )

class TestCompetitionService:
    """Test suite for CompetitionService"""
    
    @pytest.mark.asyncio
    async def test_competition_service_initialization(self, competition_service):
        """Test that competition service initializes correctly"""
        assert competition_service.redis_client is not None
        assert competition_service.ai_engine is not None
        assert competition_service.scoring_engine is not None
        assert competition_service.leaderboard_manager is not None
        assert competition_service.tournament_duration == timedelta(hours=24)
    
    @pytest.mark.asyncio
    async def test_initialize_daily_tournament(self, competition_service):
        """Test daily tournament initialization"""
        await competition_service.initialize_daily_tournament()
        
        tournament_id = competition_service.get_current_tournament_id()
        expected_key = f"tournament:{tournament_id}:meta"
        
        # Verify tournament metadata was set
        competition_service.redis_client.hset.assert_called()
        calls = competition_service.redis_client.hset.call_args_list
        
        # Check that tournament metadata was set
        meta_call_found = False
        for call in calls:
            if expected_key in str(call):
                meta_call_found = True
                break
        assert meta_call_found, "Tournament metadata should be set"
    
    def test_get_current_tournament_id(self, competition_service):
        """Test tournament ID generation"""
        tournament_id = competition_service.get_current_tournament_id()
        today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        expected_id = f"daily:{today}"
        assert tournament_id == expected_id
    
    @pytest.mark.asyncio
    async def test_process_trade_event(self, competition_service, sample_trade_event):
        """Test trade event processing"""
        # Mock the scoring engine methods
        competition_service.scoring_engine.calculate_score_components = AsyncMock(
            return_value={
                'profit_factor': 75.0,
                'win_rate': 60.0,
                'volume': 30.0,
                'consistency': 45.0
            }
        )
        
        # Mock leaderboard update
        competition_service.leaderboard_manager.update_score = AsyncMock()
        
        await competition_service.process_trade_event(sample_trade_event)
        
        # Verify scoring was calculated
        competition_service.scoring_engine.calculate_score_components.assert_called_once()
        
        # Verify leaderboard was updated
        competition_service.leaderboard_manager.update_score.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_initialize_ai_traders(self, competition_service):
        """Test AI trader initialization for tournament"""
        tournament_id = "daily:2024-01-15"
        
        # Mock AI engine methods
        competition_service.ai_engine.initialize_ai_states = Mock()
        competition_service.ai_engine.get_active_ai_traders = Mock(
            return_value=[
                Mock(id="ai:captain_vega"),
                Mock(id="ai:commander_luna"),
                Mock(id="ai:admiral_nexus")
            ]
        )
        competition_service.leaderboard_manager.update_score = AsyncMock()
        
        await competition_service.initialize_ai_traders(tournament_id)
        
        # Verify AI states were initialized
        competition_service.ai_engine.initialize_ai_states.assert_called_once_with(tournament_id)
        
        # Verify AI traders were added to leaderboard
        assert competition_service.leaderboard_manager.update_score.call_count == 3
    
    @pytest.mark.asyncio
    async def test_ai_trading_cycle(self, competition_service):
        """Test AI trading cycle execution"""
        # Mock AI engine methods
        competition_service.ai_engine.run_ai_trading_cycle = AsyncMock(
            return_value={
                'trades_generated': 5,
                'active_traders': 20,
                'market_conditions': {'volatility': 0.03}
            }
        )
        
        # Mock tournament metadata
        competition_service.redis_client.hgetall.return_value = {'status': 'active'}
        
        tournament_id = competition_service.get_current_tournament_id()
        result = await competition_service.ai_engine.run_ai_trading_cycle(tournament_id)
        
        assert result['trades_generated'] == 5
        assert result['active_traders'] == 20
        assert 'market_conditions' in result
    
    @pytest.mark.asyncio
    async def test_update_user_tournament_stats(self, competition_service):
        """Test user tournament statistics update"""
        tournament_id = "daily:2024-01-15"
        position_data = {
            'user_id': 'user_123',
            'profit': 100.0,
            'volume': 5000.0
        }
        
        # Mock current stats
        competition_service.redis_client.hgetall.return_value = {
            'total_trades': '5',
            'winning_trades': '3',
            'total_profit': '250.0',
            'total_volume': '10000.0',
            'initial_capital': '100000.0'
        }
        
        await competition_service.update_user_tournament_stats(tournament_id, position_data)
        
        # Verify stats were updated
        competition_service.redis_client.hset.assert_called()
        
        # Check the updated stats
        call_args = competition_service.redis_client.hset.call_args
        updated_stats = call_args[1]['mapping']
        
        assert int(updated_stats['total_trades']) == 6
        assert int(updated_stats['winning_trades']) == 4
        assert float(updated_stats['total_profit']) == 350.0
    
    @pytest.mark.asyncio
    async def test_publish_leaderboard_update(self, competition_service):
        """Test leaderboard update publishing"""
        tournament_id = "daily:2024-01-15"
        user_id = "user_123"
        
        # Mock Redis responses
        competition_service.redis_client.zscore.return_value = 150.5
        competition_service.redis_client.zrevrank.return_value = 2
        
        await competition_service.publish_leaderboard_update(tournament_id, user_id)
        
        # Verify Redis pub/sub publish was called
        competition_service.redis_client.publish.assert_called_once()
        
        # Check published data
        call_args = competition_service.redis_client.publish.call_args
        channel, message_json = call_args[0]
        message = json.loads(message_json)
        
        assert channel == f'tournament:{tournament_id}:leaderboard'
        assert message['user_id'] == user_id
        assert message['score'] == 150.5
        assert message['rank'] == 3  # Redis rank is 0-indexed, published is 1-indexed
    
    @pytest.mark.asyncio
    async def test_get_tournament_leaderboard(self, competition_service):
        """Test tournament leaderboard retrieval"""
        tournament_id = "daily:2024-01-15"
        
        # Mock leaderboard manager
        expected_leaderboard = [
            {
                'rank': 1,
                'user_id': 'ai:captain_vega',
                'username': 'Captain Vega',
                'score': 250.0,
                'is_ai': True
            },
            {
                'rank': 2,
                'user_id': 'user_123',
                'username': 'TestUser',
                'score': 180.0,
                'is_ai': False
            }
        ]
        
        competition_service.leaderboard_manager.get_leaderboard = AsyncMock(
            return_value=expected_leaderboard
        )
        
        result = await competition_service.get_tournament_leaderboard(tournament_id)
        
        assert len(result) == 2
        assert result[0]['rank'] == 1
        assert result[0]['username'] == 'Captain Vega'
        assert result[1]['is_ai'] is False
    
    @pytest.mark.asyncio
    async def test_get_ai_trader_info(self, competition_service):
        """Test AI trader info retrieval"""
        ai_id = "ai:captain_vega"
        
        # Mock AI engine
        mock_ai_trader = Mock()
        mock_ai_trader.id = ai_id
        mock_ai_trader.name = "Captain Vega"
        mock_ai_trader.title = "The Stellar Maverick"
        mock_ai_trader.strategy.value = "aggressive_growth"
        mock_ai_trader.backstory = "A fearless pilot..."
        mock_ai_trader.risk_profile = {'position_size': 0.15}
        mock_ai_trader.personality_traits = {'confidence': 0.9}
        mock_ai_trader.preferred_symbols = ['BTC-USD', 'ETH-USD']
        mock_ai_trader.trading_hours = list(range(9, 17))
        
        competition_service.ai_engine.get_ai_trader = Mock(return_value=mock_ai_trader)
        competition_service.ai_engine.ai_states = {
            ai_id: {
                'daily_trades': 5,
                'total_profit': 125.0,
                'portfolio_value': 101250.0,
                'win_count': 3,
                'loss_count': 2,
                'active': True
            }
        }
        
        result = await competition_service.get_ai_trader_info(ai_id)
        
        assert result is not None
        assert result['id'] == ai_id
        assert result['name'] == "Captain Vega"
        assert result['strategy'] == "aggressive_growth"
        assert result['current_state']['total_trades'] == 5
        assert result['current_state']['active'] is True
    
    @pytest.mark.asyncio
    async def test_get_tournament_statistics(self, competition_service):
        """Test comprehensive tournament statistics"""
        tournament_id = "daily:2024-01-15"
        
        # Mock dependencies
        competition_service.get_tournament_metadata = AsyncMock(
            return_value={
                'status': 'active',
                'start_time': '2024-01-15T00:00:00Z',
                'end_time': '2024-01-16T00:00:00Z'
            }
        )
        
        competition_service.get_tournament_leaderboard = AsyncMock(
            return_value=[
                {'user_id': 'user_1', 'is_ai': False, 'rank': 1},
                {'user_id': 'ai:captain_vega', 'is_ai': True, 'rank': 2},
                {'user_id': 'user_2', 'is_ai': False, 'rank': 3}
            ]
        )
        
        competition_service.redis_client.llen.return_value = 150
        
        result = await competition_service.get_tournament_statistics(tournament_id)
        
        assert result['tournament_id'] == tournament_id
        assert result['status'] == 'active'
        assert result['human_players'] == 2
        assert result['ai_players'] == 1
        assert result['total_trades'] == 150
        assert len(result['top_performers']) <= 10
    
    @pytest.mark.asyncio
    async def test_health_check(self, competition_service):
        """Test service health check"""
        # Mock AI trading task
        competition_service.ai_trading_task = Mock()
        competition_service.ai_trading_task.done.return_value = False
        
        result = await competition_service.health_check()
        
        assert result['status'] == 'healthy'
        assert result['redis_connection'] == 'ok'
        assert result['ai_trading_status'] == 'running'
        assert 'current_tournament' in result
    
    @pytest.mark.asyncio 
    async def test_health_check_unhealthy(self, competition_service):
        """Test health check when service is unhealthy"""
        # Mock Redis failure
        competition_service.redis_client.ping.side_effect = Exception("Redis connection failed")
        
        result = await competition_service.health_check()
        
        assert result['status'] == 'unhealthy'
        assert 'error' in result

class TestTournamentLifecycle:
    """Test tournament lifecycle management"""
    
    @pytest.mark.asyncio
    async def test_complete_tournament_lifecycle(self, competition_service):
        """Test complete tournament from initialization to archival"""
        # 1. Initialize tournament
        await competition_service.initialize_daily_tournament()
        tournament_id = competition_service.get_current_tournament_id()
        
        # 2. Initialize AI traders
        competition_service.ai_engine.initialize_ai_states = Mock()
        competition_service.ai_engine.get_active_ai_traders = Mock(return_value=[
            Mock(id="ai:test_trader")
        ])
        competition_service.leaderboard_manager.update_score = AsyncMock()
        
        await competition_service.initialize_ai_traders(tournament_id)
        
        # 3. Process some trades
        trade_event = DomainEvent(
            event_type="trade_executed",
            domain="trading",
            entity_id="trade_1",
            data={'user_id': 'user_1', 'profit': 100.0, 'volume': 1000.0}
        )
        
        competition_service.scoring_engine.calculate_score_components = AsyncMock(
            return_value={'profit_factor': 80.0, 'win_rate': 70.0, 'volume': 40.0, 'consistency': 60.0}
        )
        
        await competition_service.process_trade_event(trade_event)
        
        # 4. Verify tournament state
        tournament_stats = await competition_service.get_tournament_statistics(tournament_id)
        assert tournament_stats['tournament_id'] == tournament_id
        
        # 5. Test health check
        health = await competition_service.health_check()
        assert health['status'] == 'healthy'

class TestConcurrentOperations:
    """Test concurrent operations and race conditions"""
    
    @pytest.mark.asyncio
    async def test_concurrent_leaderboard_updates(self, competition_service):
        """Test concurrent leaderboard updates don't cause race conditions"""
        # Mock scoring engine
        competition_service.scoring_engine.calculate_score_components = AsyncMock(
            return_value={'profit_factor': 75.0, 'win_rate': 65.0, 'volume': 35.0, 'consistency': 55.0}
        )
        competition_service.leaderboard_manager.update_score = AsyncMock()
        
        # Create multiple trade events
        trade_events = []
        for i in range(10):
            event = DomainEvent(
                event_type="trade_executed",
                domain="trading",
                entity_id=f"trade_{i}",
                data={
                    'user_id': f'user_{i % 3}',  # 3 users making trades
                    'profit': 50.0 + i * 10,
                    'volume': 1000.0
                }
            )
            trade_events.append(event)
        
        # Process all events concurrently
        tasks = [competition_service.process_trade_event(event) for event in trade_events]
        await asyncio.gather(*tasks)
        
        # Verify all events were processed
        assert competition_service.scoring_engine.calculate_score_components.call_count == 10
        assert competition_service.leaderboard_manager.update_score.call_count == 10
    
    @pytest.mark.asyncio
    async def test_ai_trading_concurrent_with_user_trades(self, competition_service):
        """Test AI trading cycles don't interfere with user trade processing"""
        # Setup mocks
        competition_service.ai_engine.run_ai_trading_cycle = AsyncMock(
            return_value={'trades_generated': 3, 'active_traders': 5}
        )
        competition_service.scoring_engine.calculate_score_components = AsyncMock(
            return_value={'profit_factor': 60.0, 'win_rate': 50.0, 'volume': 30.0, 'consistency': 40.0}
        )
        competition_service.leaderboard_manager.update_score = AsyncMock()
        competition_service.redis_client.hgetall.return_value = {'status': 'active'}
        
        # Simulate concurrent operations
        user_trade = DomainEvent(
            event_type="trade_executed",
            domain="trading",
            entity_id="user_trade",
            data={'user_id': 'user_1', 'profit': 100.0, 'volume': 2000.0}
        )
        
        tournament_id = competition_service.get_current_tournament_id()
        
        # Run AI cycle and user trade processing concurrently
        ai_task = competition_service.ai_engine.run_ai_trading_cycle(tournament_id)
        user_task = competition_service.process_trade_event(user_trade)
        
        ai_result, _ = await asyncio.gather(ai_task, user_task)
        
        # Verify both operations completed successfully
        assert ai_result['trades_generated'] == 3
        competition_service.scoring_engine.calculate_score_components.assert_called_once()

if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])