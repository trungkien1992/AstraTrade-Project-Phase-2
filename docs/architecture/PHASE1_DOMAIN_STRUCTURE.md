# Phase 1: Domain-Driven Design Structure for AstraTrade

## Overview
This document defines the Domain-Driven Design structure for AstraTrade's Phase 1 architectural transformation. The goal is to consolidate 55+ backend services and 50+ frontend services into 6 clear domain boundaries with clean architecture layers.

---

## Bounded Context Map

```
┌─────────────────────────────────────────────────────────────────┐
│                        AstraTrade Ecosystem                     │
├─────────────────┬─────────────────┬─────────────────────────────┤
│  Trading Domain │Gamification Dm  │        Social Domain        │
│                 │                 │                             │
│ • Risk Mgmt     │ • XP System     │ • Clans & Challenges        │
│ • Portfolio     │ • Achievements  │ • Leaderboards              │
│ • Real Trading  │ • Streaks       │ • Friend Systems            │
│ • Paper Trading │ • Levels        │ • Activity Feeds            │
├─────────────────┼─────────────────┼─────────────────────────────┤
│   NFT Domain    │  User Domain    │      Financial Domain       │
│                 │                 │                             │
│ • Marketplace   │ • Authentication│ • Subscriptions             │
│ • Minting       │ • Profiles      │ • Revenue Tracking          │
│ • Collections   │ • Preferences   │ • Payment Processing        │
│ • Rewards       │ • Onboarding    │ • Compliance                │
└─────────────────┴─────────────────┴─────────────────────────────┘
```

---

## Domain Structure Details

### 1. Trading Domain

**Responsibility:** Core trading functionality, risk management, and portfolio tracking

#### Domain Entities
```typescript
// Core Trading Entities
class Trade {
  readonly id: TradeId;
  readonly userId: UserId;
  readonly asset: Asset;
  readonly direction: TradeDirection; // LONG | SHORT
  readonly amount: Money;
  readonly entryPrice: Price;
  readonly exitPrice?: Price;
  readonly status: TradeStatus;
  readonly createdAt: DateTime;
  readonly closedAt?: DateTime;
}

class Portfolio {
  readonly userId: UserId;
  readonly positions: ReadonlyArray<Position>;
  readonly totalValue: Money;
  readonly availableBalance: Money;
  readonly totalPnL: Money;
}

class Position {
  readonly asset: Asset;
  readonly quantity: Decimal;
  readonly averageEntryPrice: Price;
  readonly currentPrice: Price;
  readonly unrealizedPnL: Money;
}
```

#### Value Objects
```typescript
class Asset {
  constructor(
    readonly symbol: string,
    readonly name: string,
    readonly category: AssetCategory
  ) {}
}

class Money {
  constructor(
    readonly amount: Decimal,
    readonly currency: Currency
  ) {}
}

class RiskParameters {
  readonly maxPosition: Percentage;
  readonly stopLoss: Percentage;
  readonly takeProfit: Percentage;
}
```

#### Domain Services
```typescript
class TradingDomainService {
  async executeTrade(command: ExecuteTradeCommand): Promise<TradeResult>;
  async calculateRisk(portfolio: Portfolio, trade: Trade): Promise<RiskAssessment>;
  async updatePortfolio(userId: UserId): Promise<Portfolio>;
}

class RiskManagementService {
  validateTrade(portfolio: Portfolio, trade: Trade): ValidationResult;
  calculatePositionSize(balance: Money, risk: RiskParameters): Money;
}
```

#### Services to Consolidate
- `trading_service.py` → `TradingDomainService`
- `extended_trading_service.dart` → `TradingDomainService`
- `live_trading_service.dart` → `TradingDomainService`
- `simple_trading_service.dart` → `TradingDomainService`
- `real_trading_service.dart` → `TradingDomainService`
- `trading_stats_service.dart` → `TradingAnalyticsService`

---

### 2. Gamification Domain

**Responsibility:** XP system, achievements, levels, streaks, and progression mechanics

#### Domain Entities
```typescript
class UserProgression {
  readonly userId: UserId;
  readonly currentXP: XP;
  readonly currentLevel: Level;
  readonly streak: Streak;
  readonly achievements: ReadonlyArray<Achievement>;
}

class Achievement {
  readonly id: AchievementId;
  readonly name: string;
  readonly description: string;
  readonly criteria: AchievementCriteria;
  readonly reward: XP;
  readonly rarity: AchievementRarity;
}

class Streak {
  readonly type: StreakType; // DAILY_LOGIN | TRADING | LEARNING
  readonly currentCount: number;
  readonly bestCount: number;
  readonly lastActivityDate: Date;
}
```

