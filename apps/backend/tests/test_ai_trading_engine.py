import pytest
import asyncio
from datetime import datetime, timezone
from unittest.mock import Mock, AsyncMock, patch
import random
from typing import Dict, List

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from services.competition.ai_traders import (
    AITradingEngine, 
    AITraderPersonality, 
    TradingStrategy, 
    AI_TRADERS
)
from services.competition.ai_trading_strategies import (
    AITradingStrategies, 
    MarketConditionAnalyzer,
    TradingOpportunity
)

@pytest.fixture
def mock_market_analyzer():
    """Mock market condition analyzer"""
    analyzer = Mock(spec=MarketConditionAnalyzer)
    analyzer.get_current_conditions = AsyncMock(return_value={
        'hour': 14,
        'volatility': 0.03,
        'trend_strength': 0.7,
        'trend_direction': 'UP',
        'volume_profile': {'avg_volume': 1.2, 'volume_trend': 'INCREASING'},
        'market_sentiment': {'sentiment_score': 0.3, 'fear_greed_index': 65}
    })
    return analyzer

@pytest.fixture
def ai_trading_engine(mock_market_analyzer):
    """Create AI trading engine with mocked dependencies"""
    engine = AITradingEngine(market_data_service=mock_market_analyzer)
    return engine

@pytest.fixture
def ai_strategies(mock_market_analyzer):
    """Create AI trading strategies with mocked market analyzer"""
    return AITradingStrategies(mock_market_analyzer)

class TestAITraderPersonalities:
    """Test individual AI trader personalities"""
    
    def test_ai_traders_count(self):
        """Test that we have 20+ unique AI traders"""
        assert len(AI_TRADERS) >= 20, f"Should have at least 20 AI traders, got {len(AI_TRADERS)}"
    
    def test_ai_traders_unique_ids(self):
        """Test that all AI traders have unique IDs"""
        ids = [trader.id for trader in AI_TRADERS]
        assert len(ids) == len(set(ids)), "All AI trader IDs should be unique"
    
    def test_ai_traders_have_required_fields(self):
        """Test that all AI traders have required fields"""
        required_fields = ['id', 'name', 'title', 'strategy', 'risk_profile', 
                          'personality_traits', 'preferred_symbols', 'trading_hours', 'backstory']
        
        for trader in AI_TRADERS:
            for field in required_fields:
                assert hasattr(trader, field), f"Trader {trader.id} missing field: {field}"
                assert getattr(trader, field) is not None, f"Trader {trader.id} has None value for: {field}"
    
    def test_strategy_diversity(self):
        """Test that AI traders cover all trading strategies"""
        strategies_used = set(trader.strategy for trader in AI_TRADERS)
        all_strategies = set(TradingStrategy)
        
        # Should have good coverage of strategies
        coverage = len(strategies_used) / len(all_strategies)
        assert coverage >= 0.8, f"Strategy coverage is {coverage:.2%}, should be at least 80%"
    
    def test_risk_profile_validity(self):
        """Test that all risk profiles have valid values"""
        for trader in AI_TRADERS:
            risk_profile = trader.risk_profile
            
            # Check required keys
            required_keys = ['position_size', 'stop_loss', 'take_profit', 'max_daily_trades']
            for key in required_keys:
                assert key in risk_profile, f"Trader {trader.id} missing risk profile key: {key}"
            
            # Check value ranges
            assert 0.01 <= risk_profile['position_size'] <= 0.25, f"Invalid position_size for {trader.id}"
            assert 0.005 <= risk_profile['stop_loss'] <= 0.1, f"Invalid stop_loss for {trader.id}"
            assert 0.02 <= risk_profile['take_profit'] <= 0.5, f"Invalid take_profit for {trader.id}"
            assert 1 <= risk_profile['max_daily_trades'] <= 200, f"Invalid max_daily_trades for {trader.id}"
    
    def test_personality_traits_validity(self):
        """Test that personality traits are in valid ranges"""
        for trader in AI_TRADERS:
            traits = trader.personality_traits
            
            required_traits = ['confidence', 'patience', 'discipline', 'trade_frequency']
            for trait in required_traits:
                assert trait in traits, f"Trader {trader.id} missing trait: {trait}"
                assert 0.0 <= traits[trait] <= 1.0, f"Invalid {trait} value for {trader.id}: {traits[trait]}"
    
    def test_trading_hours_validity(self):
        """Test that trading hours are valid"""
        for trader in AI_TRADERS:
            hours = trader.trading_hours
            assert isinstance(hours, list), f"Trading hours should be list for {trader.id}"
            assert len(hours) > 0, f"Trading hours should not be empty for {trader.id}"
            for hour in hours:
                assert 0 <= hour <= 23, f"Invalid trading hour {hour} for {trader.id}"
    
    def test_preferred_symbols_validity(self):
        """Test that preferred symbols are valid"""
        for trader in AI_TRADERS:
            symbols = trader.preferred_symbols
            assert isinstance(symbols, list), f"Preferred symbols should be list for {trader.id}"
            assert len(symbols) > 0, f"Preferred symbols should not be empty for {trader.id}"
            
            # Check symbol format
            for symbol in symbols:
                assert isinstance(symbol, str), f"Symbol should be string for {trader.id}: {symbol}"
                assert len(symbol) >= 3, f"Symbol too short for {trader.id}: {symbol}"
    
    def test_should_trade_logic(self):
        """Test the should_trade method for different scenarios"""
        # Get a few different strategy types
        aggressive_trader = next(t for t in AI_TRADERS if t.strategy == TradingStrategy.AGGRESSIVE_GROWTH)
        conservative_trader = next(t for t in AI_TRADERS if t.strategy == TradingStrategy.CONSERVATIVE_VALUE)
        hft_trader = next(t for t in AI_TRADERS if t.strategy == TradingStrategy.HIGH_FREQUENCY)
        
        # Test during preferred hours with good conditions
        good_conditions = {
            'hour': aggressive_trader.trading_hours[0],
            'volatility': 0.04,
            'trend_strength': 0.8,
            'trend_direction': 'UP'
        }
        
        # HFT should always be willing to trade
        assert hft_trader.should_trade(good_conditions) == True
        
        # Test outside trading hours
        off_hours_conditions = {
            'hour': 23 if 23 not in aggressive_trader.trading_hours else 2,
            'volatility': 0.04,
            'trend_strength': 0.8
        }
        
        # Should have low probability outside trading hours
        trade_decisions = [aggressive_trader.should_trade(off_hours_conditions) for _ in range(50)]
        true_count = sum(trade_decisions)
        # Should be around 10% (5 out of 50), allow some variance
        assert true_count <= 15, f"Too many trades outside hours: {true_count}/50"

