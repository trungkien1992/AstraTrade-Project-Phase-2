"""
Trading Domain Services

Consolidated domain service implementing the Trading Domain as defined in ADR-001.
This service consolidates the following existing services per Phase 1 migration strategy:

Consolidates:
- services/trading_service.py (290 lines) - Core trading logic
- services/clan_trading_service.py (395 lines) - Clan battle integration  
- services/extended_exchange_client.py (423 lines) - External API integration
- services/groq_service.py (partial) - AI trading recommendations

Total consolidation: ~1100+ lines → Single domain service
Service reduction contribution: 4 services → 1 domain service

Architecture follows PHASE1_DOMAIN_STRUCTURE.md with:
- Clean separation of domain logic from infrastructure
- Repository pattern for data access
- Domain events for loose coupling
- Type-safe interfaces and error handling
"""

import asyncio
import logging
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Dict, List, Optional, Any, Protocol
from dataclasses import dataclass

from .entities import Trade, Portfolio, Position
from .value_objects import Asset, Money, RiskParameters, TradeDirection, TradeStatus, AssetCategory
from ..shared.events import DomainEvent, EventBus
from ..shared.repositories import Repository

logger = logging.getLogger(__name__)


# Domain Events
@dataclass
class TradeExecutedEvent(DomainEvent):
    """Domain event raised when a trade is executed."""
    trade_id: str = ""
    user_id: int = 0
    asset_symbol: str = ""
    direction: str = ""
    amount: Decimal = Decimal('0')
    entry_price: Decimal = Decimal('0')
    executed_at: datetime = None
    
    @property
    def event_type(self) -> str:
        return "trade_executed"


