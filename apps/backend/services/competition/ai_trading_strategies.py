import numpy as np
from typing import Dict, Optional, List, Tuple
import random
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

@dataclass
class MarketSignal:
    """Represents a trading signal from market analysis"""
    symbol: str
    signal_type: str
    strength: float  # 0.0 to 1.0
    direction: str   # 'BUY' or 'SELL'
    confidence: float
    timeframe: str
    indicators: Dict[str, float]

@dataclass
class TradingOpportunity:
    """Represents a specific trading opportunity"""
    symbol: str
    direction: str
    entry_price: float
    stop_price: float
    target_price: float
    signal_strength: float
    expected_duration: int  # in minutes
    risk_reward_ratio: float

class MarketConditionAnalyzer:
    """Analyzes market conditions for AI trading strategies"""
    
    def __init__(self):
        self.price_history = {}  # Symbol -> price history
        self.indicators_cache = {}
        
    async def get_current_conditions(self) -> Dict:
        """Get comprehensive market conditions"""
        # This would integrate with real market data in production
        conditions = {
            'hour': datetime.now().hour,
            'volatility': self._calculate_market_volatility(),
            'trend_strength': self._calculate_trend_strength(),
            'trend_direction': self._determine_trend_direction(),
            'volume_profile': self._analyze_volume_profile(),
            'market_sentiment': self._assess_market_sentiment(),
            'correlation_matrix': self._calculate_correlations(),
            'support_resistance': self._identify_key_levels()
        }
        return conditions
    
    def _calculate_market_volatility(self) -> float:
        """Calculate current market volatility (0.0 to 1.0)"""
        # Mock implementation - would use real VIX or calculated volatility
        base_volatility = random.uniform(0.01, 0.08)
        time_factor = self._get_time_volatility_factor()
        return min(base_volatility * time_factor, 1.0)
    
    def _calculate_trend_strength(self) -> float:
        """Calculate overall trend strength (0.0 to 1.0)"""
        # Mock trend strength calculation
        return random.uniform(0.2, 0.9)
    
    def _determine_trend_direction(self) -> str:
        """Determine overall market trend direction"""
        return random.choice(['UP', 'DOWN', 'SIDEWAYS'])
    
    def _analyze_volume_profile(self) -> Dict:
        """Analyze current volume patterns"""
        return {
            'avg_volume': random.uniform(0.5, 2.0),  # Relative to normal
            'volume_trend': random.choice(['INCREASING', 'DECREASING', 'STABLE']),
            'unusual_activity': random.random() < 0.1  # 10% chance of unusual activity
        }
    
    def _assess_market_sentiment(self) -> Dict:
        """Assess overall market sentiment"""
        sentiment_score = random.uniform(-1.0, 1.0)  # -1 = very bearish, +1 = very bullish
        return {
            'sentiment_score': sentiment_score,
            'fear_greed_index': (sentiment_score + 1) * 50,  # Convert to 0-100 scale
            'sentiment_label': self._sentiment_label(sentiment_score)
        }
    
    def _sentiment_label(self, score: float) -> str:
        """Convert sentiment score to label"""
        if score > 0.5: return 'VERY_BULLISH'
        elif score > 0.2: return 'BULLISH'
        elif score > -0.2: return 'NEUTRAL'
        elif score > -0.5: return 'BEARISH'
        else: return 'VERY_BEARISH'
    
    def _calculate_correlations(self) -> Dict:
        """Calculate asset correlations"""
        # Mock correlation matrix
        return {
            'BTC_ETH': random.uniform(0.6, 0.9),
            'SPY_QQQ': random.uniform(0.8, 0.95),
            'USD_EUR': random.uniform(-0.3, 0.3)
        }
    
    def _identify_key_levels(self) -> Dict:
        """Identify support and resistance levels"""
        return {
            'SPY': {'support': [440, 435, 430], 'resistance': [460, 465, 470]},
            'BTC-USD': {'support': [42000, 40000, 38000], 'resistance': [48000, 50000, 52000]},
            'ETH-USD': {'support': [2800, 2600, 2400], 'resistance': [3200, 3400, 3600]}
        }
    
    def _get_time_volatility_factor(self) -> float:
        """Get volatility multiplier based on time of day"""
        hour = datetime.now().hour
        if 9 <= hour <= 10 or 15 <= hour <= 16:  # Market open/close
            return 1.5
        elif 11 <= hour <= 14:  # Mid-day
            return 0.8
        else:  # After hours
            return 1.2