class TestAITradingEngine:
    """Test AI trading engine functionality"""
    
    def test_engine_initialization(self, ai_trading_engine):
        """Test that AI trading engine initializes correctly"""
        assert ai_trading_engine.ai_traders is not None
        assert len(ai_trading_engine.ai_traders) >= 20
        assert ai_trading_engine.ai_strategies is not None
        assert ai_trading_engine.market_data is not None
    
    def test_get_active_ai_traders(self, ai_trading_engine):
        """Test getting active AI traders"""
        traders = ai_trading_engine.get_active_ai_traders()
        assert len(traders) >= 20
        assert all(isinstance(trader, AITraderPersonality) for trader in traders)
    
    def test_get_ai_trader_by_id(self, ai_trading_engine):
        """Test getting specific AI trader by ID"""
        # Test existing trader
        trader = ai_trading_engine.get_ai_trader("ai:captain_vega")
        assert trader is not None
        assert trader.id == "ai:captain_vega"
        assert trader.name == "Captain Vega"
        
        # Test non-existing trader
        trader = ai_trading_engine.get_ai_trader("ai:nonexistent")
        assert trader is None
    
    def test_get_ai_traders_by_strategy(self, ai_trading_engine):
        """Test filtering AI traders by strategy"""
        aggressive_traders = ai_trading_engine.get_ai_traders_by_strategy(TradingStrategy.AGGRESSIVE_GROWTH)
        conservative_traders = ai_trading_engine.get_ai_traders_by_strategy(TradingStrategy.CONSERVATIVE_VALUE)
        
        assert len(aggressive_traders) > 0
        assert len(conservative_traders) > 0
        
        # Verify all traders have correct strategy
        for trader in aggressive_traders:
            assert trader.strategy == TradingStrategy.AGGRESSIVE_GROWTH
        
        for trader in conservative_traders:
            assert trader.strategy == TradingStrategy.CONSERVATIVE_VALUE
    
    def test_initialize_ai_states(self, ai_trading_engine):
        """Test AI state initialization for tournament"""
        tournament_id = "daily:2024-01-15"
        ai_trading_engine.initialize_ai_states(tournament_id)
        
        # Check that all AI traders have initialized states
        for ai_id in ai_trading_engine.ai_traders:
            assert ai_id in ai_trading_engine.ai_states
            state = ai_trading_engine.ai_states[ai_id]
            
            # Check state structure
            required_keys = ['tournament_id', 'positions', 'daily_trades', 'total_profit', 
                           'win_count', 'loss_count', 'portfolio_value', 'active']
            for key in required_keys:
                assert key in state, f"Missing state key {key} for {ai_id}"
            
            assert state['tournament_id'] == tournament_id
            assert state['active'] == True
            assert state['portfolio_value'] == 100000.0
    
    @pytest.mark.asyncio
    async def test_run_ai_trading_cycle(self, ai_trading_engine):
        """Test running complete AI trading cycle"""
        tournament_id = "daily:2024-01-15"
        ai_trading_engine.initialize_ai_states(tournament_id)
        
        result = await ai_trading_engine.run_ai_trading_cycle(tournament_id)
        
        assert 'trades_generated' in result
        assert 'active_traders' in result
        assert 'market_conditions' in result
        assert result['trades_generated'] >= 0
        assert result['active_traders'] > 0
    
    @pytest.mark.asyncio
    async def test_generate_ai_trade(self, ai_trading_engine):
        """Test AI trade generation"""
        tournament_id = "daily:2024-01-15"
        ai_trading_engine.initialize_ai_states(tournament_id)
        
        # Get a trader and generate trade
        trader = ai_trading_engine.get_ai_trader("ai:captain_vega")
        market_conditions = {
            'hour': 14,
            'volatility': 0.05,
            'trend_strength': 0.8,
            'trend_direction': 'UP'
        }
        
        trade = await ai_trading_engine.generate_ai_trade(trader, market_conditions)
        
        if trade is not None:  # Trade might be None if conditions don't match strategy
            assert 'ai_id' in trade
            assert 'symbol' in trade
            assert 'side' in trade
            assert 'amount' in trade
            assert trade['side'] in ['BUY', 'SELL']
            assert trade['amount'] > 0
            assert trade['symbol'] in trader.preferred_symbols
    
    @pytest.mark.asyncio
    async def test_execute_ai_trade(self, ai_trading_engine):
        """Test AI trade execution"""
        tournament_id = "daily:2024-01-15"
        ai_trading_engine.initialize_ai_states(tournament_id)
        
        trader = ai_trading_engine.get_ai_trader("ai:captain_vega")
        mock_trade = {
            'ai_id': trader.id,
            'symbol': 'BTC-USD',
            'side': 'BUY',
            'amount': 5000.0,
            'current_price': 45000.0
        }
        
        success = await ai_trading_engine.execute_ai_trade(trader, mock_trade, tournament_id)
        assert success == True
        
        # Check that state was updated
        state = ai_trading_engine.ai_states[trader.id]
        assert state['daily_trades'] == 1
        assert len(state['positions']) == 1
        assert state['last_trade_time'] is not None
    
    def test_get_ai_leaderboard_stats(self, ai_trading_engine):
        """Test getting AI leaderboard statistics"""
        tournament_id = "daily:2024-01-15"
        ai_trading_engine.initialize_ai_states(tournament_id)
        
        # Simulate some trades
        for ai_id in list(ai_trading_engine.ai_states.keys())[:3]:
            state = ai_trading_engine.ai_states[ai_id]
            state['daily_trades'] = 5
            state['total_profit'] = 150.0
            state['win_count'] = 3
            state['loss_count'] = 2
        
        stats = ai_trading_engine.get_ai_leaderboard_stats()
        
        assert len(stats) >= 3
        for stat in stats[:3]:
            assert stat['is_ai'] == True
            assert stat['daily_trades'] == 5
            assert stat['total_profit'] == 150.0
            assert stat['win_rate'] == 60.0  # 3/5 * 100