@dataclass
class TradingRewardsCalculatedEvent(DomainEvent):
    """Domain event raised when trading rewards are calculated."""
    user_id: int = 0
    trade_id: str = ""
    xp_gained: int = 0
    achievements_unlocked: List[str] = None
    bonus_items: List[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.achievements_unlocked is None:
            self.achievements_unlocked = []
        if self.bonus_items is None:
            self.bonus_items = []
    
    @property
    def event_type(self) -> str:
        return "trading_rewards_calculated"


@dataclass
class ClanBattleScoreUpdatedEvent(DomainEvent):
    """Domain event raised when clan battle scores are updated."""
    battle_id: int = 0
    user_id: int = 0
    trading_score: Decimal = Decimal('0')
    trade_count: int = 0
    pnl_usd: Decimal = Decimal('0')
    
    @property
    def event_type(self) -> str:
        return "clan_battle_score_updated"


# Repository Interfaces (to be implemented in infrastructure layer)
class TradeRepository(Protocol):
    """Repository interface for Trade persistence."""
    
    async def save(self, trade: Trade) -> Trade:
        """Persist a trade entity."""
        ...
    
    async def get_by_id(self, trade_id: str) -> Optional[Trade]:
        """Retrieve trade by ID."""
        ...
    
    async def get_user_trades(self, user_id: int, limit: int = 100) -> List[Trade]:
        """Get trades for a specific user."""
        ...
    
    async def get_user_trades_count(self, user_id: int, since: Optional[datetime] = None) -> int:
        """Count user trades optionally since a specific date."""
        ...


class PortfolioRepository(Protocol):
    """Repository interface for Portfolio persistence."""
    
    async def save(self, portfolio: Portfolio) -> Portfolio:
        """Persist a portfolio entity."""
        ...
    
    async def get_by_user_id(self, user_id: int) -> Optional[Portfolio]:
        """Retrieve portfolio by user ID."""
        ...


# External Service Interfaces (to be implemented in infrastructure layer)
class ExchangeClient(Protocol):
    """Interface for external exchange integration."""
    
    async def place_order(
        self, 
        symbol: str, 
        side: str, 
        amount: Decimal, 
        leverage: Optional[Decimal] = None
    ) -> Dict[str, Any]:
        """Place order on external exchange."""
        ...
    
    async def get_current_price(self, symbol: str) -> Decimal:
        """Get current market price for symbol."""
        ...
    
    async def get_trades(
        self, 
        start_time: int, 
        end_time: int, 
        limit: int = 1000
    ) -> Dict[str, Any]:
        """Get historical trades from exchange."""
        ...


class StarknetClient(Protocol):
    """Interface for Starknet blockchain integration."""
    
    async def update_user_points(self, user_address: str, points_delta: int) -> bool:
        """Update user points on blockchain."""
        ...
    
    async def mint_achievement(self, user_address: str, achievement_id: str) -> bool:
        """Mint achievement NFT on blockchain."""
        ...


class AIAnalysisService(Protocol):
    """Interface for AI-powered trading analysis."""
    
    async def get_trading_recommendation(
        self,
        user_id: int,
        market_data: Dict[str, Any],
        user_profile: Dict[str, Any],
        trading_history: List[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """Get AI-powered trading recommendation."""
        ...


# Main Domain Service
class TradingDomainService:
    """
    Core Trading Domain Service consolidating all trading-related functionality.
    
    This service implements the Trading Domain business logic while delegating
    infrastructure concerns to injected dependencies (Repository pattern).
    
    Consolidates functionality from:
    - TradingService: Core trade execution and validation
    - ClanTradingService: Battle scoring and clan integration
    - ExtendedExchangeClient: External exchange integration
    - GroqService: AI-powered trading analysis
    
    Responsibilities:
    - Trade execution and lifecycle management
    - Portfolio management and P&L calculation
    - Risk management and validation
    - Trading rewards and gamification integration
    - Clan battle scoring
    - AI-powered trading recommendations
    """
    
    def __init__(
        self,
        trade_repository: TradeRepository,
        portfolio_repository: PortfolioRepository,
        exchange_client: ExchangeClient,
        starknet_client: StarknetClient,
        ai_analysis_service: AIAnalysisService,
        event_bus: EventBus
    ):
        self._trade_repo = trade_repository
        self._portfolio_repo = portfolio_repository
        self._exchange_client = exchange_client
        self._starknet_client = starknet_client
        self._ai_service = ai_analysis_service
        self._event_bus = event_bus
    
    async def execute_trade(
        self,
        user_id: int,
        asset: Asset,
        direction: TradeDirection,
        amount: Money,
        risk_params: RiskParameters,
        is_mock: bool = False
    ) -> Dict[str, Any]:
        """
        Execute a trade with full validation and error handling.
        
        Consolidates logic from original TradingService.execute_trade() 
        with improved domain-driven design.
        """
        # 1. Validate user and risk parameters
        await self._validate_trade_request(user_id, amount, risk_params)
        
        # 2. Create trade entity
        trade = Trade(
            user_id=user_id,
            asset=asset,
            direction=direction,
            amount=amount
        )
        
        try:
            # 3. Execute on exchange (or mock)
            if is_mock:
                execution_result = await self._execute_mock_trade(trade)
            else:
                execution_result = await self._execute_real_trade(trade)
            
            # 4. Update trade with execution result
            trade.execute(
                entry_price=Money(execution_result['price'], amount.currency),
                exchange_order_id=execution_result['order_id']
            )
            
            # 5. Save trade to repository
            await self._trade_repo.save(trade)
            
            # 6. Update portfolio
            await self._update_portfolio(user_id, trade)
            
            # 7. Calculate and award rewards
            rewards = await self._calculate_trading_rewards(user_id, trade)
            
            # 8. Update blockchain state (if real trade)
            if not is_mock:
                await self._update_blockchain_stats(user_id, trade, rewards)
            
            # 9. Emit domain events
            await self._emit_trade_events(trade, rewards)
            
            return {
                "trade_id": trade.trade_id,
                "status": "success",
                "executed_price": float(trade.entry_price.amount),
                "exchange_order_id": trade.exchange_order_id,
                "rewards": rewards
            }
            
        except Exception as e:
            # Rollback: mark trade as failed
            trade.fail(str(e))
            await self._trade_repo.save(trade)
            
            logger.error(f"Trade execution failed for user {user_id}: {str(e)}")
            raise
    
    async def close_trade(
        self,
        trade_id: str,
        exit_price: Optional[Money] = None
    ) -> Dict[str, Any]:
        """Close an active trade and calculate final P&L."""
        trade = await self._trade_repo.get_by_id(trade_id)
        if not trade:
            raise ValueError(f"Trade {trade_id} not found")
        
        if trade.status != TradeStatus.ACTIVE:
            raise ValueError(f"Cannot close trade with status {trade.status}")
        
        # Get current market price if not provided
        if not exit_price:
            current_price = await self._exchange_client.get_current_price(trade.asset.symbol)
            exit_price = Money(current_price, trade.amount.currency)
        
        # Close trade and calculate P&L
        pnl = trade.close(exit_price)
        
        # Update repository
        await self._trade_repo.save(trade)
        
        # Update portfolio
        await self._update_portfolio(trade.user_id, trade)
        
        return {
            "trade_id": trade_id,
            "status": "closed",
            "exit_price": float(exit_price.amount),
            "pnl": float(pnl.amount),
            "pnl_percentage": float(trade.calculate_pnl_percentage(exit_price))
        }
    
    async def get_portfolio(self, user_id: int) -> Optional[Portfolio]:
        """Get user's current portfolio with real-time P&L."""
        portfolio = await self._portfolio_repo.get_by_user_id(user_id)
        if not portfolio:
            return None
        
        # Update with current market prices
        current_prices = await self._get_current_prices_for_portfolio(portfolio)
        
        # Portfolio automatically calculates real-time metrics
        return portfolio
    
    async def calculate_clan_battle_score(
        self,
        user_id: int,
        battle_id: int,
        start_time: datetime,
        end_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Calculate trading score for clan battles.
        
        Consolidates logic from ClanTradingService.calculate_trading_score()
        with improved domain modeling.
        """
        end_time = end_time or datetime.now(timezone.utc)
        
        # Get user trades during battle period
        user_trades = await self._get_user_trades_in_period(user_id, start_time, end_time)
        
        if not user_trades:
            return self._empty_battle_score()
        
        # Calculate battle metrics
        metrics = self._calculate_battle_metrics(user_trades)
        
        # Apply battle score algorithm
        battle_score = self._calculate_battle_score_algorithm(metrics)
        
        # Emit domain event
        await self._event_bus.emit(ClanBattleScoreUpdatedEvent(
            battle_id=battle_id,
            user_id=user_id,
            trading_score=battle_score["total_score"],
            trade_count=metrics["trade_count"],
            pnl_usd=metrics["total_pnl"]
        ))
        
        return battle_score
    
    async def get_ai_trading_recommendation(
        self,
        user_id: int,
        asset: Asset
    ) -> Optional[Dict[str, Any]]:
        """
        Get AI-powered trading recommendation.
        
        Consolidates logic from GroqService.get_trading_recommendation()
        with improved domain integration.
        """
        # Gather context data
        portfolio = await self.get_portfolio(user_id)
        recent_trades = await self._trade_repo.get_user_trades(user_id, limit=20)
        current_price = await self._exchange_client.get_current_price(asset.symbol)
        
        # Prepare data for AI analysis
        market_data = {
            "asset": asset.symbol,
            "current_price": float(current_price),
            "category": asset.category.value
        }
        
        user_profile = {
            "user_id": user_id,
            "portfolio_value": float(portfolio.calculate_total_value({asset.symbol: Money(current_price, 'USD')}).amount) if portfolio else 0,
            "trade_count": len(recent_trades),
            "experience_level": self._determine_experience_level(recent_trades)
        }
        
        trading_history = [
            {
                "asset": trade.asset.symbol,
                "direction": trade.direction.value,
                "amount": float(trade.amount.amount),
                "pnl": float(trade.calculate_pnl(Money(current_price, 'USD')).amount) if trade.entry_price else 0,
                "created_at": trade.created_at.isoformat()
            }
            for trade in recent_trades[-10:]  # Last 10 trades
        ]
        
        # Get AI recommendation
        recommendation = await self._ai_service.get_trading_recommendation(
            user_id=user_id,
            market_data=market_data,
            user_profile=user_profile,
            trading_history=trading_history
        )
        
        return recommendation
    
    # Private helper methods
    
    async def _validate_trade_request(
        self,
        user_id: int,
        amount: Money,
        risk_params: RiskParameters
    ) -> None:
        """Validate trade request against business rules."""
        # Get user's portfolio to check available balance
        portfolio = await self._portfolio_repo.get_by_user_id(user_id)
        if not portfolio:
            raise ValueError("User portfolio not found")
        
        # Check available balance
        if amount.amount > portfolio.available_balance.amount:
            raise ValueError("Insufficient balance for trade")
        
        # Check daily trade limits
        today_trades = await self._trade_repo.get_user_trades_count(
            user_id, 
            since=datetime.now(timezone.utc) - timedelta(days=1)
        )
        
        max_daily_trades = self._get_daily_trade_limit_for_user(user_id)  # Based on user level
        if today_trades >= max_daily_trades:
            raise ValueError("Daily trade limit exceeded")
        
        # Validate risk parameters
        if amount.amount > portfolio.available_balance.multiply(risk_params.max_position_pct / Decimal('100')).amount:
            raise ValueError("Trade amount exceeds maximum position size")
    
    async def _execute_mock_trade(self, trade: Trade) -> Dict[str, Any]:
        """Execute a mock trade with realistic simulation."""
        # Simulate execution delay
        await asyncio.sleep(0.5)
        
        # Get current market price
        current_price = await self._exchange_client.get_current_price(trade.asset.symbol)
        
        # Add realistic spread
        spread_pct = Decimal('0.002')  # 0.2% spread
        if trade.direction == TradeDirection.LONG:
            execution_price = current_price * (Decimal('1') + spread_pct)
        else:
            execution_price = current_price * (Decimal('1') - spread_pct)
        
        return {
            'price': execution_price,
            'order_id': f"MOCK-{trade.trade_id[:8]}",
            'timestamp': datetime.now(timezone.utc)
        }
    
    async def _execute_real_trade(self, trade: Trade) -> Dict[str, Any]:
        """Execute a real trade on external exchange."""
        result = await self._exchange_client.place_order(
            symbol=trade.asset.symbol,
            side=trade.direction.value,
            amount=trade.amount.amount
        )
        
        return {
            'price': Decimal(str(result['price'])),
            'order_id': result['order_id'],
            'timestamp': datetime.now(timezone.utc)
        }
    
    async def _update_portfolio(self, user_id: int, trade: Trade) -> None:
        """Update user's portfolio with new trade."""
        portfolio = await self._portfolio_repo.get_by_user_id(user_id)
        if not portfolio:
            # Create new portfolio if doesn't exist
            portfolio = Portfolio(
                user_id=user_id,
                available_balance=Money(Decimal('10000'), 'USD')  # Default starting balance
            )
        
        # Add trade to appropriate position
        position = portfolio.get_position(trade.asset.symbol)
        if not position:
            position = Position(trade.asset)
            portfolio.add_position(position)
        
        position.add_trade(trade)
        
        # Update available balance (subtract trade amount)
        new_balance = portfolio.available_balance.subtract(trade.amount)
        portfolio.update_available_balance(new_balance)
        
        await self._portfolio_repo.save(portfolio)
    
    async def _calculate_trading_rewards(
        self,
        user_id: int,
        trade: Trade
    ) -> Dict[str, Any]:
        """Calculate XP and other rewards for a completed trade."""
        base_xp = 10
        
        # Calculate P&L for reward multiplier
        if trade.entry_price:
            current_price = await self._exchange_client.get_current_price(trade.asset.symbol)
            pnl = trade.calculate_pnl(Money(current_price, trade.amount.currency))
            pnl_pct = trade.calculate_pnl_percentage(Money(current_price, trade.amount.currency))
            
            # Profit multiplier
            if pnl.is_positive():
                profit_multiplier = min(Decimal('2.0'), Decimal('1') + abs(pnl_pct) / Decimal('100'))
            else:
                profit_multiplier = Decimal('0.5')  # Reduced XP for losses
        else:
            profit_multiplier = Decimal('1.0')
        
        # Calculate total XP
        total_xp = int(Decimal(str(base_xp)) * profit_multiplier)
        
        # Check for achievements (simplified)
        achievements = await self._check_trade_achievements(user_id, trade)
        
        return {
            'xp': total_xp,
            'achievements': achievements,
            'bonus_items': [],  # Could be implemented later
            'multipliers': {
                'profit': float(profit_multiplier)
            }
        }
    
    async def _update_blockchain_stats(
        self,
        user_id: int,
        trade: Trade,
        rewards: Dict[str, Any]
    ) -> None:
        """Update user stats on Starknet blockchain."""
        try:
            user_address = f"0x{user_id:064x}"  # Convert user ID to address
            
            # Update XP points
            await self._starknet_client.update_user_points(
                user_address=user_address,
                points_delta=rewards['xp']
            )
            
            # Mint achievement NFTs
            for achievement in rewards['achievements']:
                await self._starknet_client.mint_achievement(
                    user_address=user_address,
                    achievement_id=achievement['id']
                )
        except Exception as e:
            logger.warning(f"Blockchain update failed for user {user_id}: {e}")
            # Don't fail the trade for blockchain issues
    
    async def _emit_trade_events(self, trade: Trade, rewards: Dict[str, Any]) -> None:
        """Emit domain events for the completed trade."""
        # Trade executed event
        await self._event_bus.emit(TradeExecutedEvent(
            trade_id=trade.trade_id,
            user_id=trade.user_id,
            asset_symbol=trade.asset.symbol,
            direction=trade.direction.value,
            amount=trade.amount.amount,
            entry_price=trade.entry_price.amount if trade.entry_price else Decimal('0'),
            executed_at=trade.created_at
        ))
        
        # Rewards calculated event
        await self._event_bus.emit(TradingRewardsCalculatedEvent(
            user_id=trade.user_id,
            trade_id=trade.trade_id,
            xp_gained=rewards['xp'],
            achievements_unlocked=[a['id'] for a in rewards['achievements']],
            bonus_items=rewards.get('bonus_items', [])
        ))
    
    async def _get_current_prices_for_portfolio(self, portfolio: Portfolio) -> Dict[str, Money]:
        """Get current market prices for all assets in portfolio."""
        prices = {}
        for asset_symbol in portfolio.positions.keys():
            try:
                current_price = await self._exchange_client.get_current_price(asset_symbol)
                prices[asset_symbol] = Money(current_price, 'USD')
            except Exception as e:
                logger.warning(f"Failed to get price for {asset_symbol}: {e}")
        return prices
    
    async def _get_user_trades_in_period(
        self,
        user_id: int,
        start_time: datetime,
        end_time: datetime
    ) -> List[Trade]:
        """Get user trades within a specific time period."""
        all_trades = await self._trade_repo.get_user_trades(user_id, limit=1000)
        return [
            trade for trade in all_trades
            if start_time <= trade.created_at <= end_time
        ]
    
    def _calculate_battle_metrics(self, trades: List[Trade]) -> Dict[str, Any]:
        """Calculate battle metrics from trades."""
        if not trades:
            return {"trade_count": 0, "total_pnl": Decimal('0'), "win_rate": Decimal('0')}
        
        total_pnl = Decimal('0')
        winning_trades = 0
        
        for trade in trades:
            if trade.entry_price and trade.exit_price:
                pnl = trade.calculate_pnl(trade.exit_price)
                total_pnl += pnl.amount
                if pnl.is_positive():
                    winning_trades += 1
        
        win_rate = Decimal(str(winning_trades)) / Decimal(str(len(trades))) if trades else Decimal('0')
        
        return {
            "trade_count": len(trades),
            "total_pnl": total_pnl,
            "win_rate": win_rate
        }
    
    def _calculate_battle_score_algorithm(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate battle score using domain algorithm."""
        base_score = metrics["total_pnl"]
        consistency_bonus = metrics["win_rate"] * Decimal('100')
        activity_bonus = min(Decimal(str(metrics["trade_count"])) * Decimal('10'), Decimal('200'))
        
        total_score = base_score + consistency_bonus + activity_bonus
        
        return {
            "total_score": max(Decimal('0'), total_score),
            "trade_count": metrics["trade_count"],
            "pnl_usd": metrics["total_pnl"],
            "win_rate": metrics["win_rate"]
        }
    
    def _empty_battle_score(self) -> Dict[str, Any]:
        """Return empty battle score structure."""
        return {
            "total_score": Decimal('0'),
            "trade_count": 0,
            "pnl_usd": Decimal('0'),
            "win_rate": Decimal('0')
        }
    
    def _determine_experience_level(self, trades: List[Trade]) -> str:
        """Determine user experience level based on trading history."""
        if len(trades) < 10:
            return "beginner"
        elif len(trades) < 100:
            return "intermediate"
        else:
            return "advanced"
    
    def _get_daily_trade_limit_for_user(self, user_id: int) -> int:
        """Get daily trade limit based on user level (simplified)."""
        # This would integrate with user domain to get actual user level
        return 20  # Default limit
    
    async def _check_trade_achievements(self, user_id: int, trade: Trade) -> List[Dict[str, str]]:
        """Check if trade unlocks any achievements."""
        achievements = []
        
        # First trade achievement
        user_trades = await self._trade_repo.get_user_trades(user_id)
        if len(user_trades) == 1:
            achievements.append({
                'id': 'first_trade',
                'name': 'First Steps',
                'description': 'Complete your first trade'
            })
        
        return achievements