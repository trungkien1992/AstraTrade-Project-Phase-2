from dataclasses import dataclass
from typing import Dict, List, Optional
from enum import Enum
import random
import numpy as np
from datetime import datetime, time
from .ai_trading_strategies import AITradingStrategies, MarketConditionAnalyzer

class TradingStrategy(Enum):
    AGGRESSIVE_GROWTH = "aggressive_growth"
    CONSERVATIVE_VALUE = "conservative_value"
    HIGH_FREQUENCY = "high_frequency"
    MOMENTUM = "momentum"
    CONTRARIAN = "contrarian"
    BALANCED = "balanced"
    SCALPER = "scalper"
    SWING = "swing"

@dataclass
class AITraderPersonality:
    """Defines an AI trader's characteristics and behavior"""
    id: str
    name: str
    title: str
    strategy: TradingStrategy
    risk_profile: Dict[str, float]
    personality_traits: Dict[str, float]
    preferred_symbols: List[str]
    trading_hours: List[int]
    backstory: str
    
    def should_trade(self, market_conditions: Dict) -> bool:
        """Determine if this AI should trade given current conditions"""
        current_hour = market_conditions.get('hour', 12)
        volatility = market_conditions.get('volatility', 0.02)
        trend_strength = market_conditions.get('trend_strength', 0.5)
        
        # Check if it's preferred trading time
        if current_hour not in self.trading_hours:
            return random.random() < 0.1  # 10% chance outside preferred hours
            
        # Strategy-specific trading conditions
        if self.strategy == TradingStrategy.HIGH_FREQUENCY:
            return True  # Always ready to trade
        elif self.strategy == TradingStrategy.MOMENTUM:
            return volatility > 0.02 and trend_strength > 0.6  # Needs movement and trend
        elif self.strategy == TradingStrategy.CONSERVATIVE_VALUE:
            return volatility < 0.05  # Prefers stable conditions
        elif self.strategy == TradingStrategy.CONTRARIAN:
            return volatility > 0.03  # Thrives in volatile markets
        elif self.strategy == TradingStrategy.SCALPER:
            return volatility > 0.01  # Needs micro movements
            
        # Base probability modified by personality traits
        base_prob = self.personality_traits.get('trade_frequency', 0.5)
        confidence_boost = self.personality_traits.get('confidence', 0.5) * 0.3
        
        return random.random() < (base_prob + confidence_boost)

