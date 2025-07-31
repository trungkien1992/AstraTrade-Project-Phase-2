# AstraTrade Architectural Decision Records (ADRs)

## Overview
This document contains the architectural decision records for AstraTrade's evolution from v1.0 to global scale. These decisions support the roadmap's progression from 5k users to 100k+ MAU with 99.9% uptime and financial-grade reliability.

---

## ADR-001: Domain-Driven Design Adoption for Business Logic Organization

**Status:** Approved for Phase 1 (Months 1-3)  
**Date:** 2025-07-31  
**Context:** Current codebase has 55+ backend services and 50+ frontend services without clear domain boundaries

### Decision
Restructure the entire codebase using Domain-Driven Design (DDD) with bounded contexts to isolate complex business logic.

### Rationale
1. **Business Complexity:** Gamified trading involves multiple complex domains (trading, XP systems, social features, NFTs)
2. **Team Scaling:** Growing from 1 to 8 developers requires clear ownership boundaries
3. **Roadmap Requirements:** 4 distinct revenue streams need domain expertise isolation
4. **Service Explosion:** 55+ services indicate lack of cohesive organization

### Architecture
```
┌─────────────────────────────────────┐
│           Presentation Layer        │
│     (Screens, Controllers, APIs)    │
├─────────────────────────────────────┤
│          Application Layer          │
│    (Use Cases, Command Handlers)    │
├─────────────────────────────────────┤
│           Domain Layer              │
│   (Entities, Value Objects, Rules)  │
├─────────────────────────────────────┤
│        Infrastructure Layer         │
│  (Database, Exchange APIs, Files)   │
└─────────────────────────────────────┘
```

### Bounded Contexts
1. **Trading Domain** - Asset trading, risk management, portfolio tracking
2. **Gamification Domain** - XP system, levels, achievements, streaks  
3. **Social Domain** - Clans, leaderboards, challenges, friend systems
4. **NFT Domain** - Marketplace, minting, rewards, collections
5. **User Domain** - Authentication, profiles, preferences
6. **Financial Domain** - Payments, subscriptions, revenue tracking

### Implementation Plan
- **Phase 1.1:** Extract domain entities and value objects
- **Phase 1.2:** Create domain services (consolidate 55+ services → 6 domain services)
- **Phase 1.3:** Implement clean architecture layers
- **Phase 1.4:** Add domain events for loose coupling

### Consequences
**Positive:**
- Clear ownership boundaries enable team autonomy
- Business logic centralized in domain layer
- Easier testing with isolated domains
- Better maintainability and feature development

**Negative:**  
- Increased initial complexity during migration
- Learning curve for team on DDD patterns
- Potential over-engineering for simple features

---

## ADR-002: Event-Driven Architecture for Real-Time Features

**Status:** Approved for Phase 2 (Months 4-6)  
**Date:** 2025-07-31  
**Context:** Roadmap requires live competitions, real-time leaderboards, and social features for 100k+ users

### Decision
Implement event-driven architecture with CQRS patterns for scalability and real-time capabilities.

### Rationale
1. **Scale Requirements:** 100k+ MAU with <200ms API responses
2. **Real-Time Features:** Live tournaments, competitions, instant leaderboard updates
3. **Social Features:** Real-time notifications, activity feeds, friend challenges
4. **Performance:** Read/write optimization for analytics and dashboards

### Architecture
```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│ Trading Core │    │ Social Core  │    │  NFT Core    │
│   (DDD)      │    │    (DDD)     │    │   (DDD)      │
└──────────────┘    └──────────────┘    └──────────────┘
         │                   │                   │
    ┌────┴───────────────────┴───────────────────┴────┐
    │           Event Bus (Real-time Layer)           │
    │  • Live Competitions  • Social Feed  • Alerts  │
    └─────────────────────────────────────────────────┘
         │                   │                   │
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│ Read Models  │    │ Read Models  │    │ Read Models  │
│ (Optimized)  │    │ (Optimized)  │    │ (Optimized)  │
└──────────────┘    └──────────────┘    └──────────────┘
```

### Event Types
- **Trading Events:** TradeExecuted, PositionClosed, RiskLimitHit
- **Gamification Events:** XPGained, LevelUp, AchievementUnlocked
- **Social Events:** ClanJoined, ChallengeCompleted, LeaderboardUpdated
- **NFT Events:** NFTMinted, MarketplaceSale, RewardClaimed