class TestAITradingStrategies:
    """Test AI trading strategy implementations"""
    
    @pytest.mark.asyncio
    async def test_aggressive_growth_strategy(self, ai_strategies):
        """Test aggressive growth strategy"""
        # Create aggressive trader
        trader = next(t for t in AI_TRADERS if t.strategy == TradingStrategy.AGGRESSIVE_GROWTH)
        
        market_conditions = {
            'hour': 14,
            'volatility': 0.05,
            'trend_strength': 0.8,
            'trend_direction': 'UP'
        }
        
        # Mock high momentum stocks
        with patch.object(ai_strategies.market_data, 'get_high_momentum_stocks', new_callable=AsyncMock) as mock_momentum:
            mock_momentum.return_value = [
                {'symbol': 'BTC-USD', 'price': 45000, 'momentum': 0.8}
            ]
            
            opportunity = await ai_strategies.aggressive_growth_strategy(trader, market_conditions)
            
            if opportunity:
                assert opportunity.symbol == 'BTC-USD'
                assert opportunity.direction in ['BUY', 'SELL']
                assert opportunity.signal_strength > 0
    
    @pytest.mark.asyncio
    async def test_conservative_value_strategy(self, ai_strategies):
        """Test conservative value strategy"""
        trader = next(t for t in AI_TRADERS if t.strategy == TradingStrategy.CONSERVATIVE_VALUE)
        
        # Low volatility conditions (preferred by conservative strategy)
        market_conditions = {
            'hour': 12,
            'volatility': 0.015,  # Low volatility
            'trend_strength': 0.4,
            'trend_direction': 'UP'
        }
        
        opportunity = await ai_strategies.conservative_value_strategy(trader, market_conditions)
        
        # Conservative strategy should be more selective
        if opportunity:
            assert opportunity.symbol in ['SPY', 'AAPL', 'MSFT', 'JNJ', 'PG', 'KO', 'BRK-B']
            assert opportunity.risk_reward_ratio > 1.0  # Should have good risk/reward
    
    @pytest.mark.asyncio
    async def test_high_frequency_strategy(self, ai_strategies):
        """Test high frequency trading strategy"""
        trader = next(t for t in AI_TRADERS if t.strategy == TradingStrategy.HIGH_FREQUENCY)
        
        market_conditions = {
            'hour': 15,
            'volatility': 0.03,
            'trend_strength': 0.6
        }
        
        # Mock micro opportunities
        with patch.object(ai_strategies, '_identify_micro_opportunities', new_callable=AsyncMock) as mock_micro:
            mock_micro.return_value = [
                {
                    'symbol': 'BTC-USD',
                    'direction': 'BUY',
                    'entry_price': 45000,
                    'stop_price': 44950,
                    'target_price': 45100,
                    'signal_strength': 0.8,
                    'risk_reward': 2.0
                }
            ]
            
            opportunity = await ai_strategies.high_frequency_strategy(trader, market_conditions)
            
            if opportunity:
                assert opportunity.expected_duration <= 15  # Short duration for HFT
                assert opportunity.signal_strength > 0.5
    
    @pytest.mark.asyncio
    async def test_momentum_strategy(self, ai_strategies):
        """Test momentum trading strategy"""
        trader = next(t for t in AI_TRADERS if t.strategy == TradingStrategy.MOMENTUM)
        
        market_conditions = {
            'hour': 13,
            'volatility': 0.04,
            'trend_strength': 0.75,
            'trend_direction': 'UP'
        }
        
        # Mock trending symbols
        with patch.object(ai_strategies.market_data, 'get_trending_symbols', new_callable=AsyncMock) as mock_trending:
            mock_trending.return_value = [
                {
                    'symbol': 'TSLA',
                    'current_price': 250,
                    'trend': 'UP',
                    'trend_strength': 0.8,
                    'pullback_percentage': 0.02,
                    'support_level': 240,
                    'resistance_level': 270
                }
            ]
            
            opportunity = await ai_strategies.momentum_strategy(trader, market_conditions)
            
            if opportunity:
                assert opportunity.direction == 'BUY'  # Should buy on uptrend pullback
                assert opportunity.symbol == 'TSLA'
    
    @pytest.mark.asyncio
    async def test_contrarian_strategy(self, ai_strategies):
        """Test contrarian trading strategy"""
        trader = next(t for t in AI_TRADERS if t.strategy == TradingStrategy.CONTRARIAN)
        
        # Extreme bearish sentiment (contrarian opportunity)
        market_conditions = {
            'hour': 14,
            'volatility': 0.06,  # High volatility
            'trend_strength': 0.5,
            'market_sentiment': {
                'sentiment_score': -0.7,  # Very bearish
                'fear_greed_index': 25
            }
        }
        
        opportunity = await ai_strategies.contrarian_strategy(trader, market_conditions)
        
        if opportunity:
            assert opportunity.direction == 'BUY'  # Should buy when sentiment is very bearish
            assert opportunity.signal_strength >= 0.6  # Strong contrarian signal
    
    @pytest.mark.asyncio
    async def test_scalper_strategy(self, ai_strategies):
        """Test scalping strategy"""
        trader = next(t for t in AI_TRADERS if t.strategy == TradingStrategy.SCALPER)
        
        market_conditions = {
            'hour': 11,
            'volatility': 0.025,  # Sufficient for scalping
            'trend_strength': 0.4
        }
        
        opportunity = await ai_strategies.scalper_strategy(trader, market_conditions)
        
        if opportunity:
            assert opportunity.expected_duration <= 15  # Very short duration
            # Small profit targets relative to entry price
            profit_target = abs(opportunity.target_price - opportunity.entry_price) / opportunity.entry_price
            assert profit_target <= 0.01  # Should be <= 1%

