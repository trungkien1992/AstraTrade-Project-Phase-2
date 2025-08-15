# Development Setup Guide

## Prerequisites

### Required Tools

- **Flutter**: 3.8.1 or higher
- **Dart**: 3.0.0 or higher  
- **Python**: 3.11+ for backend services
- **Node.js**: 18+ for build tools
- **Git**: Latest version

### Development Environment

- **IDE**: VS Code or Android Studio recommended
- **Flutter Extensions**: Flutter and Dart plugins
- **Python Environment**: Virtual environment recommended

## Quick Start

### 1. Clone Repository

```bash
git clone https://github.com/trungkien1992/AstraTrade-Project-Bounty-Submission.git
cd AstraTrade-Project-Phase-2
```

### 2. Frontend Setup

```bash
cd apps/frontend
flutter pub get
flutter run -d chrome
```

### 3. Backend Setup

```bash
cd apps/backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python minimal_server.py
```

### 4. Smart Contracts

```bash
# Install Scarb (Cairo package manager)
curl --proto '=https' --tlsv1.2 -sSf https://docs.swmansion.com/scarb/install.sh | sh

# Compile contracts
scarb build

# Deploy to testnet (optional)
python scripts/deployment/deploy_astratrade_v2.py
```

## Configuration

### Frontend Configuration

**File**: `apps/frontend/lib/config/app_config.dart`

```dart
class AppConfig {
  static const String apiBaseUrl = 'http://localhost:8000';
  static const String environment = 'development';
  static const bool enableMockTrading = true;
}
```

### Backend Configuration

**File**: `apps/backend/core/config.py`

```python
class Settings:
    DATABASE_URL = "postgresql://user:pass@localhost/astratrade"
    REDIS_URL = "redis://localhost:6379"
    DEBUG = True
```

### Environment Variables

Create `.env` file in project root:

```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost/astratrade

# Redis
REDIS_URL=redis://localhost:6379

# Extended Exchange API (for real trading)
EXTENDED_EXCHANGE_API_KEY=your_api_key_here
EXTENDED_EXCHANGE_SECRET=your_secret_here

# Starknet Configuration
STARKNET_ACCOUNT_ADDRESS=0x...
STARKNET_PRIVATE_KEY=0x...
```

## Development Workflow

### 1. Running Services

#### Start Backend Services
```bash
# Terminal 1: Main API Server
cd apps/backend
python run_server_8000.py

# Terminal 2: Redis (if not running as service)
redis-server

# Terminal 3: Database (if using local PostgreSQL)
pg_ctl -D /usr/local/var/postgres start
```

#### Start Frontend
```bash
# Terminal 4: Flutter App
cd apps/frontend
flutter run -d chrome  # For web development
flutter run -d ios     # For iOS simulator
flutter run -d android # For Android emulator
```

### 2. Testing

```bash
# Frontend tests
cd apps/frontend
flutter test

# Backend tests
cd apps/backend
python -m pytest

# Integration tests
python run_integration_tests.py

# Smart contract tests
cd scripts/testing
python test_contracts.py
```

### 3. Database Setup

```bash
# Run migrations
cd apps/backend
alembic upgrade head

# Create test data (optional)
python scripts/create_test_data.py
```

## IDE Configuration

### VS Code Settings

**File**: `.vscode/settings.json`

```json
{
  "dart.flutterSdkPath": "/path/to/flutter",
  "python.pythonPath": "./venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true
}
```

### Recommended Extensions

- Flutter
- Dart
- Python
- GitLens
- Thunder Client (for API testing)
- Cairo (for smart contract development)

## Debugging

### Frontend Debugging

```bash
# Debug mode with hot reload
flutter run --debug

# Debug with specific device
flutter run -d chrome --debug

# Performance profiling
flutter run --profile
```

### Backend Debugging

```bash
# Debug mode with auto-reload
uvicorn main:app --reload --debug

# Database debugging
python -c "from core.database import engine; print(engine.url)"

# Redis debugging
redis-cli ping
```

## Common Issues

### Flutter Issues

**Issue**: Package conflicts
**Solution**: 
```bash
flutter clean
flutter pub get
```

**Issue**: Platform-specific build errors
**Solution**: Check platform-specific configurations in `android/` or `ios/` directories

### Backend Issues

**Issue**: Database connection failed
**Solution**: Verify PostgreSQL is running and credentials are correct

**Issue**: Redis connection failed  
**Solution**: Start Redis server or update connection string

### Smart Contract Issues

**Issue**: Scarb compilation errors
**Solution**: Ensure Cairo version compatibility and update dependencies

**Issue**: Deployment failures
**Solution**: Check account balance and network connectivity

## Performance Tips

- Use `flutter run --release` for performance testing
- Enable database query logging in development
- Monitor Redis memory usage during development
- Use Flutter DevTools for performance profiling

## Getting Help

- Check [Architecture Documentation](../architecture/README.md)
- Review [API Documentation](../api/README.md)
- See [Smart Contracts Guide](../smart-contracts/README.md)
- Post issues on project GitHub repository