class AITradingStrategies:
    """Implementation of different AI trading strategies"""
    
    def __init__(self, market_analyzer: MarketConditionAnalyzer):
        self.market_analyzer = market_analyzer
        self.strategy_performance = {}  # Track strategy performance
        
    async def aggressive_growth_strategy(self, ai_trader, market_conditions: Dict) -> Optional[TradingOpportunity]:
        """
        Aggressive growth: Large positions on high momentum stocks.
        Looks for breakouts and strong trends.
        """
        # Focus on high-momentum, volatile symbols
        momentum_symbols = await self._get_high_momentum_symbols(ai_trader.preferred_symbols)
        
        if not momentum_symbols:
            return None
            
        # Select highest momentum symbol
        target_symbol = momentum_symbols[0]['symbol']
        momentum_score = momentum_symbols[0]['momentum']
        current_price = momentum_symbols[0]['price']
        
        # Only trade if strong momentum and trend alignment
        if momentum_score < 0.6 or market_conditions['trend_strength'] < 0.5:
            return None
        
        # Determine direction based on momentum and trend
        if momentum_score > 0.8 and market_conditions['trend_direction'] == 'UP':
            direction = 'BUY'
            entry_price = current_price * 1.002  # Slight premium for aggressive entry
            stop_price = current_price * (1 - ai_trader.risk_profile['stop_loss'])
            target_price = current_price * (1 + ai_trader.risk_profile['take_profit'])
        elif momentum_score < -0.6 and market_conditions['trend_direction'] == 'DOWN':
            direction = 'SELL'
            entry_price = current_price * 0.998  # Slight discount for aggressive short
            stop_price = current_price * (1 + ai_trader.risk_profile['stop_loss'])
            target_price = current_price * (1 - ai_trader.risk_profile['take_profit'])
        else:
            return None
        
        return TradingOpportunity(
            symbol=target_symbol,
            direction=direction,
            entry_price=entry_price,
            stop_price=stop_price,
            target_price=target_price,
            signal_strength=momentum_score,
            expected_duration=120,  # 2 hours
            risk_reward_ratio=abs(target_price - entry_price) / abs(entry_price - stop_price)
        )
    
    async def high_frequency_strategy(self, ai_trader, market_conditions: Dict) -> Optional[TradingOpportunity]:
        """
        HFT: Small, frequent trades on micro price movements.
        Uses technical indicators and order book imbalances.
        """
        # Get micro opportunities from order book analysis
        micro_opportunities = await self._identify_micro_opportunities(ai_trader.preferred_symbols)
        
        if not micro_opportunities:
            return None
        
        # Filter for high-probability opportunities
        high_prob_ops = [op for op in micro_opportunities if op['signal_strength'] > 0.7]
        
        if not high_prob_ops:
            return None
        
        opportunity = random.choice(high_prob_ops)
        
        return TradingOpportunity(
            symbol=opportunity['symbol'],
            direction=opportunity['direction'],
            entry_price=opportunity['entry_price'],
            stop_price=opportunity['stop_price'],
            target_price=opportunity['target_price'],
            signal_strength=opportunity['signal_strength'],
            expected_duration=random.randint(1, 10),  # 1-10 minutes
            risk_reward_ratio=opportunity.get('risk_reward', 1.5)
        )
    
    async def momentum_strategy(self, ai_trader, market_conditions: Dict) -> Optional[TradingOpportunity]:
        """
        Momentum: Rides existing trends, enters on pullbacks.
        Uses moving averages and relative strength.
        """
        trending_symbols = await self._get_trending_symbols(ai_trader.preferred_symbols)
        
        for symbol_data in trending_symbols:
            # Look for pullback in strong uptrend
            if (symbol_data['trend'] == 'UP' and 
                symbol_data['pullback_percentage'] > 0.015 and 
                symbol_data['trend_strength'] > 0.6):
                
                current_price = symbol_data['current_price']
                support_level = symbol_data.get('support_level', current_price * 0.97)
                resistance_level = symbol_data.get('resistance_level', current_price * 1.08)
                
                return TradingOpportunity(
                    symbol=symbol_data['symbol'],
                    direction='BUY',
                    entry_price=current_price * 0.999,  # Buy on slight dip
                    stop_price=support_level,
                    target_price=resistance_level,
                    signal_strength=symbol_data['trend_strength'],
                    expected_duration=random.randint(30, 240),  # 30 minutes to 4 hours
                    risk_reward_ratio=(resistance_level - current_price) / (current_price - support_level)
                )
            
            # Look for breakdown in strong downtrend
            elif (symbol_data['trend'] == 'DOWN' and 
                  symbol_data['bounce_percentage'] > 0.01 and 
                  symbol_data['trend_strength'] > 0.6):
                
                current_price = symbol_data['current_price']
                resistance_level = symbol_data.get('resistance_level', current_price * 1.03)
                support_level = symbol_data.get('support_level', current_price * 0.92)
                
                return TradingOpportunity(
                    symbol=symbol_data['symbol'],
                    direction='SELL',
                    entry_price=current_price * 1.001,  # Sell on slight bounce
                    stop_price=resistance_level,
                    target_price=support_level,
                    signal_strength=symbol_data['trend_strength'],
                    expected_duration=random.randint(45, 300),  # 45 minutes to 5 hours
                    risk_reward_ratio=(current_price - support_level) / (resistance_level - current_price)
                )
        
        return None
    
    async def conservative_value_strategy(self, ai_trader, market_conditions: Dict) -> Optional[TradingOpportunity]:
        """
        Conservative Value: Focus on stable, low-risk opportunities.
        Prefers blue-chip stocks and low volatility conditions.
        """
        # Only trade in low volatility conditions
        if market_conditions['volatility'] > 0.03:
            return None
        
        # Focus on stable symbols
        stable_symbols = [s for s in ai_trader.preferred_symbols 
                         if s in ['SPY', 'AAPL', 'MSFT', 'JNJ', 'PG', 'KO', 'BRK-B']]
        
        if not stable_symbols:
            return None
        
        symbol = random.choice(stable_symbols)
        current_price = self._get_mock_price(symbol)
        
        # Look for mean reversion opportunities
        price_deviation = self._calculate_price_deviation(symbol, current_price)
        
        if abs(price_deviation) < 0.01:  # Not enough deviation
            return None
        
        if price_deviation < -0.015:  # Price below mean, buy opportunity
            return TradingOpportunity(
                symbol=symbol,
                direction='BUY',
                entry_price=current_price,
                stop_price=current_price * (1 - ai_trader.risk_profile['stop_loss']),
                target_price=current_price * (1 + ai_trader.risk_profile['take_profit']),
                signal_strength=abs(price_deviation) * 10,  # Convert to 0-1 scale
                expected_duration=random.randint(240, 1440),  # 4-24 hours
                risk_reward_ratio=ai_trader.risk_profile['take_profit'] / ai_trader.risk_profile['stop_loss']
            )
        
        return None
    
    async def contrarian_strategy(self, ai_trader, market_conditions: Dict) -> Optional[TradingOpportunity]:
        """
        Contrarian: Goes against prevailing market sentiment.
        Looks for oversold/overbought conditions and sentiment extremes.
        """
        sentiment = market_conditions['market_sentiment']
        volatility = market_conditions['volatility']
        
        # Only trade when sentiment is extreme and volatility is high
        if abs(sentiment['sentiment_score']) < 0.6 or volatility < 0.025:
            return None
        
        # Choose volatile symbols for contrarian plays
        volatile_symbols = [s for s in ai_trader.preferred_symbols 
                          if s in ['VIX', 'SQQQ', 'SPXS', 'UVXY', 'GME', 'AMC']]
        
        if not volatile_symbols:
            volatile_symbols = ai_trader.preferred_symbols
        
        symbol = random.choice(volatile_symbols)
        current_price = self._get_mock_price(symbol)
        
        # Contrarian logic: buy when very bearish, sell when very bullish
        if sentiment['sentiment_score'] < -0.6:  # Very bearish, buy
            direction = 'BUY'
            entry_price = current_price
            stop_price = current_price * (1 - ai_trader.risk_profile['stop_loss'])
            target_price = current_price * (1 + ai_trader.risk_profile['take_profit'])
        elif sentiment['sentiment_score'] > 0.6:  # Very bullish, sell
            direction = 'SELL'
            entry_price = current_price
            stop_price = current_price * (1 + ai_trader.risk_profile['stop_loss'])
            target_price = current_price * (1 - ai_trader.risk_profile['take_profit'])
        else:
            return None
        
        return TradingOpportunity(
            symbol=symbol,
            direction=direction,
            entry_price=entry_price,
            stop_price=stop_price,
            target_price=target_price,
            signal_strength=abs(sentiment['sentiment_score']),
            expected_duration=random.randint(60, 480),  # 1-8 hours
            risk_reward_ratio=ai_trader.risk_profile['take_profit'] / ai_trader.risk_profile['stop_loss']
        )
    
    async def balanced_strategy(self, ai_trader, market_conditions: Dict) -> Optional[TradingOpportunity]:
        """
        Balanced: Combines multiple strategies based on market conditions.
        Adapts approach based on volatility, trend, and sentiment.
        """
        volatility = market_conditions['volatility']
        trend_strength = market_conditions['trend_strength']
        sentiment_score = market_conditions['market_sentiment']['sentiment_score']
        
        # Choose sub-strategy based on market conditions
        if volatility > 0.04 and abs(sentiment_score) > 0.5:
            # High volatility + extreme sentiment -> Use contrarian approach
            return await self.contrarian_strategy(ai_trader, market_conditions)
        
        elif trend_strength > 0.7:
            # Strong trend -> Use momentum approach
            return await self.momentum_strategy(ai_trader, market_conditions)
        
        elif volatility < 0.02:
            # Low volatility -> Use conservative approach
            return await self.conservative_value_strategy(ai_trader, market_conditions)
        
        else:
            # Mixed conditions -> Use moderate aggressive approach
            return await self._moderate_growth_approach(ai_trader, market_conditions)
    
    async def scalper_strategy(self, ai_trader, market_conditions: Dict) -> Optional[TradingOpportunity]:
        """
        Scalper: Very short-term trades on micro price movements.
        High frequency with small profit targets.
        """
        # Need high volatility for scalping opportunities
        if market_conditions['volatility'] < 0.015:
            return None
        
        # Focus on liquid symbols
        liquid_symbols = [s for s in ai_trader.preferred_symbols 
                         if s in ['SPY', 'QQQ', 'BTC-USD', 'ETH-USD', 'EUR-USD']]
        
        if not liquid_symbols:
            return None
        
        symbol = random.choice(liquid_symbols)
        current_price = self._get_mock_price(symbol)
        
        # Generate micro price levels
        micro_movement = current_price * random.uniform(0.001, 0.005)  # 0.1% to 0.5%
        direction = random.choice(['BUY', 'SELL'])
        
        if direction == 'BUY':
            entry_price = current_price
            target_price = current_price + micro_movement
            stop_price = current_price - (micro_movement * 0.8)  # Tight stop
        else:
            entry_price = current_price
            target_price = current_price - micro_movement
            stop_price = current_price + (micro_movement * 0.8)
        
        return TradingOpportunity(
            symbol=symbol,
            direction=direction,
            entry_price=entry_price,
            stop_price=stop_price,
            target_price=target_price,
            signal_strength=market_conditions['volatility'] * 20,  # Scale volatility to signal strength
            expected_duration=random.randint(1, 15),  # 1-15 minutes
            risk_reward_ratio=1.25  # Slightly positive risk/reward for scalping
        )
    
    async def swing_strategy(self, ai_trader, market_conditions: Dict) -> Optional[TradingOpportunity]:
        """
        Swing: Medium-term trades capturing price swings.
        Uses technical analysis and pattern recognition.
        """
        # Look for swing opportunities in preferred symbols
        swing_opportunities = await self._identify_swing_patterns(ai_trader.preferred_symbols)
        
        if not swing_opportunities:
            return None
        
        # Filter for high-quality swing setups
        quality_setups = [op for op in swing_opportunities if op['pattern_strength'] > 0.6]
        
        if not quality_setups:
            return None
        
        setup = random.choice(quality_setups)
        
        return TradingOpportunity(
            symbol=setup['symbol'],
            direction=setup['direction'],
            entry_price=setup['entry_price'],
            stop_price=setup['stop_price'],
            target_price=setup['target_price'],
            signal_strength=setup['pattern_strength'],
            expected_duration=random.randint(480, 2880),  # 8 hours to 2 days
            risk_reward_ratio=setup.get('risk_reward', 2.0)
        )
    
    # Helper methods
    async def _get_high_momentum_symbols(self, symbols: List[str]) -> List[Dict]:
        """Get symbols with high momentum scores"""
        momentum_data = []
        
        for symbol in symbols:
            price = self._get_mock_price(symbol)
            momentum = random.uniform(-1.0, 1.0)  # Mock momentum score
            
            if abs(momentum) > 0.3:  # Only include significant momentum
                momentum_data.append({
                    'symbol': symbol,
                    'price': price,
                    'momentum': momentum
                })
        
        return sorted(momentum_data, key=lambda x: abs(x['momentum']), reverse=True)
    
    async def _identify_micro_opportunities(self, symbols: List[str]) -> List[Dict]:
        """Identify HFT opportunities from order book analysis"""
        opportunities = []
        
        for symbol in symbols:
            if random.random() > 0.3:  # 30% chance per symbol
                continue
                
            current_price = self._get_mock_price(symbol)
            
            # Simulate order book imbalance
            imbalance = random.uniform(-0.8, 0.8)
            
            if abs(imbalance) > 0.4:  # Significant imbalance
                direction = 'BUY' if imbalance > 0 else 'SELL'
                spread = current_price * 0.001  # 0.1% spread
                
                opportunities.append({
                    'symbol': symbol,
                    'direction': direction,
                    'entry_price': current_price,
                    'stop_price': current_price - spread * 2 if direction == 'BUY' else current_price + spread * 2,
                    'target_price': current_price + spread * 3 if direction == 'BUY' else current_price - spread * 3,
                    'signal_strength': abs(imbalance),
                    'risk_reward': 1.5
                })
        
        return opportunities
    
    async def _get_trending_symbols(self, symbols: List[str]) -> List[Dict]:
        """Get symbols with trend analysis"""
        trending_data = []
        
        for symbol in symbols:
            price = self._get_mock_price(symbol)
            trend_strength = random.uniform(0.0, 1.0)
            trend_direction = random.choice(['UP', 'DOWN', 'SIDEWAYS'])
            
            if trend_strength > 0.4:  # Only include meaningful trends
                trending_data.append({
                    'symbol': symbol,
                    'current_price': price,
                    'trend': trend_direction,
                    'trend_strength': trend_strength,
                    'pullback_percentage': random.uniform(0.005, 0.03) if trend_direction == 'UP' else 0,
                    'bounce_percentage': random.uniform(0.005, 0.02) if trend_direction == 'DOWN' else 0,
                    'support_level': price * random.uniform(0.94, 0.98),
                    'resistance_level': price * random.uniform(1.02, 1.08)
                })
        
        return trending_data
    
    async def _moderate_growth_approach(self, ai_trader, market_conditions: Dict) -> Optional[TradingOpportunity]:
        """Moderate growth approach for balanced strategy"""
        symbol = random.choice(ai_trader.preferred_symbols)
        current_price = self._get_mock_price(symbol)
        
        # Moderate risk/reward setup
        direction = random.choice(['BUY', 'SELL'])
        position_size = ai_trader.risk_profile['position_size'] * 0.8  # Slightly smaller position
        
        if direction == 'BUY':
            stop_price = current_price * (1 - ai_trader.risk_profile['stop_loss'] * 0.7)
            target_price = current_price * (1 + ai_trader.risk_profile['take_profit'] * 0.8)
        else:
            stop_price = current_price * (1 + ai_trader.risk_profile['stop_loss'] * 0.7)
            target_price = current_price * (1 - ai_trader.risk_profile['take_profit'] * 0.8)
        
        return TradingOpportunity(
            symbol=symbol,
            direction=direction,
            entry_price=current_price,
            stop_price=stop_price,
            target_price=target_price,
            signal_strength=0.5,  # Moderate signal strength
            expected_duration=random.randint(120, 480),  # 2-8 hours
            risk_reward_ratio=1.2
        )
    
    async def _identify_swing_patterns(self, symbols: List[str]) -> List[Dict]:
        """Identify swing trading patterns"""
        patterns = []
        
        for symbol in symbols:
            if random.random() > 0.4:  # 40% chance per symbol
                continue
                
            price = self._get_mock_price(symbol)
            pattern_type = random.choice(['BULLISH_FLAG', 'BEARISH_FLAG', 'DOUBLE_BOTTOM', 'DOUBLE_TOP'])
            pattern_strength = random.uniform(0.3, 1.0)
            
            if pattern_type in ['BULLISH_FLAG', 'DOUBLE_BOTTOM']:
                direction = 'BUY'
                target_price = price * random.uniform(1.05, 1.15)
                stop_price = price * random.uniform(0.92, 0.97)
            else:
                direction = 'SELL'
                target_price = price * random.uniform(0.85, 0.95)
                stop_price = price * random.uniform(1.03, 1.08)
            
            patterns.append({
                'symbol': symbol,
                'direction': direction,
                'entry_price': price,
                'stop_price': stop_price,
                'target_price': target_price,
                'pattern_type': pattern_type,
                'pattern_strength': pattern_strength,
                'risk_reward': abs(target_price - price) / abs(price - stop_price)
            })
        
        return patterns
    
    def _get_mock_price(self, symbol: str) -> float:
        """Get mock price for symbol"""
        mock_prices = {
            'BTC-USD': 45000, 'ETH-USD': 3000, 'AAPL': 180, 'TSLA': 250,
            'SPY': 450, 'QQQ': 380, 'EUR-USD': 1.08, 'GBP-USD': 1.25,
            'NVDA': 500, 'MSFT': 350, 'GOOGL': 140, 'AMZN': 150,
            'JNJ': 160, 'PG': 140, 'KO': 60, 'BRK-B': 350,
            'VIX': 20, 'SQQQ': 15, 'SPXS': 8, 'UVXY': 12
        }
        base_price = mock_prices.get(symbol, 100.0)
        # Add small random variation
        return base_price * (1 + random.uniform(-0.02, 0.02))
    
    def _calculate_price_deviation(self, symbol: str, current_price: float) -> float:
        """Calculate how much current price deviates from moving average"""
        # Mock calculation - would use real price history
        moving_average = current_price * random.uniform(0.98, 1.02)
        return (current_price - moving_average) / moving_average