class TestStrategyDistribution:
    """Test strategy distribution and balance"""
    
    def test_strategy_balance(self):
        """Test that strategies are reasonably balanced across AI traders"""
        strategy_counts = {}
        for strategy in TradingStrategy:
            strategy_counts[strategy] = sum(1 for trader in AI_TRADERS if trader.strategy == strategy)
        
        total_traders = len(AI_TRADERS)
        
        # Each strategy should have at least 1 trader
        for strategy, count in strategy_counts.items():
            assert count >= 1, f"Strategy {strategy} should have at least 1 trader, got {count}"
        
        # No single strategy should dominate (>50% of traders)
        max_count = max(strategy_counts.values())
        assert max_count <= total_traders * 0.5, f"No strategy should have >50% of traders, max is {max_count}/{total_traders}"
    
    def test_personality_diversity(self):
        """Test diversity in personality traits"""
        # Collect all confidence values
        confidence_values = [trader.personality_traits['confidence'] for trader in AI_TRADERS]
        
        # Should have good spread
        min_confidence = min(confidence_values)
        max_confidence = max(confidence_values)
        assert max_confidence - min_confidence >= 0.5, "Should have diverse confidence levels"
        
        # Similar tests for other traits
        patience_values = [trader.personality_traits['patience'] for trader in AI_TRADERS]
        min_patience = min(patience_values)
        max_patience = max(patience_values)
        assert max_patience - min_patience >= 0.5, "Should have diverse patience levels"