#### Value Objects
```typescript
class XP {
  constructor(readonly points: number) {
    if (points < 0) throw new Error("XP cannot be negative");
  }
  
  add(amount: number): XP {
    return new XP(this.points + amount);
  }
}

class Level {
  constructor(readonly value: number) {}
  
  static fromXP(xp: XP): Level {
    return new Level(Math.floor(xp.points / 100) + 1);
  }
}
```

#### Domain Services
```typescript
class GamificationDomainService {
  async awardXP(userId: UserId, activity: Activity): Promise<XPAward>;
  async checkAchievements(userId: UserId): Promise<Achievement[]>;
  async updateStreak(userId: UserId, activity: Activity): Promise<Streak>;
}

class AchievementEngine {
  evaluateAchievements(userActivity: UserActivity): Achievement[];
  calculateXPReward(achievement: Achievement): XP;
}
```

#### Services to Consolidate
- `simple_gamification_service.dart` → `GamificationDomainService`
- `xp_service.dart` → `GamificationDomainService`
- `gamification_integration.dart` → `GamificationDomainService`

---

### 3. Social Domain

**Responsibility:** Clans, leaderboards, friend systems, challenges, and social interactions

#### Domain Entities
```typescript
class Clan {
  readonly id: ClanId;
  readonly name: string;
  readonly description: string;
  readonly members: ReadonlyArray<ClanMember>;
  readonly totalXP: XP;
  readonly level: ClanLevel;
  readonly createdAt: DateTime;
}

class Challenge {
  readonly id: ChallengeId;
  readonly name: string;
  readonly description: string;
  readonly participants: ReadonlyArray<UserId>;
  readonly duration: Duration;
  readonly reward: XP;
  readonly status: ChallengeStatus;
}

class Leaderboard {
  readonly period: LeaderboardPeriod; // DAILY | WEEKLY | MONTHLY | ALL_TIME
  readonly entries: ReadonlyArray<LeaderboardEntry>;
  readonly lastUpdated: DateTime;
}
```

#### Value Objects
```typescript
class ClanMember {
  constructor(
    readonly userId: UserId,
    readonly role: ClanRole,
    readonly contributedXP: XP,
    readonly joinedAt: DateTime
  ) {}
}

class LeaderboardEntry {
  constructor(
    readonly userId: UserId,
    readonly username: string,
    readonly xp: XP,
    readonly level: Level,
    readonly rank: number
  ) {}
}
```

#### Domain Services
```typescript
class SocialDomainService {
  async createClan(command: CreateClanCommand): Promise<Clan>;
  async joinClan(userId: UserId, clanId: ClanId): Promise<void>;
  async updateLeaderboard(period: LeaderboardPeriod): Promise<Leaderboard>;
}

class ChallengeEngine {
  createChallenge(template: ChallengeTemplate): Challenge;
  evaluateProgress(challenge: Challenge): ChallengeProgress;
}
```

#### Services to Consolidate
- `leaderboard_service.dart` → `SocialDomainService`
- `simple_social_service.dart` → `SocialDomainService` 
- `friend_challenges_service.dart` → `SocialDomainService`
- `social_sharing_service.dart` → `SocialDomainService`
- `clan_trading_service.py` → `SocialDomainService`

---

### 4. NFT Domain

**Responsibility:** NFT marketplace, minting, collections, and reward distribution

#### Domain Entities
```typescript
class NFTCollection {
  readonly id: CollectionId;
  readonly name: string;
  readonly description: string;
  readonly items: ReadonlyArray<NFTItem>;
  readonly totalSupply: number;
  readonly creator: UserId;
}

class NFTItem {
  readonly id: NFTId;
  readonly collectionId: CollectionId;
  readonly tokenId: string;
  readonly metadata: NFTMetadata;
  readonly owner: UserId;
  readonly rarity: NFTRarity;
  readonly mintedAt: DateTime;
}

class MarketplaceListing {
  readonly nftId: NFTId;
  readonly seller: UserId;
  readonly price: Money;
  readonly currency: Currency;
  readonly listedAt: DateTime;
  readonly expiresAt: DateTime;
}
```

#### Value Objects
```typescript
class NFTMetadata {
  constructor(
    readonly name: string,
    readonly description: string,
    readonly image: string,
    readonly attributes: ReadonlyArray<NFTAttribute>
  ) {}
}

class NFTAttribute {
  constructor(
    readonly trait_type: string,
    readonly value: string,
    readonly rarity: number
  ) {}
}
```

