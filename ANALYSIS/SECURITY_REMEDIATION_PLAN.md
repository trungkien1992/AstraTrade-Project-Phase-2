# Security Remediation Plan: Secure Trade Execution

**Date:** 2025-08-03
**Status:** Ready for Development
**Related Document:** `SECURITY_VULNERABILITY_REPORT.md`

---

### Overview

This document outlines the engineering tasks required to remediate the critical authentication and authorization vulnerabilities in the AstraTrade backend. The work is broken down into a single Epic with five dependent stories. All tasks must be completed to secure the platform.

---

### **Epic: [SEC-001] Secure the End-to-End Trade Execution Workflow**

**Description:** Implement a zero-trust security model for the trade execution process, from the API Gateway to all downstream services. This involves replacing mock authentication with robust JWT validation, enforcing server-side identity, and adding authorization controls.

**Goal:** Ensure that only authenticated and authorized users can execute trades for themselves, completely eliminating the identity spoofing vulnerability.

---

### Stories / Tasks

#### **1. Story: [SEC-002] Implement JWT Validation in API Gateway**

-   **Status:** To Do
-   **Priority:** Blocker
-   **Description:** The current mock authentication in the API Gateway must be replaced with a production-ready JWT validation mechanism. The gateway must be able to cryptographically verify tokens and extract user identity from their claims.
-   **Technical Details:**
    -   Integrate a JWT library (e.g., `python-jose`) into `api_gateway.py`.
    -   Update the `get_current_user` dependency to perform full token validation (signature, expiration, issuer).
    -   Configure the validation to use a secure, shared secret or public key.
    -   The function should extract the `user_id` and other relevant claims from the token payload.
-   **Acceptance Criteria:**
    -   Requests with missing, invalid, or expired tokens are rejected with a `401 Unauthorized` error.
    -   Requests with a valid JWT proceed, and the `current_user` object contains the verified `user_id` from the token's claims.

#### **2. Story: [SEC-003] Enforce Server-Side Identity at the Gateway**

-   **Status:** To Do
-   **Priority:** High
-   **Depends On:** [SEC-002]
-   **Description:** The API Gateway must be the single source of truth for user identity. It must ignore any `user_id` provided by the client in the request body and use the validated identity from the JWT.
-   **Technical Details:**
    -   In the `execute_trade` endpoint of `api_gateway.py`, modify the logic to ignore the `user_id` from the `TradeRequest` payload.
    -   The `user_id` from the `current_user` object (derived from the JWT) must be used when constructing the data packet to be forwarded to the `trading-service`.
-   **Acceptance Criteria:**
    -   A trade request sent with a `user_id` in the body that does not match the `user_id` in the JWT is still processed for the user in the JWT.
    -   The `trading-service` only ever receives the `user_id` that was validated from the token.

#### **3. Story: [SEC-004] Securely Propagate Identity to Downstream Services**

-   **Status:** To Do
-   **Priority:** High
-   **Depends On:** [SEC-002]
-   **Description:** The validated user identity must be securely passed from the API Gateway to all internal microservices. This prevents downstream services from needing to re-authenticate the user.
-   **Technical Details:**
    -   Modify the `make_service_request` function in `api_gateway.py`.
    -   Add a new HTTP header, `X-Authenticated-User-ID`, to all outgoing requests to downstream services.
    -   The value of this header must be the validated `user_id` from the JWT.
-   **Acceptance Criteria:**
    -   All internal service-to-service requests originating from the API Gateway contain the `X-Authenticated-User-ID` header.
    -   The header is not added to requests that have not been authenticated.

#### **4. Story: [SEC-005] Implement Identity Verification in Trading Service**

-   **Status:** To Do
-   **Priority:** High
-   **Depends On:** [SEC-004]
-   **Description:** The `trading-service` must be updated to trust and use the identity provided by the gateway, removing its reliance on the insecure request payload.
-   **Technical Details:**
    -   Modify the `execute_trade` endpoint in `services/trading/main.py`.
    -   The function must extract the `user_id` from the `X-Authenticated-User-ID` header.
    -   The `user_id` from the request body must be ignored and removed from the business logic.
    -   If the `X-Authenticated-User-ID` header is missing, the service must return a `403 Forbidden` or `500 Internal Server Error`, as this indicates a security misconfiguration.
-   **Acceptance Criteria:**
    -   The `trading-service` successfully executes trades using the `user_id` from the secure header.
    -   The service rejects any request that is missing the identity header.

#### **5. Story: [SEC-006] Implement Basic Authorization Controls**

-   **Status:** To Do
-   **Priority:** Medium
-   **Depends On:** [SEC-005]
-   **Description:** Add a defense-in-depth authorization check to ensure a user can only perform actions on their own resources.
-   **Technical Details:**
    -   In the `trading-service`, add a check to verify that the `user_id` from the `X-Authenticated-User-ID` header matches the owner of the account/resources being acted upon.
    -   This serves as a secondary guardrail against misconfigurations.
-   **Acceptance Criteria:**
    -   An explicit authorization check is present in the `execute_trade` function.
    -   The system is prepared for future, more complex authorization rules (e.g., admin roles).
