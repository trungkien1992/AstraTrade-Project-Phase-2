# Execution Ticket: Implement Standalone FeeSplitter Contract

**ID:** ET-20250806-001
**Status:** OPEN
**Author:** Gemini AI
**Date:** August 6, 2025

---

## 1. Summary

This ticket outlines the plan to architect and implement a standalone `FeeSplitter` smart contract. This contract will manage the distribution of protocol revenue from the `AstraTradeExchange` to various on-chain beneficiaries, starting with the `AstraTradePaymaster` and the protocol treasury. This approach replaces the initial idea of directly coupling the Exchange and Paymaster contracts in favor of a more secure, modular, and flexible design.

## 2. Problem Statement

Directly integrating fee distribution logic into the `AstraTradeExchange` contract presents significant long-term risks:

*   **Security Risk:** It increases the complexity and attack surface of the most critical contract in the protocol. A bug in the fee logic could jeopardize the entire exchange.
*   **Rigidity:** Any future changes to fee percentages or the addition of new beneficiaries would require a high-risk upgrade of the core `Exchange` contract.
*   **Auditability:** It complicates the auditing process by mixing core exchange logic with financial routing logic, making it harder and more expensive to verify correctness.

## 3. Proposed Solution: The `FeeSplitter` Architecture

To address these risks, we will adopt a modular, "separation of concerns" architecture. This design is superior in security, flexibility, and auditability.

1.  **`AstraTradeExchange`:** This contract's role will be minimal. It will compute and collect trading fees, accumulating them in an internal balance. It will have a single, permissionless `sweep_fees()` function to transfer these accumulated funds to the `FeeSplitter`.
2.  **`FeeSplitter` (New Contract):** This new, standalone contract will be the central hub for fee management. Its sole responsibility is to receive funds from the `Exchange` and distribute them to a governable list of beneficiaries according to predefined shares.
3.  **`AstraTradePaymaster`:** This contract will be a beneficiary of the `FeeSplitter`. Its funding logic will be simplified to only accept funds from the `FeeSplitter`'s address.

This design isolates risks, enhances security, and provides the flexibility to evolve the protocol's economic model without touching the core trading engine.

## 4. Implementation Plan

### Phase 1: Create `FeeSplitter.cairo`
- **Action:** Create a new file: `src/contracts/fee_splitter.cairo`.
- **Logic:**
    - Implement a beneficiary registry (mapping address to percentage share).
    - Implement a function to receive funds from the `Exchange`.
    - Implement a public `distribute_fees()` function that can be called permissionlessly.
    - Add timelocked governance functions for managing beneficiaries and their respective shares.

### Phase 2: Integrate Existing Contracts
- **`AstraTradeExchange.cairo`:**
    - Add a `fee_splitter_address` storage variable.
    - Modify fee collection logic to accumulate fees internally instead of transferring them immediately.
    - Add a public `sweep_fees()` function to push the accumulated funds to the `FeeSplitter`.
- **`AstraTradePaymaster.cairo`:**
    - Modify the funding logic to only accept transfers from the `FeeSplitter` contract's address.

### Phase 3: Update Off-Chain Components & Testing
- **Deployment Scripts:** Update all relevant deployment scripts to include the new `FeeSplitter` contract and correctly link the contract addresses during deployment.
- **Testing:**
    - Write comprehensive unit tests for the `FeeSplitter` in isolation.
    - Update the integration test suite to verify the full `Exchange -> FeeSplitter -> Paymaster` flow.
    - Add economic simulation tests to model behavior under various market conditions (e.g., high/low volume, gas spikes).

## 5. Success Criteria

- All new and existing smart contracts compile successfully.
- All unit and integration tests pass, demonstrating the correct and secure flow of funds.
- On the Sepolia testnet, fees generated from trades on the `Exchange` are successfully swept to the `FeeSplitter` and subsequently distributed to the `Paymaster` and treasury addresses according to the configured shares.
- All governance functions for managing the `FeeSplitter` are proven to be secure and functional via testing.
