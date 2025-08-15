from typing import Dict, Optional
from datetime import datetime, timedelta
import numpy as np
import redis

class TournamentScoringEngine:
    """
    Calculates composite scores for tournament participants.
    
    Scoring Formula:
    - Profit Factor: 40% (risk-adjusted returns)
    - Win Rate: 30% (consistency)
    - Volume Score: 20% (activity level)
    - Consistency: 10% (steady performance)
    """
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.weights = {
            'profit_factor': 0.4,
            'win_rate': 0.3,
            'volume': 0.2,
            'consistency': 0.1
        }
    
    async def calculate_score_components(self, user_id: str, tournament_id: str) -> Dict[str, float]:
        """Calculate individual scoring components"""
        user_stats = await self.get_user_tournament_stats(user_id, tournament_id)
        
        components = {
            'profit_factor': self.calculate_profit_factor(user_stats),
            'win_rate': self.calculate_win_rate(user_stats),
            'volume': self.calculate_volume_score(user_stats),
            'consistency': self.calculate_consistency_score(user_stats)
        }
        
        return components
    
    def calculate_profit_factor(self, stats: Dict) -> float:
        """
        Calculate risk-adjusted returns.
        Uses Sharpe-like ratio normalized to 0-100 scale.
        """
        if stats.get('total_trades', 0) == 0:
            return 0.0
            
        initial_capital = float(stats.get('initial_capital', 100000))
        total_profit = float(stats.get('total_profit', 0))
        returns = total_profit / initial_capital
        
        # Use volatility from stats or calculate a basic one
        volatility = float(stats.get('returns_std', 0.1))
        if volatility == 0:
            volatility = 0.1  # Avoid division by zero
        
        # Sharpe-like calculation
        risk_adjusted_return = returns / volatility if volatility > 0 else returns
        
        # Normalize to 0-100 scale with sigmoid function
        # Adjust the scaling factor based on typical trading returns
        normalized = 100 * (1 / (1 + np.exp(-5 * risk_adjusted_return)))
        
        return normalized
    
    def calculate_win_rate(self, stats: Dict) -> float:
        """Calculate percentage of profitable trades"""
        total_trades = int(stats.get('total_trades', 0))
        if total_trades == 0:
            return 0.0
            
        winning_trades = int(stats.get('winning_trades', 0))
        return (winning_trades / total_trades) * 100
    
    def calculate_volume_score(self, stats: Dict) -> float:
        """
        Score based on trading activity.
        Encourages participation without promoting overtrading.
        """
        volume = float(stats.get('total_volume', 0))
        
        # Logarithmic scale to prevent volume gaming
        # Cap at 100,000 credits to prevent abuse
        normalized_volume = min(volume / 100000, 1.0)
        
        # Apply diminishing returns
        score = 100 * (1 - np.exp(-3 * normalized_volume))
        
        return score
    
    def calculate_consistency_score(self, stats: Dict) -> float:
        """
        Reward steady performance over time.
        Lower variance in returns = higher consistency.
        """
        total_trades = int(stats.get('total_trades', 0))
        if total_trades < 3:
            return 0.0  # Need minimum trades for consistency
            
        returns_variance = float(stats.get('returns_variance', 1.0))
        
        # Inverse relationship: lower variance = higher score
        # Normalize using exponential decay
        consistency = 100 * np.exp(-returns_variance)
        
        return consistency
    
    def calculate_composite_score(self, components: Dict[str, float]) -> float:
        """Combine all components into final tournament score"""
        total = sum(
            components[key] * self.weights[key] 
            for key in self.weights if key in components
        )
        
        return round(total, 2)
    
    async def get_user_tournament_stats(self, user_id: str, tournament_id: str) -> Dict:
        """Retrieve user's tournament statistics from Redis"""
        stats_key = f"tournament:{tournament_id}:stats:{user_id}"
        raw_stats = self.redis.hgetall(stats_key)
        
        if not raw_stats:
            return {
                'total_trades': 0,
                'winning_trades': 0,
                'total_profit': 0.0,
                'total_volume': 0.0,
                'initial_capital': 100000.0,
                'returns_std': 0.1,
                'returns_variance': 1.0
            }
        
        # Convert string values to appropriate types
        stats = {}
        for key, value in raw_stats.items():
            if key in ['total_trades', 'winning_trades']:
                stats[key] = int(value)
            elif key in ['total_profit', 'total_volume', 'initial_capital', 'returns_std', 'returns_variance']:
                stats[key] = float(value)
            else:
                stats[key] = value
        
        return stats
    
    async def calculate_user_score(self, user_id: str, tournament_id: str) -> float:
        """Calculate complete user score for tournament"""
        components = await self.calculate_score_components(user_id, tournament_id)
        return self.calculate_composite_score(components)
    
    def calculate_returns_volatility(self, trade_returns: list) -> float:
        """Calculate volatility of trade returns"""
        if len(trade_returns) < 2:
            return 0.1  # Default volatility
        
        returns_array = np.array(trade_returns)
        return float(np.std(returns_array))
    
    def calculate_returns_variance(self, trade_returns: list) -> float:
        """Calculate variance of trade returns"""
        if len(trade_returns) < 2:
            return 1.0  # Default variance
        
        returns_array = np.array(trade_returns)
        return float(np.var(returns_array))
    
    async def update_user_returns_stats(self, user_id: str, tournament_id: str, new_return: float):
        """Update user's return statistics with new trade return"""
        returns_key = f"tournament:{tournament_id}:returns:{user_id}"
        
        # Get existing returns (stored as JSON list)
        existing_returns_json = self.redis.get(returns_key)
        if existing_returns_json:
            import json
            returns_list = json.loads(existing_returns_json)
        else:
            returns_list = []
        
        # Add new return
        returns_list.append(new_return)
        
        # Keep only last 100 returns to prevent memory bloat
        if len(returns_list) > 100:
            returns_list = returns_list[-100:]
        
        # Store updated returns
        import json
        self.redis.set(returns_key, json.dumps(returns_list))
        
        # Calculate and store statistics
        if len(returns_list) > 1:
            volatility = self.calculate_returns_volatility(returns_list)
            variance = self.calculate_returns_variance(returns_list)
            
            stats_key = f"tournament:{tournament_id}:stats:{user_id}"
            self.redis.hset(stats_key, mapping={
                'returns_std': str(volatility),
                'returns_variance': str(variance)
            })
    
    def get_score_breakdown(self, components: Dict[str, float]) -> Dict[str, Dict]:
        """Get detailed score breakdown for UI display"""
        breakdown = {}
        
        for component, score in components.items():
            weight = self.weights.get(component, 0)
            weighted_score = score * weight
            
            breakdown[component] = {
                'raw_score': round(score, 2),
                'weight': weight,
                'weighted_score': round(weighted_score, 2),
                'percentage_of_total': round((weighted_score / 100) * 100, 1)
            }
        
        return breakdown
    
    def get_scoring_explanation(self) -> Dict[str, str]:
        """Get human-readable explanation of scoring system"""
        return {
            'profit_factor': f"Risk-adjusted returns ({self.weights['profit_factor']*100}% of score). Higher profits with lower volatility score better.",
            'win_rate': f"Percentage of profitable trades ({self.weights['win_rate']*100}% of score). Consistency in winning trades.",
            'volume': f"Trading activity level ({self.weights['volume']*100}% of score). Rewards participation but with diminishing returns.",
            'consistency': f"Steady performance over time ({self.weights['consistency']*100}% of score). Lower variance in returns scores higher."
        }