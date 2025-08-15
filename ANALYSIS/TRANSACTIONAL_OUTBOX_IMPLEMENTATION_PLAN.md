# Roadmap: Implementing the Transactional Outbox Pattern

**Date:** 2025-08-03
**Status:** Proposed
**Related Document:** `ARCHITECTURAL_RISK_ANALYSIS.md`

---

### **Epic: [ARC-001] Guarantee Critical Event Delivery via Transactional Outbox**

**Description:** Refactor the `trading-service` to implement the Transactional Outbox pattern. This will ensure that all critical events related to a trade are guaranteed to be published at least once, eliminating the risk of data inconsistency between the trading ledger and downstream financial systems.

**Goal:** Achieve reliable eventual consistency for the entire trade lifecycle, making the system more robust and auditable.

---

### Stories / Tasks

#### **1. Story: [ARC-002] Create the `event_outbox` Table**

-   **Status:** To Do
-   **Priority:** Blocker
-   **Description:** A new database table, `event_outbox`, is required to persist events atomically alongside business transactions. A database migration script must be created to introduce this table into the schema.
-   **Technical Details:**
    -   Create a new Alembic migration script.
    -   The `event_outbox` table schema should include:
        -   `id` (Primary Key, UUID or BigInt)
        -   `aggregate_id` (e.g., `trade_id`, for grouping events)
        -   `event_type` (String, e.g., "astra.trading.trade_executed.v1")
        -   `payload` (JSON/JSONB, the event data)
        -   `status` (String, e.g., `PENDING`, `PUBLISHED`, `FAILED`)
        -   `created_at` (Timestamp)
        -   `updated_at` (Timestamp)
-   **Acceptance Criteria:**
    -   The migration script successfully creates the `event_outbox` table in the database.
    -   The table schema is indexed appropriately (e.g., on `status` and `created_at`).

#### **2. Story: [ARC-003] Integrate Outbox Write into Trading Logic**

-   **Status:** To Do
-   **Priority:** High
-   **Depends On:** [ARC-002]
-   **Description:** The core `execute_trade` logic in the `trading-service` must be modified to write to the `event_outbox` table instead of publishing directly to the event bus.
-   **Technical Details:**
    -   In `services/trading/main.py`, refactor the `execute_trade` function.
    -   Wrap the database operations (creating the trade, updating positions) in a single, atomic transaction.
    -   Within this same transaction, insert the `TradeExecuted` and `PositionUpdated` events as records into the `event_outbox` table with a `status` of `PENDING`.
    -   Remove the direct calls to `event_bus.publish_event()` from this function.
-   **Acceptance Criteria:**
    -   When a trade is executed, a trade record and its corresponding event records are created atomically in the database.
    -   If any part of the transaction fails, the trade and the outbox events are all rolled back.
    -   No events are published directly to Redis from the trade execution endpoint.

#### **3. Story: [ARC-004] Implement the Message Relay Service**

-   **Status:** To Do
-   **Priority:** High
-   **Depends On:** [ARC-003]
-   **Description:** Create a background process or service responsible for relaying events from the `event_outbox` table to the Redis Event Bus.
-   **Technical Details:**
    -   This can be implemented as a background task (e.g., using `asyncio.create_task`) within the `trading-service` or as a separate, standalone process.
    -   The relay will periodically poll the `event_outbox` table for records with `status = 'PENDING'`.
    -   For each pending event, the relay will:
        1.  Publish the event to the appropriate Redis Stream using the existing `EventBus`.
        2.  Upon successful publication, update the event's record in the `event_outbox` table to `status = 'PUBLISHED'`. This update must be handled carefully to prevent race conditions.
-   **Acceptance Criteria:**
    -   The relay reliably reads pending events from the outbox.
    -   Events are successfully published to Redis.
    -   The status of published events is correctly updated in the database.
    -   The relay is resilient and can handle temporary unavailability of Redis.

#### **4. Story: [ARC-005] Add Monitoring and Alerting for the Outbox**

-   **Status:** To Do
-   **Priority:** Medium
-   **Depends On:** [ARC-004]
-   **Description:** To ensure the health and performance of the new outbox system, monitoring and alerting must be implemented.
-   **Technical Details:**
    -   Expose Prometheus metrics from the `trading-service` or relay process, including:
        -   `outbox_pending_events_total` (a gauge for the current number of pending events).
        -   `outbox_oldest_pending_event_age_seconds` (the age of the oldest unprocessed event).
        -   `outbox_events_published_total` (a counter for successfully relayed events).
        -   `outbox_publish_errors_total` (a counter for errors).
    -   Configure alerts in Grafana/Alertmanager to trigger if:
        -   The number of pending events exceeds a defined threshold.
        -   The age of the oldest event exceeds a defined threshold (e.g., 5 minutes).
-   **Acceptance Criteria:**
    -   Key metrics for the outbox system are visible on a monitoring dashboard.
    -   Alerts are configured to notify the on-call team of potential issues with event delivery.

#### **5. Story: [ARC-006] Create Integration Tests for the Outbox Workflow**

-   **Status:** To Do
-   **Priority:** High
-   **Depends On:** [ARC-004]
-   **Description:** Develop end-to-end integration tests to validate the correctness and resilience of the transactional outbox implementation.
-   **Technical Details:**
    -   Create a new test suite that covers the full lifecycle of an event.
    -   **Test Case 1 (Happy Path):**
        -   Trigger the `execute_trade` endpoint.
        -   Assert that the trade and a `PENDING` outbox event are in the database.
        -   Assert that the message relay publishes the event to Redis and updates its status to `PUBLISHED`.
    -   **Test Case 2 (Failure Scenario):**
        -   Simulate a Redis connection failure.
        -   Assert that the relay fails to publish the event and that its status remains `PENDING`.
        -   Restore the Redis connection and assert that the relay eventually succeeds.
-   **Acceptance Criteria:**
    -   The integration tests are added to the CI/CD pipeline.
    -   The tests successfully validate both the success and failure modes of the outbox system.
