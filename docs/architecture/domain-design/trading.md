# Trading Domain Architecture

## Overview

The Trading Domain implements the core business logic for perpetual futures trading within AstraTrade. It follows Domain-Driven Design principles and uses a centralized domain logic with delegated execution pattern.

## Architecture Pattern

### Core Design: Centralization & Delegation

1. **Centralized Domain Logic**: The Trading Domain is implemented within the AstraTrade backend using Domain-Driven Design. It encapsulates all core business rules, risk management, and portfolio logic.

2. **Delegated Execution**: The actual execution of trades is delegated to an external service, **Extended Exchange**, via a clean `ExchangeClient` protocol.

## Domain Structure

```
domains/trading/
├── entities.py          # Core domain entities
├── value_objects.py     # Value objects and enums
├── services.py          # Domain services
└── tests/              # Domain tests
```

## Key Components

### Entities

- **Trade**: Represents a trading position with entry/exit prices, quantities, and P&L
- **TradingSession**: Manages multiple trades within a session
- **Portfolio**: Tracks overall trading performance and balances

### Value Objects

- **Asset**: Enumeration of supported trading assets (ETH, BTC, SOL, etc.)
- **TradeDirection**: Long or Short positions
- **Money**: Monetary values with currency specification
- **TradeStatus**: Active, Closed, Pending, Failed states

### Services

- **TradingService**: Core trading orchestration
- **RiskManagementService**: Position sizing and risk validation
- **PortfolioService**: Balance and performance tracking

## Integration Points

### External Exchange Integration

The Trading Domain integrates with Extended Exchange through:

- **Real-time market data**: Price feeds and market information
- **Order execution**: Trade placement and management
- **Account management**: Balance queries and position tracking

### Event System

The domain publishes events for:

- Trade execution completion
- Portfolio updates
- Risk threshold breaches
- Session state changes

## Risk Management

The domain implements comprehensive risk management:

- **Position sizing**: Maximum position limits based on account balance
- **Stop-loss automation**: Automatic trade closure on adverse price movements
- **Portfolio limits**: Overall exposure caps across all positions
- **Leverage controls**: Maximum leverage per trade and overall

## Testing Strategy

- **Unit tests**: Domain logic and business rules
- **Integration tests**: External API interactions
- **Performance tests**: High-frequency trading scenarios
- **Validation tests**: Risk management and compliance rules

## Implementation Status

- ✅ **Core Entities**: Complete implementation with full test coverage
- ✅ **Value Objects**: All trading-related value objects implemented
- ✅ **Domain Services**: Trading orchestration and risk management
- ✅ **External Integration**: Extended Exchange API client
- ✅ **Event Publishing**: Redis-based event system
- 🔄 **Advanced Features**: Portfolio analytics and reporting (in progress)

## Future Enhancements

- Advanced order types (stop-limit, trailing stops)
- Multi-asset portfolio optimization
- Algorithmic trading strategies
- Performance analytics and reporting
- Real-time risk monitoring dashboard