#### Domain Services
```typescript
class NFTDomainService {
  async mintNFT(command: MintNFTCommand): Promise<NFTItem>;
  async listForSale(nftId: NFTId, price: Money): Promise<MarketplaceListing>;
  async purchaseNFT(listingId: ListingId, buyer: UserId): Promise<void>;
}

class NFTRewardDistributor {
  async awardNFTReward(userId: UserId, achievement: Achievement): Promise<NFTItem>;
  calculateRarity(attributes: NFTAttribute[]): NFTRarity;
}
```

#### Services to Consolidate
- `nft_service.dart` → `NFTDomainService`

---

### 5. User Domain

**Responsibility:** User authentication, profiles, preferences, and onboarding

#### Domain Entities
```typescript
class User {
  readonly id: UserId;
  readonly email: Email;
  readonly username: Username;
  readonly profile: UserProfile;
  readonly preferences: UserPreferences;
  readonly createdAt: DateTime;
  readonly isActive: boolean;
}

class UserProfile {
  readonly displayName: string;
  readonly avatar?: string;
  readonly bio?: string;
  readonly experienceLevel: ExperienceLevel;
  readonly tradingGoals: ReadonlyArray<TradingGoal>;
}

class OnboardingProgress {
  readonly userId: UserId;
  readonly completedSteps: ReadonlyArray<OnboardingStep>;
  readonly currentStep: OnboardingStep;
  readonly isCompleted: boolean;
}
```

#### Value Objects
```typescript
class Email {
  constructor(readonly value: string) {
    if (!this.isValid(value)) {
      throw new Error("Invalid email format");
    }
  }
  
  private isValid(email: string): boolean {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  }
}

class Username {
  constructor(readonly value: string) {
    if (value.length < 3 || value.length > 20) {
      throw new Error("Username must be 3-20 characters");
    }
  }
}
```

#### Domain Services
```typescript
class UserDomainService {
  async registerUser(command: RegisterUserCommand): Promise<User>;
  async updateProfile(userId: UserId, profile: UserProfile): Promise<void>;
  async completeOnboardingStep(userId: UserId, step: OnboardingStep): Promise<void>;
}

class AuthenticationService {
  async authenticateUser(credentials: UserCredentials): Promise<AuthToken>;
  async refreshToken(token: RefreshToken): Promise<AuthToken>;
}
```

#### Services to Consolidate
- `auth_service.dart` → `UserDomainService`
- `unified_wallet_setup_service.dart` → `UserDomainService`
- `wallet_import_service.dart` → `UserDomainService`

---

### 6. Financial Domain

**Responsibility:** Payments, subscriptions, revenue tracking, and financial compliance

#### Domain Entities
```typescript
class Subscription {
  readonly id: SubscriptionId;
  readonly userId: UserId;
  readonly plan: SubscriptionPlan;
  readonly status: SubscriptionStatus;
  readonly currentPeriodStart: DateTime;
  readonly currentPeriodEnd: DateTime;
  readonly cancelAtPeriodEnd: boolean;
}

class Payment {
  readonly id: PaymentId;
  readonly userId: UserId;
  readonly amount: Money;
  readonly currency: Currency;
  readonly status: PaymentStatus;
  readonly gateway: PaymentGateway;
  readonly createdAt: DateTime;
}

class RevenueRecord {
  readonly userId: UserId;
  readonly source: RevenueSource; // SUBSCRIPTION | NFT_SALE | API_SHARE
  readonly amount: Money;
  readonly recordedAt: DateTime;
}
```

#### Value Objects
```typescript
class SubscriptionPlan {
  constructor(
    readonly name: string,
    readonly price: Money,
    readonly interval: BillingInterval,
    readonly features: ReadonlyArray<PlanFeature>
  ) {}
}

class PlanFeature {
  constructor(
    readonly name: string,
    readonly description: string,
    readonly limit?: number
  ) {}
}
```

#### Domain Services
```typescript
class FinancialDomainService {
  async createSubscription(command: CreateSubscriptionCommand): Promise<Subscription>;
  async processPayment(command: ProcessPaymentCommand): Promise<Payment>;
  async recordRevenue(record: RevenueRecord): Promise<void>;
}

class ComplianceService {
  async validateTransaction(transaction: Transaction): Promise<ComplianceResult>;
  async generateAuditReport(period: AuditPeriod): Promise<AuditReport>;
}
```

#### Services to Consolidate
- `subscription_service.dart` → `FinancialDomainService`

---

## Clean Architecture Layers

### 1. Presentation Layer
**Responsibility:** UI components, API controllers, and user interaction handling

