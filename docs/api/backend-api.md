# 🚀 AstraTrade Backend API

> **FastAPI service powering mobile-first gamified perpetuals trading**

The AstraTrade backend is a high-performance FastAPI service that handles all trading logic, user management, XP systems, and leaderboard features. It's specifically optimized for mobile applications with comprehensive authentication, gasless transaction support, and real-time gamification mechanics.

## 📖 Table of Contents

- [🌟 Features](#-features)
- [🛠️ Tech Stack](#️-tech-stack)
- [🚀 Quick Start](#-quick-start)
- [📚 API Documentation](#-api-documentation)
- [🔐 Authentication](#-authentication)
- [🎮 Gamification System](#-gamification-system)
- [💰 Trading Integration](#-trading-integration)
- [🏗️ Architecture](#️-architecture)
- [🧪 Testing](#-testing)
- [🔧 Configuration](#-configuration)
- [📊 Monitoring](#-monitoring)

## 🌟 Features

### Core Functionality
- **User Management**: Registration, authentication, profile management
- **Trading Endpoints**: Mock and real trading with Extended Exchange API
- **XP & Gamification**: Experience points, levels, achievements, streaks
- **Leaderboards**: Real-time rankings and competitive features
- **Daily Rewards**: Automated reward system for mobile engagement

### Mobile-Optimized
- **Gasless Transactions**: Paymaster integration for seamless UX
- **Real-time Updates**: WebSocket support for live data
- **Mobile Performance**: Optimized API responses for mobile networks
- **Push Notifications**: Integration-ready for mobile notifications

### Security & Compliance
- **JWT Authentication**: Secure session management
- **Rate Limiting**: API protection against abuse
- **Input Validation**: Comprehensive data validation
- **Security Headers**: Production-ready security middleware

## 🛠️ Tech Stack

### Core Framework
- **FastAPI**: Modern, fast web framework for building APIs
- **Python 3.9+**: Modern Python with async/await support
- **Uvicorn**: Lightning-fast ASGI server
- **Pydantic**: Data validation using Python type annotations

### Database & Storage
- **SQLAlchemy**: SQL toolkit and ORM
- **SQLite/PostgreSQL**: Development and production databases
- **Alembic**: Database migration management

### External Integrations
- **Extended Exchange API**: Real perpetuals trading
- **Starknet**: Blockchain interaction and paymaster support
- **Web3Auth**: Social authentication integration

### Development & Operations
- **Pytest**: Comprehensive testing framework
- **FastAPI Testing**: Built-in testing utilities
- **Prometheus**: Metrics and monitoring
- **Sentry**: Error tracking and performance monitoring

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- pip or pipenv
- SQLite (included) or PostgreSQL (production)

### Development Setup

1. **Clone and navigate to backend**:
   ```bash
   cd astratrade_backend
   ```

2. **Create virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Initialize database**:
   ```bash
   python -m core.database init
   ```

6. **Start development server**:
   ```bash
   uvicorn core.main:app --reload --port 8001
   ```

7. **Access API documentation**:
   - Swagger UI: http://localhost:8001/docs
   - ReDoc: http://localhost:8001/redoc

## 📚 API Documentation

### Authentication Endpoints
| Method | Endpoint | Description | Authentication |
|--------|----------|-------------|----------------|
| POST | `/register` | Register new user | None |
| POST | `/login` | User login | None |
| GET | `/users/me` | Get current user | Bearer Token |

### Trading Endpoints
| Method | Endpoint | Description | Authentication |
|--------|----------|-------------|----------------|
| POST | `/trade` | Place a trade (auto-detects mock/real) | Bearer Token |
| POST | `/trade/mock` | Place a mock trade | Bearer Token |
| POST | `/trade/real` | Place a real trade | Bearer Token |
| GET | `/trades` | Get user's trade history | Bearer Token |
| GET | `/portfolio/balance` | Get portfolio balance | Bearer Token |

### Gamification Endpoints
| Method | Endpoint | Description | Authentication |
|--------|----------|-------------|----------------|
| POST | `/xp/add` | Add XP to user | Bearer Token |
| GET | `/leaderboard` | Get global leaderboard | None |
| POST | `/rewards/daily` | Award daily rewards | Admin |
| POST | `/mobile/daily-check-in` | Daily check-in for mobile users | Bearer Token |

### System Endpoints
| Method | Endpoint | Description | Authentication |
|--------|----------|-------------|----------------|
| GET | `/health` | Health check | None |
| GET | `/metrics` | Prometheus metrics | None |

### Request/Response Examples

**Place a Trade**:
```bash
curl -X POST "http://localhost:8001/trade" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "asset": "BTC/USD",
    "direction": "long",
    "amount": 100.0
  }'
```

**Response**:
```json
{
  "trade_id": 123,
  "outcome": "profit",
  "profit_percentage": 2.5,
  "message": "Trade successful! +2.5% profit",
  "xp_gained": 25
}
```

## 🔐 Authentication

### JWT Token System
- **Access Tokens**: Short-lived tokens for API access
- **Refresh Tokens**: Long-lived tokens for session management
- **Token Rotation**: Automatic token refresh for security

### Web3Auth Integration
- **Social Login**: Google, Twitter, Discord authentication
- **Wallet Connection**: Seamless blockchain account linking
- **Account Abstraction**: No private key management required

### Security Features
- **Rate Limiting**: Protection against brute force attacks
- **CORS Configuration**: Secure cross-origin resource sharing
- **Security Headers**: HSTS, CSP, X-Frame-Options, etc.
- **Input Sanitization**: SQL injection and XSS protection

## 🎮 Gamification System

### XP & Levels
- **XP Sources**: Trading, daily check-ins, achievements, streaks
- **Level Calculation**: `level = 1 + (xp // 100)`
- **XP Multipliers**: Streak bonuses, activity rewards, special events

### Achievement System
- **Trade-based**: Volume milestones, profit targets, streak achievements
- **NFT Rewards**: On-chain achievement tokens via AchievementNFT contract
- **Rarity Tiers**: Common, Rare, Epic, Legendary achievements

### Daily Rewards
- **Check-in Bonuses**: Mobile-optimized daily engagement
- **Streak Multipliers**: Consecutive day bonuses
- **Activity Rewards**: Trading volume and frequency bonuses

### Leaderboard System
- **Global Rankings**: XP-based competitive leaderboards
- **Time-based Boards**: Daily, weekly, monthly rankings
- **Clan System**: Team-based competition (future feature)

## 💰 Trading Integration

### Extended Exchange API
- **Real Trading**: Live perpetuals trading via Extended API
- **Mock Trading**: Simulated trading for free-to-play users
- **Risk Management**: Position limits, daily trading caps

### Paymaster Integration
- **Gasless UX**: Zero transaction fees for users
- **Starknet L2**: Fast, cheap blockchain interactions
- **Automated Sponsorship**: Smart contract gas fee coverage

### Portfolio Management
- **Balance Tracking**: Real-time portfolio valuation
- **P&L Calculation**: Profit/loss tracking and history
- **Risk Metrics**: Exposure, volatility, performance analytics

## 🏗️ Architecture

### Directory Structure
```
astratrade_backend/
├── core/                    # Core application logic
│   ├── main.py             # FastAPI application and routes
│   ├── database.py         # Database models and connection
│   └── config.py           # Configuration management
├── auth/                   # Authentication system
│   └── auth.py             # JWT and Web3Auth integration
├── services/               # Business logic services
│   ├── trading_service.py  # Trading logic and API integration
│   ├── extended_exchange_client.py  # Extended API client
│   └── game_service.py     # Gamification logic
├── models/                 # Data models
│   └── game_models.py      # Game-specific data structures
└── utils/                  # Utility functions
    └── logging.py          # Structured logging
```

### Database Schema
- **Users**: User profiles, authentication, XP, levels
- **Trades**: Trade history, outcomes, performance metrics
- **Achievements**: NFT achievements, unlock conditions
- **Daily Rewards**: Reward history, streak tracking

### External Dependencies
- **Extended Exchange**: Real trading execution
- **Starknet Network**: Blockchain interactions
- **Web3Auth**: Social authentication
- **Paymaster Contract**: Gasless transaction sponsorship

## 🧪 Testing

### Test Coverage
- **Unit Tests**: Individual function testing
- **Integration Tests**: API endpoint testing
- **Contract Tests**: Blockchain interaction testing
- **Performance Tests**: Load and stress testing

### Running Tests
```bash
# Install test dependencies
pip install pytest pytest-asyncio pytest-cov

# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_trading.py
```

### Test Categories
- **Authentication**: User registration, login, token validation
- **Trading**: Mock/real trades, portfolio management
- **Gamification**: XP calculation, achievement unlocks
- **Database**: Model validation, migration testing

## 🔧 Configuration

### Environment Variables
```bash
# Database
DATABASE_URL="sqlite:///./astratrade.db"

# Authentication
SECRET_KEY="your-secret-key"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30

# External APIs
EXTENDED_API_KEY="your-extended-api-key"
EXTENDED_API_URL="https://api.extended.exchange"

# Starknet
STARKNET_NETWORK="testnet"
PAYMASTER_ADDRESS="0x..."

# Monitoring
SENTRY_DSN="your-sentry-dsn"
```

### Production Configuration
- **Database**: PostgreSQL with connection pooling
- **Redis**: Caching and session storage
- **SSL/TLS**: HTTPS enforcement
- **Load Balancing**: Multiple instance deployment

## 📊 Monitoring

### Metrics Collection
- **Prometheus**: Custom metrics for trading, user activity
- **Grafana**: Dashboard for monitoring and alerting
- **Performance**: API response times, error rates

### Health Checks
- **Database**: Connection and query performance
- **External APIs**: Extended Exchange, Starknet availability
- **System**: Memory usage, CPU utilization

### Error Tracking
- **Sentry**: Real-time error monitoring
- **Structured Logging**: JSON-formatted logs for analysis
- **Alert System**: Critical error notifications

---

## 🤝 Contributing

1. Follow the [Security Setup Guide](../SECURITY_SETUP.md)
2. Set up development environment
3. Run tests before submitting changes
4. Follow FastAPI best practices
5. Update documentation for new features

## 📚 Additional Resources

- [Main Project Documentation](../README.md)
- [Frontend Configuration](../astratrade-frontend/CONFIGURATION.md)
- [Game Design Document](../docs/game_design.md)
- [Security Setup Guide](../SECURITY_SETUP.md)

---

*Built for mobile-first DeFi gaming on Starknet* 