"""
AstraTrade Domain Layer - Phase 1 Implementation

This package implements the Domain-Driven Design architecture defined in ADR-001.
It consolidates 105+ services into 6 bounded contexts with clean architecture layers.

Phase 1 Implementation follows MIGRATION_STRATEGY_SUCCESS_METRICS.md:
- Backend: 55+ services → 6 domain services  
- Frontend: 50+ services → 6 domain services
- Target: 89% service reduction while maintaining functionality

Domains (Bounded Contexts):
- trading: Core trading operations, risk management, portfolio tracking
- gamification: XP system, achievements, progression mechanics  
- social: Clans, leaderboards, challenges, friend systems
- nft: Marketplace, minting, collections, reward distribution
- user: Authentication, profiles, preferences, onboarding
- financial: Payments, subscriptions, revenue tracking, compliance

Architecture Layers (per ADR-001):
┌─────────────────────────────────────┐
│           Presentation Layer        │ <- Screens, Controllers, APIs
├─────────────────────────────────────┤
│          Application Layer          │ <- Use Cases, Command Handlers  
├─────────────────────────────────────┤
│           Domain Layer              │ <- Entities, Value Objects, Rules
├─────────────────────────────────────┤
│        Infrastructure Layer         │ <- Database, APIs, External Services
└─────────────────────────────────────┘
"""