### CQRS Implementation
- **Command Side:** Domain operations through DDD aggregates
- **Query Side:** Optimized read models for dashboards and analytics
- **Event Store:** Audit trail and replay capabilities for compliance

### Implementation Plan
- **Phase 2.1:** Implement event bus (Redis Streams/NATS)
- **Phase 2.2:** Add CQRS for leaderboards and analytics
- **Phase 2.3:** Real-time WebSocket connections for live features
- **Phase 2.4:** Event sourcing for audit trails

### Consequences
**Positive:**
- Horizontal scalability for 100k+ users
- Real-time features enable engagement and retention
- Optimized read models improve performance
- Event sourcing provides audit trails for compliance

**Negative:**
- Eventual consistency requires careful UX design
- Increased infrastructure complexity
- Monitoring and debugging more challenging

---

## ADR-003: Functional Programming Core for Financial Calculations

**Status:** Approved for Phase 3 (Months 7-12)  
**Date:** 2025-07-31  
**Context:** Real money trading requires mathematical precision and regulatory compliance

### Decision  
Implement functional programming patterns for all financial calculations with immutable data structures and pure functions.

### Rationale
1. **Financial Accuracy:** Real trading with user funds requires mathematical correctness
2. **Audit Requirements:** Regulatory compliance needs immutable audit trails
3. **Risk Management:** Complex position sizing and stop-loss logic must be reliable
4. **Testing:** Pure functions enable property-based testing and formal verification

### Architecture
```
┌─────────────────────────────────────┐
│        Pure Function Layer          │
│  (P&L, Position Sizing, Risk Mgmt)  │
├─────────────────────────────────────┤
│       Effect Management Layer       │
│   (IO, State, Error Handling)       │
├─────────────────────────────────────┤
│        Immutable Data Layer         │
│  (Trade Records, Portfolio State)   │
├─────────────────────────────────────┤
│       Event Sourcing Store          │
│    (Audit Trail, Compliance)        │
└─────────────────────────────────────┘
```

### Core Financial Functions
```typescript
// Pure functions for financial calculations
type Position = {
  readonly asset: string;
  readonly quantity: Decimal;
  readonly entryPrice: Decimal;
  readonly currentPrice: Decimal;
};

const calculatePnL = (position: Position): Decimal => 
  position.quantity.mul(position.currentPrice.sub(position.entryPrice));

const calculatePositionSize = (
  accountBalance: Decimal,
  riskPercentage: Decimal,
  stopLossDistance: Decimal
): Decimal => 
  accountBalance.mul(riskPercentage).div(stopLossDistance);
```

### Implementation Strategy
- **Immutable Data:** All financial data structures are immutable
- **Pure Functions:** No side effects in calculation logic
- **Monadic Error Handling:** Explicit error flows with Maybe/Either types
- **Event Sourcing:** Complete audit trail of all financial operations
- **Property-Based Testing:** Verify mathematical properties hold

### Implementation Plan
- **Phase 3.1:** Rewrite core financial calculations as pure functions
- **Phase 3.2:** Implement immutable position and portfolio data structures  
- **Phase 3.3:** Add property-based testing for all financial logic
- **Phase 3.4:** Formal verification for critical algorithms

### Consequences
**Positive:**
- Mathematical correctness for real money trading
- Immutable audit trails for regulatory compliance
- Easier testing and debugging of financial logic
- Formal verification possible for critical functions

**Negative:**
- Performance overhead from immutable data structures
- Learning curve for functional programming patterns
- More complex state management

---

## ADR-004: Microservices Architecture for Global Scale

**Status:** Approved for Phase 3 (Months 7-12)  
**Date:** 2025-07-31  
**Context:** Global expansion requires 99.9% uptime across multiple regions

### Decision
Decompose monolithic backend into microservices with service mesh for global deployment.

### Rationale
1. **Global Scale:** 100k+ MAU across US, EU, Asia regions
2. **Reliability:** 99.9% uptime SLA requirements
3. **Team Autonomy:** Multiple development teams need independent deployment
4. **Technology Diversity:** Different domains may benefit from different tech stacks

### Microservices Decomposition
```
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│  Trading Service│  │Gamification Svc │  │  Social Service │
│   (Node.js)     │  │   (Python)      │  │   (Go)          │
└─────────────────┘  └─────────────────┘  └─────────────────┘
         │                     │                     │
    ┌────┴─────────────────────┴─────────────────────┴────┐
    │              Service Mesh (Istio)                  │
    │    • Load Balancing  • Circuit Breakers  • TLS    │
    └─────────────────────────────────────────────────────┘
         │                     │                     │
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│   NFT Service   │  │  Auth Service   │  │Financial Service│
│   (Rust)        │  │   (Python)      │  │  (Haskell)      │
└─────────────────┘  └─────────────────┘  └─────────────────┘
```

