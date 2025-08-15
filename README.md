# AstraTrade - Gamified Perpetuals Trading App

> **StarkWare Bounty Submission**: Cross-platform Flutter app transforming DeFi trading into an intuitive, cosmic gaming experience

[![StarkWare Bounty](https://img.shields.io/badge/StarkWare-Bounty%20Submission-blue)](https://github.com/trungkien1992/AstraTrade-Project-Bounty-Submission)
[![Flutter](https://img.shields.io/badge/Flutter-3.8.1+-blue)](https://flutter.dev)
[![Starknet](https://img.shields.io/badge/Starknet-Cairo%20Contracts-green)](https://www.starknet.io)

---

## 🚀 Quick Start

### 5-Minute Evaluation

```bash
git clone https://github.com/trungkien1992/AstraTrade-Project-Bounty-Submission.git
cd AstraTrade-Project-Phase-2
cd apps/frontend && flutter pub get && flutter run -d chrome
```

**🎯 Test Flow**: Experience Selection → Virtual Balance → Goals → Trading Interface → Results

### Full Setup

See [Development Setup Guide](docs/development/setup.md) for complete installation instructions.

---

## 🏆 StarkWare Bounty Status

**All bounty requirements successfully fulfilled and ready for evaluation.**

| Requirement | Status | Documentation |
|-------------|--------|---------------|
| **Extended Exchange API** | ✅ **COMPLETE** | [API Integration](docs/api/extended-exchange.md) |
| **Smart Contract Development** | ✅ **COMPLETE** | [Smart Contracts](docs/smart-contracts/README.md) |
| **Real Transaction Capability** | ✅ **VERIFIED** | [Deployment Guide](docs/smart-contracts/deployment.md) |
| **Code Quality** | ✅ **IMPROVED** | [Architecture Docs](docs/architecture/README.md) |

**📋 Complete Details**: [Bounty Submission Documentation](docs/project/bounty-submission.md)

---

## 🎮 What is AstraTrade?

AstraTrade transforms complex blockchain trading into an engaging, cosmic gaming experience:

### Core Features
- **🌌 Cosmic Trading Experience** - Space-themed gamification of DeFi trading
- **🎯 Risk-Free Learning** - Practice with virtual funds before real trading
- **🔐 Web3Auth Integration** - One-tap social login (Google/Apple)
- **⚡ Real Trading Capability** - Extended Exchange API for live trades
- **🎨 Gamified Experience** - XP, levels, achievements, and leaderboards
- **📱 Mobile-First Design** - Native iOS/Android with cross-platform web support

### Technology Stack
- **Frontend**: Flutter with Starknet.dart integration
- **Backend**: FastAPI microservices architecture
- **Smart Contracts**: Cairo contracts on Starknet
- **Trading**: Extended Exchange API integration
- **Authentication**: Web3Auth with biometric support

---

## 📚 Documentation

### Quick Navigation

- **🎯 [Project Overview](docs/project/README.md)** - Team, roadmap, and project status
- **🏗️ [Architecture](docs/architecture/README.md)** - System design and technical decisions  
- **🛠️ [Development](docs/development/setup.md)** - Setup, configuration, and deployment
- **📡 [API Documentation](docs/api/backend-api.md)** - Backend and External API integration
- **🔗 [Smart Contracts](docs/smart-contracts/README.md)** - Cairo contracts and deployment
- **🔍 [Analysis](docs/analysis/technical-debt.md)** - Security, performance, and technical analysis

### Getting Started

1. **New to AstraTrade?** → Start with [Project Overview](docs/project/README.md)
2. **Setting up development?** → See [Development Setup](docs/development/setup.md)  
3. **Understanding the architecture?** → Review [Architecture Docs](docs/architecture/README.md)
4. **Deploying to production?** → Follow [Deployment Guide](docs/development/deployment.md)

---

## 🚀 Key Achievements

### ✅ Bounty Delivery Excellence
- **Production-Ready**: Complete Flutter mobile app with backend services
- **Real Trading**: Live Extended Exchange API integration with HMAC authentication
- **Smart Contracts**: Cairo contracts deployed and verified on Starknet Sepolia
- **Code Quality**: Professional architecture with comprehensive testing

### ✅ Technical Innovation  
- **Gasless Transactions**: AVNU paymaster integration for seamless UX
- **Cosmic Gamification**: Unique space-themed trading experience
- **Cross-Platform**: Flutter app supporting iOS, Android, and Web
- **Microservices**: Scalable backend with domain-driven design

### ✅ Security & Performance
- **Security Hardening**: Comprehensive vulnerability analysis and remediation
- **Performance Optimization**: Sub-second response times and efficient resource usage
- **Production Ready**: Load balancing, monitoring, and deployment automation

---

## 🛠️ Development

### Prerequisites
- Flutter 3.8.1+
- Python 3.11+
- PostgreSQL and Redis
- Scarb (Cairo package manager)

### Local Development
```bash
# Backend services
cd apps/backend && python run_server_8000.py

# Frontend application  
cd apps/frontend && flutter run -d chrome

# Smart contracts
scarb build && python scripts/deployment/deploy_astratrade_v2.py
```

**📖 Full Instructions**: [Development Setup Guide](docs/development/setup.md)

---

## 🤝 Contributing

AstraTrade is a StarkWare bounty submission project. For development and contribution guidelines:

1. Review [Architecture Documentation](docs/architecture/README.md)
2. Follow [Development Setup](docs/development/setup.md)
3. Check [Technical Analysis](docs/analysis/technical-debt.md)
4. See [Team Information](docs/project/team.md)

---

## 📄 License

This project is part of a StarkWare bounty submission. All rights reserved.

**Project Repository**: [AstraTrade-Project-Bounty-Submission](https://github.com/trungkien1992/AstraTrade-Project-Bounty-Submission)

---

**🎯 Ready for StarkWare Evaluation** | **📱 Mobile-First DeFi Trading** | **🌌 Cosmic Gaming Experience**