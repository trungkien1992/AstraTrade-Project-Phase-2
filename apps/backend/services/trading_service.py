from typing import Optional, Dict, Any
import asyncio
from datetime import datetime, timedelta
import random
from decimal import Decimal

from repositories.user_repository import UserRepository
from repositories.trade_repository import TradeRepository
from external.exchange_client import ExchangeClient
from external.starknet_client import StarknetClient
from core.events import EventBus, TradeExecutedEvent
from models.trade import Trade, TradeStatus
from schemas.trade import TradeRequest, TradeResult

class TradingService:
    def __init__(
        self,
        user_repo: UserRepository,
        trade_repo: TradeRepository,
        exchange_client: ExchangeClient,
        starknet_client: StarknetClient,
        event_bus: EventBus
    ):
        self.user_repo = user_repo
        self.trade_repo = trade_repo
        self.exchange_client = exchange_client
        self.starknet_client = starknet_client
        self.event_bus = event_bus
        
    async def execute_trade(
        self,
        user_id: int,
        request: TradeRequest
    ) -> TradeResult:
        """Execute a trade with full error handling and rollback"""
        # Validate user and limits
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        
        await self._validate_trade_limits(user, request)
        
        # Create pending trade record
        trade = await self.trade_repo.create({
            'user_id': user_id,
            'asset': request.asset,
            'direction': request.direction,
            'amount': float(request.amount),
            'status': TradeStatus.PENDING,
            'created_at': datetime.utcnow()
        })
        
        try:
            # Execute on exchange (or mock)
            if request.is_mock:
                exchange_result = await self._execute_mock_trade(request)
            else:
                exchange_result = await self.exchange_client.place_order(
                    symbol=request.asset,
                    side=request.direction,
                    amount=request.amount,
                    leverage=request.leverage
                )
            
            # Update trade with result
            trade = await self.trade_repo.update(trade.id, {
                'status': TradeStatus.COMPLETED,
                'executed_price': exchange_result.price,
                'profit_amount': exchange_result.profit,
                'profit_percentage': exchange_result.profit_percentage,
                'execution_time': exchange_result.timestamp,
                'exchange_order_id': exchange_result.order_id
            })
            
            # Calculate rewards
            rewards = await self._calculate_rewards(user, trade)
            
            # Update user stats
            await self.user_repo.update_xp(user_id, rewards['xp'])
            await self.user_repo.update_daily_streak(user_id)
            
            # Update on-chain if real trade
            if not request.is_mock:
                await self._update_blockchain_stats(user_id, trade, rewards)
            
            # Emit event
            await self.event_bus.emit(TradeExecutedEvent(
                user_id=user_id,
                trade_id=trade.id,
                profit=trade.profit_amount,
                xp_gained=rewards['xp']
            ))
            
            return TradeResult(
                trade_id=trade.id,
                status='success',
                executed_price=trade.executed_price,
                profit_amount=trade.profit_amount,
                profit_percentage=trade.profit_percentage,
                rewards=rewards
            )
            
        except Exception as e:
            # Rollback on failure
            await self.trade_repo.update(trade.id, {
                'status': TradeStatus.FAILED,
                'error_message': str(e)
            })
            raise
    
    async def _validate_trade_limits(self, user, request):
        """Validate trade against user limits"""
        # Check daily trade limit
        today_trades = await self.trade_repo.get_user_trades_count(
            user.id,
            since=datetime.utcnow() - timedelta(days=1)
        )
        
        if today_trades >= self._get_daily_trade_limit(user.level):
            raise ValueError("Daily trade limit exceeded")
        
        # Check position size limit
        max_position = self._get_max_position_size(user.level)
        if request.amount > max_position:
            raise ValueError(f"Position size exceeds limit of {max_position}")
        
        # Check cooldown period
        last_trade = await self.trade_repo.get_last_user_trade(user.id)
        if last_trade:
            cooldown = self._get_trade_cooldown(user.level)
            time_since_last = datetime.utcnow() - last_trade.created_at
            if time_since_last < cooldown:
                remaining = cooldown - time_since_last
                raise ValueError(f"Trade cooldown: {remaining.seconds}s remaining")
    
    async def _execute_mock_trade(self, request):
        """Execute a mock trade with realistic simulation"""
        # Simulate execution delay
        await asyncio.sleep(random.uniform(0.5, 2.0))
        
        # Generate realistic price movement
        base_price = await self._get_mock_price(request.asset)
        spread = base_price * 0.0002  # 0.02% spread
        
        if request.direction == 'long':
            executed_price = base_price + spread
        else:
            executed_price = base_price - spread
        
        # Simulate profit/loss based on market conditions
        market_movement = random.gauss(0, 0.02)  # 2% std dev
        
        if request.direction == 'long':
            exit_price = executed_price * (1 + market_movement)
        else:
            exit_price = executed_price * (1 - market_movement)
        
        profit_percentage = ((exit_price - executed_price) / executed_price) * 100
        if request.direction == 'short':
            profit_percentage = -profit_percentage
        
        profit_amount = float(request.amount) * (profit_percentage / 100)
        
        return {
            'price': executed_price,
            'profit': profit_amount,
            'profit_percentage': profit_percentage,
            'timestamp': datetime.utcnow(),
            'order_id': f"MOCK-{int(datetime.utcnow().timestamp())}"
        }
    
    async def _calculate_rewards(self, user, trade) -> Dict[str, Any]:
        """Calculate XP and other rewards for a trade"""
        base_xp = 10
        
        # Profit multiplier
        if trade.profit_amount > 0:
            profit_multiplier = min(2.0, 1 + (trade.profit_percentage / 100))
        else:
            profit_multiplier = 0.5
        
        # Streak multiplier
        streak_multiplier = 1 + (user.current_streak * 0.1)
        
        # Level multiplier
        level_multiplier = 1 + (user.level * 0.05)
        
        # Calculate total XP
        total_xp = int(
            base_xp * profit_multiplier * streak_multiplier * level_multiplier
        )
        
        # Check for achievements
        achievements = await self._check_achievements(user, trade)
        
        # Bonus items (random chance)
        bonus_items = []
        if random.random() < 0.1:  # 10% chance
            bonus_items.append({
                'type': 'shield_dust',
                'amount': random.randint(5, 20)
            })
        
        return {
            'xp': total_xp,
            'achievements': achievements,
            'bonus_items': bonus_items,
            'multipliers': {
                'profit': profit_multiplier,
                'streak': streak_multiplier,
                'level': level_multiplier
            }
        }
    
    async def _update_blockchain_stats(self, user_id, trade, rewards):
        """Update user stats on blockchain"""
        try:
            # Update points on leaderboard contract
            await self.starknet_client.update_user_points(
                user_address=await self._get_user_starknet_address(user_id),
                points_delta=rewards['xp']
            )
            
            # Mint achievement NFTs if any
            for achievement in rewards['achievements']:
                await self.starknet_client.mint_achievement(
                    user_address=await self._get_user_starknet_address(user_id),
                    achievement_id=achievement['id']
                )
        except Exception as e:
            # Log but don't fail the trade
            print(f"Blockchain update failed: {e}")
    
    async def _check_achievements(self, user, trade):
        """Check if user unlocked any achievements"""
        achievements = []
        
        # First trade achievement
        if await self.trade_repo.get_user_trades_count(user.id) == 1:
            achievements.append({
                'id': 'first_trade',
                'name': 'First Steps',
                'description': 'Complete your first trade'
            })
        
        # Profit achievements
        if trade.profit_amount > 100:
            achievements.append({
                'id': 'profit_100',
                'name': 'Profit Master',
                'description': 'Earn $100 in a single trade'
            })
        
        # Streak achievements
        if user.current_streak == 7:
            achievements.append({
                'id': 'streak_7',
                'name': 'Week Warrior',
                'description': 'Trade for 7 consecutive days'
            })
        
        return achievements
    
    def _get_daily_trade_limit(self, level: int) -> int:
        """Get daily trade limit based on level"""
        return 10 + (level * 5)
    
    def _get_max_position_size(self, level: int) -> float:
        """Get max position size based on level"""
        return 100 + (level * 50)
    
    def _get_trade_cooldown(self, level: int) -> timedelta:
        """Get trade cooldown period based on level"""
        seconds = max(10, 60 - (level * 5))
        return timedelta(seconds=seconds)
    
    async def _get_mock_price(self, asset: str) -> float:
        """Get mock price for asset"""
        prices = {
            'BTC-USD': 65000.0,
            'ETH-USD': 3500.0,
            'SOL-USD': 150.0,
        }
        return prices.get(asset, 100.0)
    
    async def _get_user_starknet_address(self, user_id: int) -> str:
        """Get user's Starknet address"""
        # This would be stored in the database
        return f"0x{user_id:064x}"
