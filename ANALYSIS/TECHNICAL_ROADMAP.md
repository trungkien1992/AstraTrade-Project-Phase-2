# AstraTrade Technical Roadmap

**Document Status:** Active | **Last Updated:** 2025-08-06

This roadmap outlines the development priorities for AstraTrade, building on the current architectural foundation. It is structured to ensure a stable transition to microservices before new features are implemented.

---

### Phase 1: The Infrastructure Bridge (Estimated: 8 Weeks)

**Goal:** Successfully transition the existing Python domains into a resilient, event-driven microservices architecture.

1.  **Complete the Social Domain:** Finalize the last remaining domain implementation in Python, ensuring it adheres to the established DDD patterns.
2.  **Deploy Core Infrastructure:**
    *   Deploy Redis Streams as the central event bus.
    *   Containerize all 6 Python domains using Docker.
    *   Configure the FastAPI-based API Gateway to route traffic to the services.
3.  **Activate Microservices:**
    *   Deploy the containerized services to a staging environment (e.g., on Kubernetes).
    *   Implement service discovery and health checks.
    *   Enable event publishing and consumption between all services via the event bus.
4.  **Initial Observability & Validation:**
    *   Implement structured logging and basic metrics for all new services.
    *   Conduct load testing to validate performance and identify immediate bottlenecks.

---

### Phase 2: Hardening and Optimization (Estimated: 4 Weeks)

**Goal:** Stabilize the new architecture, address known risks, and pay down technical debt before adding new features.

1.  **Enhance Observability:** Implement distributed tracing to provide a clear view of requests as they flow through the microservices architecture.
2.  **Prioritize Architectural Risks:** Review the `ARCHITECTURAL_RISK_ANALYSIS.md` and create actionable tickets to mitigate the highest-priority risks.
3.  **Address Technical Debt:** Begin tackling the items identified in `TECHNICAL_DEBT_ANALYSIS.md`, focusing on areas that impact the new microservices.
4.  **Execute Security Remediation:** Implement the fixes outlined in the `SECURITY_REMEDIATION_PLAN.md`.

---

### Phase 3: New Feature Development (Ongoing)

**Goal:** Leverage the new, stable architecture to build and deploy high-value features.

1.  **Implement Transactional Outbox Pattern:** Roll out the `TRANSACTIONAL_OUTBOX_IMPLEMENTATION_PLAN.md`. This will increase the reliability of event publishing from the new microservices.
2.  **Implement Fee Splitter:** Develop and deploy the `EXECUTION_TICKET_FEE_SPLITTER_IMPLEMENTATION.md`.
3.  **Evolve Smart Contracts:** Begin implementing the advanced DeFi features (staking, lending) outlined as the next evolution for the Cairo contracts in `ARCHITECTURAL_DECISION_RECORDS.md` (ADR-005).
