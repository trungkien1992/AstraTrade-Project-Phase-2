# AstraTrade: Backend Engineering Guide to User & Auth Architecture

**Audience:** Senior Backend Engineers

**Purpose:** This document provides the definitive strategic and architectural rationale for the User, Authentication, and Permissions models. All future development must align with these principles to ensure scalability, security, and rapid iteration.

---

## Section 1: Core Architectural Principles

1.  **Hybrid Authentication for Mass Adoption:** We combine Web3-native social logins (via Web3Auth) with a traditional, first-party credential system. This allows for a seamless, low-friction onboarding experience for the mass market while providing the security, resilience, and choice required for a financial-grade platform.

2.  **Centralized Auth Service as the Gatekeeper:** All authentication and authorization logic is consolidated into a dedicated `Auth Service`. This service is the single source of truth for identity, sessions, and permissions. Downstream services (Trading, Financial, etc.) are simplified and secured by offloading all auth decisions to this central authority.

3.  **Two-Vector Entitlement System:** Our permissions model is a hybrid of **Attribute-Based Access Control (ABAC)** and lightweight **Role-Based Access Control (RBAC)**. It is built on two primary vectors:
    *   **Verification Vector (Compliance):** Governs access to real-money features based on KYC status.
    *   **Subscription Vector (Commercial):** Governs access to premium features and usage quotas.

4.  **Data Model Designed for Velocity:** The data model is intentionally designed to minimize schema migrations and allow for rapid feature development. This is achieved through flexible structures like JSONB for user preferences, allowing the frontend and product teams to experiment with new features without requiring backend changes.

---

## Section 2: Implementation Directives & Rationale

### **On Authentication Flow:**

*   **Primary Onboarding (Web3Auth):** The default user journey begins with Web3Auth for social login. This is our primary mechanism for acquiring and activating users at scale.
    *   **Implementation Implication:** The `Auth Service` must be tightly integrated with the Web3Auth SDK. It will be responsible for validating the tokens from Web3Auth and creating a corresponding AstraTrade user profile.

*   **First-Party Credentials (Password/Email):** The `SecurityCredentials` value object, containing `hashed_password` and `password_salt`, serves as a vital fallback and alternative authentication path.
    *   **Implementation Implication:** The `Auth Service` must support a full password-based authentication flow (registration, login, password reset). Use a memory-hard algorithm like **Argon2id** for hashing passwords.

*   **Platform-Controlled 2FA:** We will implement our own 2FA logic using the `two_factor_secret` in `SecurityCredentials`. This is non-negotiable for a financial platform.
    *   **Implementation Implication:** The `Auth Service` must handle TOTP (Time-based One-Time Password) generation, validation, and recovery code management. It must trigger "step-up" authentication for sensitive operations (e.g., withdrawals, API key creation) regardless of the initial login method.

### **On the User Data Model & Permissions:**

*   **`user_id` (Internal vs. External):**
    *   **Directive:** The integer `user_id` is the internal primary key for the database and **must never** be exposed in public APIs. All external-facing resources should use a separate, non-sequential public identifier (e.g., a UUID).
    *   **Rationale:** This decouples our internal database schema from our public API contract, improving security and allowing us to optimize database performance without affecting external clients.

*   **`verification_tier` (The Compliance Vector):**
    *   **Directive:** This enum is the backbone of the user lifecycle and the primary compliance gate. The `can_real_trade` permission is **deterministically** granted only when a user reaches `IDENTITY_VERIFIED`.
    *   **Rationale:** This creates an explicit, auditable link between KYC completion and access to financial features, eliminating manual or discretionary errors. It is the single source of truth for compliance.

*   **`permissions` (The Computed Entitlement Set):**
    *   **Directive:** This object represents the *computed result* of all access control policies (Verification, Subscription, Status, etc.). Downstream services **must** check the permissions object (e.g., `user.permissions.can_real_trade`) rather than interpreting the raw attributes themselves.
    *   **Rationale:** This abstracts policy complexity. The `Auth Service` or `User Domain` acts as the Policy Decision Point (PDP), and the `permissions` object is the resulting policy decision. This decouples services from policy logic, allowing policies to evolve without requiring changes to every downstream service.

*   **`preferences` (Flexible Key-Value Store):**
    *   **Directive:** This field must be implemented using a flexible data type like JSONB. It is to be used for non-critical, UX-related settings.
    *   **Rationale:** This design choice is critical for development velocity. It allows the frontend and product teams to add new user-configurable settings without requiring backend schema changes, which are slow and costly.

### **On the `Auth Service` & Enforcement:**

*   **Token Issuance:**
    *   **Directive:** The `Auth Service` will issue short-lived JWT access tokens and long-lived, rotating refresh tokens. Access tokens must contain essential, non-sensitive claims like the public `user_id` (UUID), `verification_tier`, `subscription_tier`, and a permissions hash/version.
    *   **Rationale:** This is a standard, secure pattern for microservices authentication. It allows downstream services to validate tokens and make basic authorization decisions locally and quickly.

*   **Fine-Grained Authorization & Enforcement:**
    *   **Directive:** For complex or highly sensitive operations, downstream services should make a real-time call to the `Auth Service`'s policy decision point (PDP) API to get a definitive allow/deny answer. For simple checks, validating the token is sufficient.
    *   **Example Enforcement Flow (Trading Service):**
        1.  Validate the JWT.
        2.  Check if `can_real_trade` is true within the token's claims or from the `permissions` object.
        3.  Enforce any rate limits or quotas associated with the user's subscription tier.
        4.  If all checks pass, execute the trade.
    *   **Rationale:** This layered approach balances performance (local token validation) with security and consistency (centralized policy decisions for critical operations).