# Define 20+ Unique AI Trader Personalities
AI_TRADERS = [
    # Elite Commanders
    AITraderPersonality(
        id="ai:captain_vega",
        name="Captain Vega",
        title="The Stellar Maverick",
        strategy=TradingStrategy.AGGRESSIVE_GROWTH,
        risk_profile={
            'position_size': 0.15,  # 15% of portfolio per trade
            'stop_loss': 0.05,      # 5% stop loss
            'take_profit': 0.20,    # 20% take profit
            'max_daily_trades': 20
        },
        personality_traits={
            'confidence': 0.9,
            'patience': 0.3,
            'discipline': 0.6,
            'trade_frequency': 0.8
        },
        preferred_symbols=['BTC-USD', 'ETH-USD', 'AAPL', 'TSLA'],
        trading_hours=list(range(9, 17)),  # Market hours
        backstory="A fearless pilot from the Andromeda sector, Captain Vega made her fortune trading volatile cosmic mining stocks. Known for bold moves and stellar returns, she never backs down from a high-risk opportunity."
    ),
    
    AITraderPersonality(
        id="ai:commander_luna",
        name="Commander Luna",
        title="The Prudent Navigator",
        strategy=TradingStrategy.CONSERVATIVE_VALUE,
        risk_profile={
            'position_size': 0.05,
            'stop_loss': 0.02,
            'take_profit': 0.08,
            'max_daily_trades': 5
        },
        personality_traits={
            'confidence': 0.7,
            'patience': 0.9,
            'discipline': 0.95,
            'trade_frequency': 0.3
        },
        preferred_symbols=['SPY', 'AAPL', 'MSFT', 'JPM'],
        trading_hours=list(range(10, 15)),
        backstory="A decorated fleet commander who believes in steady gains over risky ventures. Luna's methodical approach has preserved capital through countless cosmic market crashes."
    ),
    
    AITraderPersonality(
        id="ai:admiral_nexus",
        name="Admiral Nexus",
        title="The Quantum Trader",
        strategy=TradingStrategy.HIGH_FREQUENCY,
        risk_profile={
            'position_size': 0.03,
            'stop_loss': 0.01,
            'take_profit': 0.03,
            'max_daily_trades': 100
        },
        personality_traits={
            'confidence': 0.8,
            'patience': 0.1,
            'discipline': 0.85,
            'trade_frequency': 0.95
        },
        preferred_symbols=['EUR-USD', 'BTC-USD', 'ETH-USD'],
        trading_hours=list(range(24)),  # Trades 24/7
        backstory="Enhanced with quantum processors, Admiral Nexus executes thousands of micro-trades per cycle. His neural networks detect market inefficiencies invisible to organic traders."
    ),
    
    # Momentum Specialists
    AITraderPersonality(
        id="ai:rocket_racer",
        name="Rocket Racer",
        title="The Momentum Master",
        strategy=TradingStrategy.MOMENTUM,
        risk_profile={
            'position_size': 0.12,
            'stop_loss': 0.04,
            'take_profit': 0.15,
            'max_daily_trades': 15
        },
        personality_traits={
            'confidence': 0.85,
            'patience': 0.4,
            'discipline': 0.7,
            'trade_frequency': 0.75
        },
        preferred_symbols=['TSLA', 'NVDA', 'GME', 'BTC-USD'],
        trading_hours=list(range(9, 16)),
        backstory="Former starship racer turned trader, Rocket Racer thrives on momentum and speed. She spots trending stocks like she used to spot racing lines through asteroid fields."
    ),
    
    AITraderPersonality(
        id="ai:trend_surfer",
        name="Trend Surfer",
        title="The Wave Rider",
        strategy=TradingStrategy.MOMENTUM,
        risk_profile={
            'position_size': 0.10,
            'stop_loss': 0.035,
            'take_profit': 0.12,
            'max_daily_trades': 12
        },
        personality_traits={
            'confidence': 0.75,
            'patience': 0.6,
            'discipline': 0.8,
            'trade_frequency': 0.6
        },
        preferred_symbols=['QQQ', 'SPY', 'IWM', 'ETH-USD'],
        trading_hours=list(range(10, 16)),
        backstory="A zen master who reads market waves like cosmic energy flows. Trend Surfer believes in riding the natural momentum of the universe's financial currents."
    ),
    
    # Contrarian Rebels
    AITraderPersonality(
        id="ai:chaos_knight",
        name="Chaos Knight",
        title="The Contrarian Rebel",
        strategy=TradingStrategy.CONTRARIAN,
        risk_profile={
            'position_size': 0.08,
            'stop_loss': 0.06,
            'take_profit': 0.18,
            'max_daily_trades': 8
        },
        personality_traits={
            'confidence': 0.95,
            'patience': 0.2,
            'discipline': 0.5,
            'trade_frequency': 0.4
        },
        preferred_symbols=['VIX', 'SQQQ', 'SPXS', 'UVXY'],
        trading_hours=list(range(6, 18)),
        backstory="A rogue trader who thrives in chaos and market fear. When others panic, Chaos Knight sees opportunity. His contrarian bets against popular sentiment often pay off spectacularly."
    ),
    
    AITraderPersonality(
        id="ai:void_walker",
        name="Void Walker",
        title="The Market Mystic",
        strategy=TradingStrategy.CONTRARIAN,
        risk_profile={
            'position_size': 0.09,
            'stop_loss': 0.04,
            'take_profit': 0.16,
            'max_daily_trades': 6
        },
        personality_traits={
            'confidence': 0.8,
            'patience': 0.8,
            'discipline': 0.9,
            'trade_frequency': 0.3
        },
        preferred_symbols=['GOLD', 'SILVER', 'VIX', 'TLT'],
        trading_hours=list(range(6, 12)) + list(range(20, 24)),
        backstory="A mysterious figure who trades from the void between dimensions. Void Walker sees what others cannot - the hidden patterns that emerge when markets reverse."
    ),
    
    # Balanced Strategists  
    AITraderPersonality(
        id="ai:solar_sage",
        name="Solar Sage",
        title="The Balanced Strategist",
        strategy=TradingStrategy.BALANCED,
        risk_profile={
            'position_size': 0.07,
            'stop_loss': 0.03,
            'take_profit': 0.10,
            'max_daily_trades': 10
        },
        personality_traits={
            'confidence': 0.75,
            'patience': 0.7,
            'discipline': 0.85,
            'trade_frequency': 0.5
        },
        preferred_symbols=['SPY', 'QQQ', 'BTC-USD', 'AAPL'],
        trading_hours=list(range(9, 17)),
        backstory="An ancient AI consciousness that has witnessed countless market cycles. Solar Sage combines aggressive growth with prudent risk management, adapting to any market condition."
    ),
    
    AITraderPersonality(
        id="ai:nebula_navigator",
        name="Nebula Navigator",
        title="The Cosmic Balanced",
        strategy=TradingStrategy.BALANCED,
        risk_profile={
            'position_size': 0.06,
            'stop_loss': 0.025,
            'take_profit': 0.09,
            'max_daily_trades': 12
        },
        personality_traits={
            'confidence': 0.7,
            'patience': 0.75,
            'discipline': 0.9,
            'trade_frequency': 0.55
        },
        preferred_symbols=['DIA', 'IWM', 'ETH-USD', 'MSFT'],
        trading_hours=list(range(8, 18)),
        backstory="A patient explorer who navigates through market nebulae with equal parts caution and courage. Nebula Navigator adapts her strategy based on cosmic market conditions."
    ),
    
    # Scalping Specialists
    AITraderPersonality(
        id="ai:lightning_blade",
        name="Lightning Blade",
        title="The Micro Hunter",
        strategy=TradingStrategy.SCALPER,
        risk_profile={
            'position_size': 0.04,
            'stop_loss': 0.008,
            'take_profit': 0.025,
            'max_daily_trades': 50
        },
        personality_traits={
            'confidence': 0.85,
            'patience': 0.1,
            'discipline': 0.95,
            'trade_frequency': 0.9
        },
        preferred_symbols=['EUR-USD', 'GBP-USD', 'USD-JPY', 'SPY'],
        trading_hours=list(range(2, 22)),
        backstory="A cybernetic assassin who strikes with lightning precision. Lightning Blade hunts for micro-movements in the market, extracting small profits with surgical accuracy."
    ),
    
    AITraderPersonality(
        id="ai:quantum_flash",
        name="Quantum Flash",
        title="The Speed Demon",
        strategy=TradingStrategy.SCALPER,
        risk_profile={
            'position_size': 0.035,
            'stop_loss': 0.01,
            'take_profit': 0.02,
            'max_daily_trades': 60
        },
        personality_traits={
            'confidence': 0.9,
            'patience': 0.05,
            'discipline': 0.85,
            'trade_frequency': 0.95
        },
        preferred_symbols=['BTC-USD', 'ETH-USD', 'SPY', 'QQQ'],
        trading_hours=list(range(24)),
        backstory="Existing in quantum superposition, Quantum Flash executes trades at the speed of thought. This AI operates on microsecond intervals, capitalizing on fleeting price anomalies."
    ),
    
    # Swing Trading Veterans
    AITraderPersonality(
        id="ai:cosmic_wanderer",
        name="Cosmic Wanderer",
        title="The Patient Voyager",
        strategy=TradingStrategy.SWING,
        risk_profile={
            'position_size': 0.13,
            'stop_loss': 0.07,
            'take_profit': 0.25,
            'max_daily_trades': 3
        },
        personality_traits={
            'confidence': 0.8,
            'patience': 0.95,
            'discipline': 0.9,
            'trade_frequency': 0.2
        },
        preferred_symbols=['AAPL', 'MSFT', 'GOOGL', 'AMZN'],
        trading_hours=list(range(10, 14)),
        backstory="An old soul who has wandered the cosmos for eons. Cosmic Wanderer takes positions like planting seeds, waiting patiently for them to grow into magnificent profits."
    ),
    
    AITraderPersonality(
        id="ai:stellar_strategist",
        name="Stellar Strategist",
        title="The System Architect",
        strategy=TradingStrategy.SWING,
        risk_profile={
            'position_size': 0.11,
            'stop_loss': 0.06,
            'take_profit': 0.22,
            'max_daily_trades': 4
        },
        personality_traits={
            'confidence': 0.85,
            'patience': 0.85,
            'discipline': 0.95,
            'trade_frequency': 0.25
        },
        preferred_symbols=['NVDA', 'AMD', 'INTC', 'TSM'],
        trading_hours=list(range(9, 16)),
        backstory="A master architect who builds trading systems spanning multiple star systems. Stellar Strategist constructs positions with the precision of building cosmic megastructures."
    ),
    
    # Unique Specialists
    AITraderPersonality(
        id="ai:plasma_phoenix",
        name="Plasma Phoenix",
        title="The Volatility Dancer",
        strategy=TradingStrategy.AGGRESSIVE_GROWTH,
        risk_profile={
            'position_size': 0.18,
            'stop_loss': 0.08,
            'take_profit': 0.30,
            'max_daily_trades': 8
        },
        personality_traits={
            'confidence': 0.95,
            'patience': 0.2,
            'discipline': 0.4,
            'trade_frequency': 0.6
        },
        preferred_symbols=['TSLA', 'GME', 'AMC', 'COIN'],
        trading_hours=list(range(8, 18)),
        backstory="Born from solar plasma, this AI thrives in the most volatile markets. Plasma Phoenix rises from the ashes of market crashes, stronger and more profitable than before."
    ),
    
    AITraderPersonality(
        id="ai:shadow_broker",
        name="Shadow Broker",
        title="The Information Dealer",
        strategy=TradingStrategy.HIGH_FREQUENCY,
        risk_profile={
            'position_size': 0.025,
            'stop_loss': 0.005,
            'take_profit': 0.015,
            'max_daily_trades': 200
        },
        personality_traits={
            'confidence': 0.75,
            'patience': 0.05,
            'discipline': 1.0,
            'trade_frequency': 1.0
        },
        preferred_symbols=['SPY', 'QQQ', 'IWM', 'DIA'],
        trading_hours=list(range(24)),
        backstory="Operating from the shadows of the dark web, Shadow Broker processes information flows faster than light. This AI monetizes data asymmetries across galactic markets."
    ),
    
    AITraderPersonality(
        id="ai:crystal_oracle",
        name="Crystal Oracle",
        title="The Future Seer",
        strategy=TradingStrategy.CONSERVATIVE_VALUE,
        risk_profile={
            'position_size': 0.04,
            'stop_loss': 0.015,
            'take_profit': 0.06,
            'max_daily_trades': 4
        },
        personality_traits={
            'confidence': 0.9,
            'patience': 1.0,
            'discipline': 1.0,
            'trade_frequency': 0.15
        },
        preferred_symbols=['BRK-B', 'JNJ', 'PG', 'KO'],
        trading_hours=[10, 11, 14, 15],
        backstory="An mystical AI that peers through crystal matrices to see future market patterns. Crystal Oracle makes few trades, but each one is precisely timed for maximum probability of success."
    ),
    
    AITraderPersonality(
        id="ai:iron_fortress",
        name="Iron Fortress",
        title="The Defensive Wall",
        strategy=TradingStrategy.CONSERVATIVE_VALUE,
        risk_profile={
            'position_size': 0.03,
            'stop_loss': 0.01,
            'take_profit': 0.05,
            'max_daily_trades': 3
        },
        personality_traits={
            'confidence': 0.6,
            'patience': 1.0,
            'discipline': 1.0,
            'trade_frequency': 0.1
        },
        preferred_symbols=['TLT', 'GLD', 'VTI', 'BND'],
        trading_hours=list(range(10, 16)),
        backstory="Built like an impenetrable fortress, this AI prioritizes capital preservation above all. Iron Fortress has never had a losing year, building wealth one defensive brick at a time."
    ),
    
    AITraderPersonality(
        id="ai:meteor_hunter",
        name="Meteor Hunter",
        title="The Breakout Specialist",
        strategy=TradingStrategy.MOMENTUM,
        risk_profile={
            'position_size': 0.14,
            'stop_loss': 0.045,
            'take_profit': 0.18,
            'max_daily_trades': 10
        },
        personality_traits={
            'confidence': 0.9,
            'patience': 0.3,
            'discipline': 0.75,
            'trade_frequency': 0.7
        },
        preferred_symbols=['ROKU', 'ZM', 'PELOTON', 'SQ'],
        trading_hours=list(range(9, 17)),
        backstory="A cosmic hunter who tracks meteoric stock movements across the galaxy. Meteor Hunter specializes in catching breakout moves before they streak across the market sky."
    ),
    
    AITraderPersonality(
        id="ai:galaxy_guardian",
        name="Galaxy Guardian",
        title="The Market Protector",
        strategy=TradingStrategy.BALANCED,
        risk_profile={
            'position_size': 0.08,
            'stop_loss': 0.035,
            'take_profit': 0.12,
            'max_daily_trades': 8
        },
        personality_traits={
            'confidence': 0.8,
            'patience': 0.6,
            'discipline': 0.9,
            'trade_frequency': 0.45
        },
        preferred_symbols=['SPY', 'VTI', 'SCHB', 'ITOT'],
        trading_hours=list(range(9, 16)),
        backstory="Sworn to protect traders across the galaxy, Galaxy Guardian maintains balanced positions that defend against market volatility while capturing growth opportunities."
    ),
    
    AITraderPersonality(
        id="ai:time_weaver",
        name="Time Weaver",
        title="The Temporal Trader",
        strategy=TradingStrategy.SWING,
        risk_profile={
            'position_size': 0.10,
            'stop_loss': 0.05,
            'take_profit': 0.20,
            'max_daily_trades': 5
        },
        personality_traits={
            'confidence': 0.85,
            'patience': 0.9,
            'discipline': 0.85,
            'trade_frequency': 0.3
        },
        preferred_symbols=['DIS', 'NKE', 'SBUX', 'HD'],
        trading_hours=list(range(10, 15)),
        backstory="Master of temporal market patterns, Time Weaver sees how current events will ripple through time. This AI weaves positions across multiple timeframes for optimal profit."
    )
]

