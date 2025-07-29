# AstraTrade Smart Contracts Documentation

## Overview

This document provides documentation for the AstraTrade smart contracts implemented in Cairo for the Starknet blockchain. The contracts have been enhanced with basic functionality and now compile successfully with Scarb 2.8.0.

## Contract Structure

The AstraTrade project includes the following smart contracts:

1. **Paymaster Contract** - Handles gasless transactions for users with enhanced functionality
2. **Vault Contract** - Manages user assets and balances with enhanced functionality
3. **Exchange Contract** - Handles trading operations with basic functionality

## Paymaster Contract

### Purpose
The Paymaster contract enables gasless transactions for AstraTrade users, providing a seamless user experience by covering transaction fees.

### Key Features
- Owner management
- Pause/unpause functionality
- Event emission for monitoring
- Dummy value storage for testing
- Transaction count tracking
- Total gas sponsored tracking

### Functions
- `get_dummy()` - Returns a dummy value for testing
- `test_emit()` - Emits a test event with user address and value
- `get_owner()` - Returns the contract owner
- `is_paused()` - Returns whether the contract is paused
- `get_transaction_count()` - Returns the number of sponsored transactions
- `get_total_gas_sponsored()` - Returns the total gas sponsored
- `sponsor_transaction()` - Sponsors a transaction (stub implementation)
- `transfer_ownership()` - Transfers ownership to a new address

### Events
- `TestEvent` - Emitted by the `test_emit` function

## Vault Contract

### Purpose
The Vault contract manages user assets and balances within the AstraTrade ecosystem.

### Key Features
- Balance tracking (stub implementation)
- Deposit/withdraw functions (stub implementation)
- Owner controls
- Pause/unpause functionality
- Total value locked tracking

### Functions
- `get_owner()` - Returns the contract owner
- `is_paused()` - Returns whether the contract is paused
- `get_balance()` - Returns a user's token balance
- `get_total_value_locked()` - Returns the total value locked in the vault
- `deposit()` - Deposits tokens into the vault
- `withdraw()` - Withdraws tokens from the vault
- `transfer_ownership()` - Transfers ownership to a new address

## Exchange Contract

### Purpose
The Exchange contract handles trading operations within the AstraTrade platform.

### Key Features
- Order placement functionality (stub implementation)
- Deposit/withdraw functions (stub implementation)
- Owner controls
- Pause/unpause functionality

### Functions
- `get_owner()` - Returns the contract owner
- `is_paused()` - Returns whether the contract is paused
- `get_balance()` - Returns a user's token balance
- `place_order()` - Places a trading order
- `cancel_order()` - Cancels a trading order
- `deposit()` - Deposits tokens
- `withdraw()` - Withdraws tokens

### Enums
- `OrderSide` - Buy or Sell
- `OrderType` - Market or Limit

## Compilation

All contracts compile successfully with Scarb 2.8.0:

```bash
cd apps/contracts
scarb build
```

## Testing

To verify contract compilation:

```bash
cd /Users/admin/AstraTrade-Project
python3 scripts/test_contracts_simple.py
```

## Current Status

The smart contracts have been enhanced with basic functionality and now compile successfully with Scarb 2.8.0. All contracts include proper error handling and event emission.

## Future Enhancements

Planned improvements for the smart contracts include:

1. Implement actual deposit/withdraw logic in the Vault contract with proper token transfers
2. Add gas sponsorship functionality in the Paymaster contract with real gas calculations
3. Implement comprehensive trading functionality in the Exchange contract with order matching
4. Add comprehensive unit tests for all contracts with full coverage
5. Perform security audit of smart contracts by a professional auditing firm
6. Implement proper token transfers using Starknet's token standards (ERC20, ERC721)
7. Add access controls and role-based permissions
8. Implement upgradeability patterns for future enhancements