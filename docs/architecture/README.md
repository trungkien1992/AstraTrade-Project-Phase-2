# AstraTrade Architecture Documentation

This section contains comprehensive technical documentation for the AstraTrade system architecture.

## 📁 Architecture Overview

### Core Documents

- **[Current Architecture](current-architecture.md)**: The single source of truth for the system's architecture and the 8-week "Infrastructure Bridge" roadmap
- **[Architectural Decision Records](decision-records.md)**: The rationale and context behind key architectural decisions

### Domain Architecture

The system follows Domain-Driven Design principles with the following domains:

- **[Trading Domain](domain-design/trading.md)**: Core trading logic, risk management, and portfolio handling
- **[Gamification Domain](domain-design/gamification.md)**: XP systems, achievements, leaderboards, and engagement mechanics
- **[Financial Domain](domain-design/financial.md)**: Asset management, balance tracking, and financial operations
- **[User Domain](domain-design/user.md)**: User management, authentication, and profile handling
- **[Social Domain](domain-design/social.md)**: Friend systems, challenges, and social features
- **[NFT Domain](domain-design/nft.md)**: NFT collection, marketplace, and minting functionality

## 🏗️ System Overview

AstraTrade implements a modern microservices architecture with:

- **Frontend**: Flutter mobile application with Starknet integration
- **Backend**: FastAPI-based microservices with domain separation
- **Smart Contracts**: Cairo contracts on Starknet for gasless transactions
- **External Integrations**: Extended Exchange API for real trading
- **Infrastructure**: Redis for event streaming, PostgreSQL for persistence

## 🎯 Quick Navigation

- **For system architecture overview**: Start with [Current Architecture](current-architecture.md)
- **For architectural decisions**: See [Decision Records](decision-records.md)  
- **For domain-specific details**: Browse the [Domain Design](domain-design/) directory
- **For smart contracts**: See [Smart Contracts Documentation](../smart-contracts/README.md)

## 🔄 Architecture Evolution

The system has evolved through several phases:

1. **Phase 0**: Bounty delivery with MVP functionality
2. **Phase 1**: User service foundation and basic trading
3. **Phase 2A**: Microservices architecture implementation
4. **Phase 2B**: Event-driven architecture and real-time features
5. **Phase 3**: Advanced features and production optimization

Each phase builds upon the previous one while maintaining backward compatibility and system stability.