class TestMarketConditionAnalyzer:
    """Test market condition analysis"""
    
    @pytest.mark.asyncio
    async def test_get_current_conditions(self, mock_market_analyzer):
        """Test market condition analysis"""
        conditions = await mock_market_analyzer.get_current_conditions()
        
        required_keys = ['hour', 'volatility', 'trend_strength', 'trend_direction', 
                        'volume_profile', 'market_sentiment']
        
        for key in required_keys:
            assert key in conditions, f"Missing market condition key: {key}"
        
        # Test value ranges
        assert 0 <= conditions['hour'] <= 23
        assert 0 <= conditions['volatility'] <= 1
        assert 0 <= conditions['trend_strength'] <= 1
        assert conditions['trend_direction'] in ['UP', 'DOWN', 'SIDEWAYS']

class TestPerformanceAndScaling:
    """Test performance characteristics"""
    
    @pytest.mark.asyncio
    async def test_multiple_ai_traders_performance(self, ai_trading_engine):
        """Test performance with all AI traders active"""
        tournament_id = "daily:2024-01-15"
        ai_trading_engine.initialize_ai_states(tournament_id)
        
        # Run trading cycle multiple times
        start_time = datetime.now()
        
        for _ in range(5):
            result = await ai_trading_engine.run_ai_trading_cycle(tournament_id)
            assert result['active_traders'] > 0
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Should complete 5 cycles reasonably quickly
        assert duration < 10, f"5 AI trading cycles took too long: {duration}s"
    
    @pytest.mark.asyncio
    async def test_concurrent_ai_trade_generation(self, ai_trading_engine):
        """Test concurrent trade generation doesn't cause issues"""
        tournament_id = "daily:2024-01-15"
        ai_trading_engine.initialize_ai_states(tournament_id)
        
        market_conditions = {
            'hour': 14,
            'volatility': 0.04,
            'trend_strength': 0.7,
            'trend_direction': 'UP'
        }
        
        # Generate trades for multiple AI traders concurrently
        traders = ai_trading_engine.get_active_ai_traders()[:5]  # Test with first 5
        
        trade_tasks = [
            ai_trading_engine.generate_ai_trade(trader, market_conditions)
            for trader in traders
        ]
        
        trades = await asyncio.gather(*trade_tasks, return_exceptions=True)
        
        # Should not have any exceptions
        for trade in trades:
            assert not isinstance(trade, Exception), f"Trade generation failed: {trade}"

if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])