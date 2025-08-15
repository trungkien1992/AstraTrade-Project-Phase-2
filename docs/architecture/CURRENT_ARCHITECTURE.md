# AstraTrade: Current Architecture & Infrastructure Bridge

**Document Status:** Active | **Last Updated:** 2025-08-06

## 1. Overview

This document provides a consolidated overview of AstraTrade's current system architecture and outlines the immediate 8-week "Infrastructure Bridge" strategy. It serves as the single source of truth, superseding earlier plans like the Go-rewrite detailed in `evolution_plan.md`.

The core architectural strategy is to leverage the significant progress made in the Python-based domain implementations by deploying them as microservices, rather than undertaking a high-risk, full rewrite. This approach, detailed in **ADR-006** and **ADR-007**, accelerates time-to-market for key features like real-time capabilities and improved scalability.

## 2. Current Architectural State

The architecture is a hybrid model, transitioning from a well-structured monolith to a distributed system.

### 2.1. Backend: Python-First Domain-Driven Design (DDD)

The backend is substantially complete, with 5 of the 6 business domains implemented in Python using high-quality DDD patterns.

*   **Primary Language:** Python
*   **Architectural Pattern:** Domain-Driven Design (DDD) with Clean Architecture layers.
*   **Implementation Status (83% Complete):**
    *   ✅ **Trading Domain:** Complete
    *   ✅ **Gamification Domain:** Complete
    *   ✅ **User Domain:** Complete
    *   ✅ **Financial Domain:** Complete (with Functional Programming patterns)
    *   ✅ **NFT Domain:** Complete
    *   ⏳ **Social Domain:** In Progress (Final domain to be completed)

### 2.2. Frontend: Flutter

The frontend is a mobile-first Flutter application, described as feature-complete and fully delivered. It provides a gamified user experience and integrates with both the backend services and Starknet smart contracts.

### 2.3. Blockchain: Cairo Smart Contracts

The on-chain components are implemented as Cairo smart contracts on the Starknet L2 network. These contracts for handling the exchange, vault, and paymaster functionalities are deployed and operational.

## 3. The "Infrastructure Bridge" Strategy

This is an 8-week plan to evolve the current Python domains into a microservices architecture.

### 3.1. Architectural Vision

The target architecture is a set of containerized Python services communicating via an event bus, with the flexibility to add specialized Go services for performance bottlenecks.

```mermaid
graph TD
    subgraph Frontend
        A[Flutter Mobile App]
    end

    subgraph Backend
        B[API Gateway: FastAPI] --> C{Event Bus (Redis Streams)}

        subgraph Python Microservices
            D1[Trading Service]
            D2[Gamification Service]
            D3[User Service]
            D4[Financial Service]
            D5[NFT Service]
            D6[Social Service]
        end

        subgraph Specialized Services (Future)
            G1[Go: Real-time Leaderboards]
            G2[Go: High-Frequency Trading]
        end

        D1 -- Publishes/Subscribes --> C
        D2 -- Publishes/Subscribes --> C
        D3 -- Publishes/Subscribes --> C
        D4 -- Publishes/Subscribes --> C
        D5 -- Publishes/Subscribes --> C
        D6 -- Publishes/Subscribes --> C
        G1 -- Subscribes --> C
        G2 -- Subscribes --> C
    end

    subgraph Blockchain
        E[Starknet Smart Contracts]
    end

    A --> B
    B --> E
```

### 3.2. 8-Week Implementation Plan

**Weeks 1-2: Domain Completion & Event Design**
-   Complete the `Social` domain reorganization in Python.
-   Standardize event schemas (e.g., Avro/Protobuf) for cross-domain communication.
-   Prepare Python domains for containerization (Docker).

**Weeks 3-4: Event Bus & Basic Infrastructure**
-   Deploy Redis Streams as the event bus.
-   Implement event publishing from the Python domains.
-   Set up initial monitoring and logging infrastructure.
-   Configure the FastAPI API Gateway to route to the new services.

**Weeks 5-6: Microservices Deployment**
-   Deploy each Python domain as an independent containerized service (e.g., on Kubernetes).
-   Implement service discovery and health checks.
-   Enable real-time, event-driven communication between services.

**Weeks 7-8: Performance Optimization & Go Integration**
-   Conduct load testing to identify performance bottlenecks.
-   Implement CQRS read models for analytics and leaderboards.
-   Deploy selective Go services for high-throughput operations if necessary.

## 4. Deprecation of Previous Plans

The "Go-rewrite" strategy detailed in `evolution_plan.md` is officially **DEPRECATED**. The "Infrastructure Bridge" plan (ADR-007) provides a more pragmatic, lower-risk path to achieving the project's scalability and real-time feature goals by building on the existing, proven Python codebase.

## 5. Key Benefits of the Current Strategy

*   **Reduced Risk:** Avoids a "big bang" rewrite, preserving working business logic.
*   **Accelerated Timeline:** Delivers microservices benefits and real-time features in 8 weeks vs. the 18+ weeks of a full rewrite.
*   **Leverages Expertise:** Capitalizes on the team's strong Python skills.
*   **Immediate Value:** The infrastructure can be deployed now, supporting the already-completed domains.