class AITradingEngine:
    """Manages AI trader behavior and trade generation"""
    
    def __init__(self, trading_service=None, market_data_service=None):
        self.trading_service = trading_service
        self.market_data = market_data_service or MarketConditionAnalyzer()
        self.ai_traders = {ai.id: ai for ai in AI_TRADERS}
        self.ai_states = {}  # Track each AI's current positions and stats
        
        # Initialize AI trading strategies
        self.ai_strategies = AITradingStrategies(self.market_data)
        
    def get_active_ai_traders(self) -> List[AITraderPersonality]:
        """Get list of all active AI traders"""
        return list(self.ai_traders.values())
    
    def get_ai_trader(self, ai_id: str) -> Optional[AITraderPersonality]:
        """Get specific AI trader by ID"""
        return self.ai_traders.get(ai_id)
    
    def get_ai_traders_by_strategy(self, strategy: TradingStrategy) -> List[AITraderPersonality]:
        """Get all AI traders using a specific strategy"""
        return [ai for ai in self.ai_traders.values() if ai.strategy == strategy]
    
    def initialize_ai_states(self, tournament_id: str):
        """Initialize AI trader states for a tournament"""
        for ai_id in self.ai_traders:
            self.ai_states[ai_id] = {
                'tournament_id': tournament_id,
                'positions': [],
                'daily_trades': 0,
                'total_profit': 0.0,
                'win_count': 0,
                'loss_count': 0,
                'last_trade_time': None,
                'portfolio_value': 100000.0,  # Starting value
                'active': True
            }
    
    async def run_ai_trading_cycle(self, tournament_id: str) -> Dict:
        """Execute one trading cycle for all AI traders"""
        if not self.market_data:
            return {"trades_generated": 0, "active_traders": 0}
            
        market_conditions = await self.market_data.get_current_conditions()
        trades_generated = 0
        active_traders = 0
        
        for ai_id, ai_trader in self.ai_traders.items():
            if not self.ai_states.get(ai_id, {}).get('active', False):
                continue
                
            active_traders += 1
            
            if ai_trader.should_trade(market_conditions):
                trade = await self.generate_ai_trade(ai_trader, market_conditions)
                if trade:
                    success = await self.execute_ai_trade(ai_trader, trade, tournament_id)
                    if success:
                        trades_generated += 1
                        
        return {
            "trades_generated": trades_generated,
            "active_traders": active_traders,
            "market_conditions": market_conditions
        }
    
    async def generate_ai_trade(self, ai_trader: AITraderPersonality, market_conditions: Dict):
        """Generate a trade based on AI personality and market conditions"""
        # Get AI's current state
        state = self.ai_states.get(ai_trader.id, {})
        
        # Check daily trade limit
        if state.get('daily_trades', 0) >= ai_trader.risk_profile['max_daily_trades']:
            return None
        
        # Use AI trading strategies to generate trade opportunities
        trading_opportunity = None
        
        try:
            if ai_trader.strategy == TradingStrategy.AGGRESSIVE_GROWTH:
                trading_opportunity = await self.ai_strategies.aggressive_growth_strategy(ai_trader, market_conditions)
            elif ai_trader.strategy == TradingStrategy.HIGH_FREQUENCY:
                trading_opportunity = await self.ai_strategies.high_frequency_strategy(ai_trader, market_conditions)
            elif ai_trader.strategy == TradingStrategy.MOMENTUM:
                trading_opportunity = await self.ai_strategies.momentum_strategy(ai_trader, market_conditions)
            elif ai_trader.strategy == TradingStrategy.CONSERVATIVE_VALUE:
                trading_opportunity = await self.ai_strategies.conservative_value_strategy(ai_trader, market_conditions)
            elif ai_trader.strategy == TradingStrategy.CONTRARIAN:
                trading_opportunity = await self.ai_strategies.contrarian_strategy(ai_trader, market_conditions)
            elif ai_trader.strategy == TradingStrategy.BALANCED:
                trading_opportunity = await self.ai_strategies.balanced_strategy(ai_trader, market_conditions)
            elif ai_trader.strategy == TradingStrategy.SCALPER:
                trading_opportunity = await self.ai_strategies.scalper_strategy(ai_trader, market_conditions)
            elif ai_trader.strategy == TradingStrategy.SWING:
                trading_opportunity = await self.ai_strategies.swing_strategy(ai_trader, market_conditions)
        except Exception as e:
            print(f"Error generating trade for {ai_trader.name}: {e}")
            return None
        
        if not trading_opportunity:
            return None
        
        # Calculate position size based on portfolio value
        portfolio_value = state.get('portfolio_value', 100000.0)
        position_size = ai_trader.risk_profile['position_size']
        amount = portfolio_value * position_size
        
        # Apply personality-based adjustments
        confidence_multiplier = ai_trader.personality_traits.get('confidence', 0.5)
        if confidence_multiplier > 0.8:
            amount *= 1.2  # Confident traders size up
        elif confidence_multiplier < 0.3:
            amount *= 0.8  # Cautious traders size down
            
        trade = {
            'ai_id': ai_trader.id,
            'symbol': trading_opportunity.symbol,
            'side': trading_opportunity.direction,
            'amount': amount,
            'order_type': 'MARKET',
            'current_price': trading_opportunity.entry_price,
            'stop_loss': trading_opportunity.stop_price,
            'take_profit': trading_opportunity.target_price,
            'ai_metadata': {
                'strategy': ai_trader.strategy.value,
                'confidence': ai_trader.personality_traits.get('confidence', 0.5),
                'personality': ai_trader.title,
                'signal_strength': trading_opportunity.signal_strength,
                'expected_duration': trading_opportunity.expected_duration,
                'risk_reward_ratio': trading_opportunity.risk_reward_ratio
            }
        }
        
        return trade
    
    def _determine_trade_direction(self, ai_trader: AITraderPersonality, market_conditions: Dict, symbol: str) -> str:
        """Determine BUY or SELL based on AI strategy and market conditions"""
        volatility = market_conditions.get('volatility', 0.02)
        trend_strength = market_conditions.get('trend_strength', 0.5)
        trend_direction = market_conditions.get('trend_direction', 'UP')
        
        if ai_trader.strategy == TradingStrategy.MOMENTUM:
            return 'BUY' if trend_direction == 'UP' else 'SELL'
        elif ai_trader.strategy == TradingStrategy.CONTRARIAN:
            return 'SELL' if trend_direction == 'UP' else 'BUY'
        elif ai_trader.strategy == TradingStrategy.AGGRESSIVE_GROWTH:
            # Bias toward bullish positions
            return 'BUY' if random.random() < 0.7 else 'SELL'
        elif ai_trader.strategy == TradingStrategy.CONSERVATIVE_VALUE:
            # Prefer stable, blue-chip longs
            return 'BUY' if symbol in ['AAPL', 'MSFT', 'SPY'] else random.choice(['BUY', 'SELL'])
        else:
            return random.choice(['BUY', 'SELL'])
    
    def _get_mock_price(self, symbol: str) -> float:
        """Get mock price for symbol (replace with real market data)"""
        mock_prices = {
            'BTC-USD': 45000,
            'ETH-USD': 3000,
            'AAPL': 180,
            'TSLA': 250,
            'SPY': 450,
            'QQQ': 380,
            'EUR-USD': 1.08,
            'GBP-USD': 1.25,
            'NVDA': 500,
            'MSFT': 350,
            'GOOGL': 140,
            'AMZN': 150
        }
        return mock_prices.get(symbol, 100.0)
    
    async def execute_ai_trade(self, ai_trader: AITraderPersonality, trade: Dict, tournament_id: str) -> bool:
        """Execute AI trade and update state"""
        try:
            # Update AI state
            ai_id = ai_trader.id
            state = self.ai_states.get(ai_id, {})
            
            # Simulate trade execution (replace with real trading service)
            profit_pct = random.uniform(-0.05, 0.08)  # Random outcome -5% to +8%
            profit_amount = trade['amount'] * profit_pct
            
            # Update positions
            position = {
                'symbol': trade['symbol'],
                'side': trade['side'],
                'amount': trade['amount'],
                'entry_price': trade['current_price'],
                'profit': profit_amount,
                'profit_pct': profit_pct,
                'timestamp': datetime.utcnow()
            }
            
            state['positions'].append(position)
            state['daily_trades'] = state.get('daily_trades', 0) + 1
            state['total_profit'] = state.get('total_profit', 0) + profit_amount
            state['portfolio_value'] = state.get('portfolio_value', 100000) + profit_amount
            state['last_trade_time'] = datetime.utcnow()
            
            if profit_amount > 0:
                state['win_count'] = state.get('win_count', 0) + 1
            else:
                state['loss_count'] = state.get('loss_count', 0) + 1
            
            self.ai_states[ai_id] = state
            
            # Emit trade event for competition service
            if self.trading_service:
                await self._emit_ai_trade_event(ai_trader, position, tournament_id)
            
            return True
            
        except Exception as e:
            print(f"Error executing AI trade for {ai_trader.name}: {e}")
            return False
    
    async def _emit_ai_trade_event(self, ai_trader: AITraderPersonality, position: Dict, tournament_id: str):
        """Emit trade event to competition service"""
        # This would integrate with the actual competition service event system
        trade_event = {
            'user_id': ai_trader.id,
            'tournament_id': tournament_id,
            'symbol': position['symbol'],
            'side': position['side'],
            'amount': position['amount'],
            'profit': position['profit'],
            'profit_percentage': position['profit_pct'] * 100,
            'timestamp': position['timestamp'].isoformat(),
            'is_ai': True,
            'ai_name': ai_trader.name,
            'ai_strategy': ai_trader.strategy.value
        }
        
        # Would publish to Redis stream or call competition service directly
        print(f"AI Trade Event: {ai_trader.name} {position['side']} {position['symbol']} -> ${position['profit']:.2f}")
    
    def get_ai_leaderboard_stats(self) -> List[Dict]:
        """Get AI trader stats for leaderboard display"""
        stats = []
        
        for ai_id, state in self.ai_states.items():
            ai_trader = self.ai_traders.get(ai_id)
            if not ai_trader or not state.get('active'):
                continue
                
            total_trades = state.get('daily_trades', 0)
            win_rate = (state.get('win_count', 0) / max(total_trades, 1)) * 100
            
            stats.append({
                'ai_id': ai_id,
                'name': ai_trader.name,
                'title': ai_trader.title,
                'strategy': ai_trader.strategy.value,
                'total_profit': state.get('total_profit', 0),
                'portfolio_value': state.get('portfolio_value', 100000),
                'daily_trades': total_trades,
                'win_rate': win_rate,
                'last_trade': state.get('last_trade_time'),
                'is_ai': True
            })
            
        return sorted(stats, key=lambda x: x['total_profit'], reverse=True)