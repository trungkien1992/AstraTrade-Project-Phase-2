# Execution Ticket: Tokenize XP into an On-Chain Reputation SBT

**ID:** ET-20250806-002
**Status:** OPEN
**Author:** Gemini AI
**Date:** August 6, 2025

---

## 1. Summary

This ticket proposes the evolution of the existing internal XP-based gamification system into a formal, on-chain, non-transferable reputation token, commonly known as a Soulbound Token (SBT). This change will transform user reputation from a simple, internal metric used for gas discounts into a core, composable protocol asset. This enhances long-term user retention and unlocks significant future value by making user status a verifiable and interoperable on-chain primitive.

## 2. Problem Statement & Opportunity

The current XP system within the `AstraTradePaymaster` is highly effective for driving engagement but has a critical limitation: its value is confined entirely within the AstraTrade protocol. It is an internal accounting number, invisible and inaccessible to other smart contracts or external applications. 

This presents a massive missed opportunity. By keeping reputation off-chain or in a simple storage slot, we fail to capitalize on the core tenets of Web3: composability and verifiable identity. The opportunity is to elevate this feature from a simple discount mechanism into a foundational pillar of a user's on-chain identity, creating durable, long-term value for both the user and the protocol.

## 3. Proposed Solution: The `AstraTradeReputation` SBT

We will create a dedicated smart contract for a non-transferable Reputation Token (SBT). This contract will serve as the definitive on-chain record of a user's contribution and status within the AstraTrade ecosystem.

1.  **`AstraTradeReputation` (New SBT Contract):** A new contract will be created to mint and manage these non-transferable tokens. Each user will be issued a single SBT, and the token's metadata or an associated storage mapping will track their reputation score (the current "XP").
2.  **`AstraTradePaymaster` (Modified):** The `Paymaster` will be refactored. Instead of managing XP internally, it will be granted the exclusive right to call the `AstraTradeReputation` contract to increase a user's reputation score whenever they perform actions that save gas. When determining a user's gas tier, the `Paymaster` will now read the reputation score directly from the SBT contract.
3.  **Frontend (Modified):** The user interface will be updated to query and display the user's on-chain reputation score from the SBT contract, making this a tangible and visible asset to the user.

This architecture cleanly separates the mechanism of reputation *accrual* (the `Paymaster`) from the representation of reputation *itself* (the `Reputation SBT`), making the entire system more modular and powerful.

## 4. Implementation Plan

### Phase 1: Create the `AstraTradeReputation` SBT Contract
- **Action:** Create a new file: `src/contracts/astratrade_reputation.cairo`.
- **Logic:**
    - Implement a standard non-transferable token interface.
    - Create a mapping from a user's address to their reputation score.
    - Implement a permissioned `increase_reputation` function, callable only by an authorized address (which will be the `Paymaster`).
    - Implement a public `get_reputation` view function.

### Phase 2: Refactor the `AstraTradePaymaster` Contract
- **Action:** Modify `src/contracts/paymaster.cairo`.
- **Logic:**
    - Remove the internal storage related to `total_xp_from_gas_savings`.
    - Add a storage variable for the `reputation_contract_address`.
    - In the logic where XP was previously incremented, replace it with an external call to the `AstraTradeReputation` contract's `increase_reputation` function.
    - When calculating a user's gas tier, replace the internal XP check with an external call to the `AstraTradeReputation` contract's `get_reputation` function.

### Phase 3: Update Off-Chain Components & Testing
- **Deployment Scripts:** Update deployment scripts to deploy the new `AstraTradeReputation` contract and correctly set its address in the `AstraTradePaymaster` during setup.
- **Frontend:** Update the UI components that display user level and XP to fetch data from the new `AstraTradeReputation` contract.
- **Testing:** Create new unit tests for the `Reputation` contract. Update integration tests to verify that reputation is correctly updated by the `Paymaster` and that gas tiers are correctly assigned based on the on-chain reputation score.

## 5. Success Criteria

- A user's reputation score is stored as a non-transferable, on-chain token.
- When a user saves gas via the `Paymaster`, their reputation score on the `AstraTradeReputation` contract increases accordingly.
- The user's gas tier benefits are correctly calculated based on their on-chain reputation score.
- The frontend correctly displays the user's on-chain reputation.
- The system is fully tested, secure, and deployed on the Sepolia testnet.