### Service Boundaries
- **Trading Service:** Trade execution, portfolio management, risk controls
- **Gamification Service:** XP system, achievements, progression tracking
- **Social Service:** Clans, leaderboards, friend systems, messaging
- **NFT Service:** Marketplace, minting, metadata management
- **Auth Service:** Authentication, authorization, user management
- **Financial Service:** Payments, subscriptions, revenue tracking, compliance

### Implementation Plan
- **Phase 3.1:** Containerize existing domain services
- **Phase 3.2:** Implement API gateways and service discovery
- **Phase 3.3:** Deploy service mesh with observability
- **Phase 3.4:** Regional deployment with data locality

### Consequences
**Positive:**
- Independent scaling and deployment per service
- Technology choice flexibility per domain
- Fault isolation and resilience
- Team autonomy and faster development

**Negative:**
- Distributed system complexity
- Network latency between services  
- Data consistency challenges
- Operational overhead

---

## ADR-005: Cairo Smart Contract Evolution

**Status:** Approved for All Phases  
**Date:** 2025-07-31  
**Context:** Current contracts are basic; roadmap requires advanced DeFi features

### Decision
Evolve Cairo smart contracts using modular architecture with formal verification for financial operations.

### Rationale
1. **DeFi Integration:** Roadmap includes yield farming, staking, lending protocols
2. **Financial Security:** Real money requires formally verified contract logic
3. **Scalability:** Modular contracts enable feature expansion
4. **Compliance:** Regulatory requirements for on-chain operations

### Contract Architecture Evolution
```
Phase 1: Basic Contracts (Current)
├── Paymaster (gasless transactions)
├── Vault (asset storage) 
└── Exchange (basic trading)

Phase 2: Advanced DeFi Contracts
├── StakingManager (yield generation)
├── LendingPool (capital efficiency)
├── GovernanceToken (DAO features)
└── RewardsDistributor (tokenomics)

Phase 3: Cross-Chain & Enterprise
├── BridgeConnector (multi-chain)
├── ComplianceModule (regulatory)
├── InstitutionalVault (enterprise)
└── FormallyVerifiedCore (critical math)
```

### Implementation Plan
- **Phase 1:** Optimize existing contracts, add comprehensive testing
- **Phase 2:** Implement advanced DeFi modules with modular architecture
- **Phase 3:** Add formal verification and cross-chain capabilities

### Consequences
**Positive:**
- Modular architecture enables rapid feature development
- Formal verification ensures financial correctness
- Advanced DeFi features unlock new revenue streams

**Negative:**
- Formal verification requires specialized expertise
- Cross-chain complexity increases attack surface
- Gas optimization challenges with complex logic

---

## Migration Strategy

### Parallel Development Approach
1. **New Architecture Development:** Build alongside existing system
2. **Feature Flags:** Control rollout and enable A/B testing
3. **Gradual Migration:** Move domain by domain over 6-12 months
4. **Rollback Capability:** Always maintain fallback to previous architecture

### Success Metrics by Phase

**Phase 1 Success Metrics:**
- Service count reduced from 55+ to 6 domain services
- Clear domain boundaries established
- Development velocity increased by 30%
- Bug reduction of 40% due to better testing

**Phase 2 Success Metrics:**  
- API response times <200ms for 95th percentile
- Real-time features operational with <100ms latency
- Horizontal scaling demonstrated with load testing
- Event throughput of 10,000+ events/second

**Phase 3 Success Metrics:**
- 99.9% uptime SLA achieved
- 100k+ MAU supported across global regions
- All financial calculations formally verified
- Zero financial discrepancies in audit

---

## Conclusion

These architectural decisions provide a clear evolution path from AstraTrade's current v1.0 state to a globally scalable, financially reliable, and technically advanced platform. Each decision is justified by specific roadmap requirements and supports the ambitious growth targets outlined in the development roadmap.

The phased approach ensures risk mitigation while maintaining development velocity and user experience quality throughout the transformation.

---

**Document Version:** 1.0  
**Last Updated:** July 31, 2025  
**Next Review:** September 1, 2025