```
Frontend (Flutter)              Backend (FastAPI)
├── Screens/                   ├── Controllers/
│   ├── TradingScreen          │   ├── TradingController
│   ├── GamificationScreen     │   ├── GamificationController
│   └── SocialScreen           │   └── SocialController
├── Widgets/                   ├── DTOs/
│   ├── TradingWidget          │   ├── TradeRequest
│   └── LeaderboardWidget      │   └── TradeResponse
└── Navigation/                └── Middleware/
    └── AppRouter                  └── AuthMiddleware
```

### 2. Application Layer
**Responsibility:** Use cases, command handlers, and application-specific business rules

```
├── UseCases/
│   ├── ExecuteTradeUseCase
│   ├── AwardXPUseCase
│   ├── UpdateLeaderboardUseCase
│   └── MintNFTUseCase
├── Commands/
│   ├── ExecuteTradeCommand
│   ├── CreateClanCommand
│   └── RegisterUserCommand
└── Queries/
    ├── GetPortfolioQuery
    ├── GetLeaderboardQuery
    └── GetUserProfileQuery
```

### 3. Domain Layer
**Responsibility:** Core business logic, entities, value objects, and domain services

```
├── Entities/
│   ├── Trade, Portfolio, Position
│   ├── User, Achievement, Streak
│   ├── Clan, Challenge, Leaderboard
│   └── NFTItem, Collection, Listing
├── ValueObjects/
│   ├── Money, Price, XP, Level
│   ├── Email, Username
│   └── NFTMetadata, Attributes
├── DomainServices/
│   ├── TradingDomainService
│   ├── GamificationDomainService
│   └── SocialDomainService
└── Events/
    ├── TradeExecutedEvent
    ├── XPAwardedEvent
    └── AchievementUnlockedEvent
```

### 4. Infrastructure Layer
**Responsibility:** External integrations, database access, and technical concerns

```
├── Repositories/
│   ├── SqlTradeRepository
│   ├── SqlUserRepository
│   └── SqlNFTRepository
├── ExternalServices/
│   ├── ExtendedExchangeClient
│   ├── StarknetClient
│   └── PaymentGateway
├── EventBus/
│   ├── RedisEventBus
│   └── EventHandlers
└── Configuration/
    ├── DatabaseConfig
    └── ApiConfig
```

---

## Migration Plan

### Phase 1.1: Domain Extraction (Weeks 1-2)
1. **Identify Domain Boundaries:** Map existing services to domains
2. **Extract Entities:** Create domain entities from existing models
3. **Define Value Objects:** Identify and create value objects
4. **Create Domain Services:** Consolidate related services

### Phase 1.2: Service Consolidation (Weeks 3-4)
1. **Backend Services:** Merge 55+ services into 6 domain services
2. **Frontend Services:** Consolidate Flutter services into domain-specific services
3. **Remove Duplications:** Eliminate redundant functionality
4. **Update Dependencies:** Ensure clean dependency flow

### Phase 1.3: Clean Architecture Implementation (Weeks 5-6)
1. **Layer Separation:** Enforce dependency inversion principle
2. **Use Case Implementation:** Create application-specific business rules
3. **Repository Pattern:** Abstract data access with interfaces
4. **Dependency Injection:** Configure IoC container

### Phase 1.4: Testing and Validation (Weeks 7-8)
1. **Unit Tests:** Test domain logic in isolation
2. **Integration Tests:** Verify layer interactions
3. **Domain Tests:** Property-based testing for business rules
4. **Performance Testing:** Ensure no degradation

---

## Success Metrics

### Service Consolidation
- **Before:** 55+ backend services, 50+ frontend services
- **After:** 6 domain services (backend), 6 domain services (frontend)
- **Target:** 90%+ reduction in service count

### Code Quality
- **Domain Logic Coverage:** 95%+ test coverage for domain layer
- **Cyclomatic Complexity:** <10 for all domain methods
- **Code Duplication:** <5% across domain services

### Development Velocity
- **Feature Development:** 30% faster due to clear boundaries
- **Bug Resolution:** 40% faster due to better testing
- **Onboarding Time:** 50% faster for new developers

### Business Impact
- **Trading Accuracy:** 99.9%+ for all financial calculations
- **Gamification Engagement:** Clear XP/achievement logic
- **Social Features:** Scalable clan and leaderboard systems

---

## Conclusion

This Phase 1 domain structure provides the foundation for AstraTrade's architectural evolution. By clearly separating concerns into six bounded contexts with clean architecture layers, the system becomes more maintainable, testable, and scalable.

The consolidation from 100+ services to 12 domain services (6 backend, 6 frontend) dramatically reduces complexity while maintaining all functionality. This structure prepares the codebase for Phase 2's event-driven extensions and Phase 3's microservices decomposition.

---

**Document Version:** 1.0  
**Last Updated:** July 31, 2025  
**Next Review:** August 15, 2025