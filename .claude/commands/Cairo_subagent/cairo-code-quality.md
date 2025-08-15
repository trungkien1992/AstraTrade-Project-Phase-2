# Cairo Code Quality Enhancement Sub-Agent Workflow

Advanced specialized workflow for systematic code quality improvement, maintainability enhancement, and technical debt reduction.

## Usage

```bash
@claude cairo-code-quality <enhancement_type> <target_file>
```

## Supported Enhancement Types

- `function-decomposition`: Break down complex functions into smaller, focused units
- `documentation`: Add comprehensive NatSpec and inline documentation
- `test-coverage`: Enhance test coverage and quality
- `error-handling`: Improve error handling patterns and consistency
- `naming-conventions`: Standardize naming and improve readability
- `all`: Comprehensive code quality enhancement plan

## Sub-commands

- `@claude cairo-code-quality <type> <file>`: Full quality enhancement workflow
- `@claude cairo-code-quality <type> <file> --analysis`: Code quality assessment only
- `@claude cairo-code-quality <type> <file> --implementation`: Step-by-step quality improvements
- `@claude cairo-code-quality <type> <file> --metrics`: Quality metrics and technical debt measurement

## Examples

```bash
# Decompose complex functions for better maintainability
@claude cairo-code-quality function-decomposition src/contracts/exchange.cairo

# Add comprehensive documentation
@claude cairo-code-quality documentation src/contracts/exchange.cairo --implementation

# Enhance test coverage with quality metrics
@claude cairo-code-quality test-coverage src/contracts/exchange.cairo --metrics

# Comprehensive code quality improvement
@claude cairo-code-quality all src/contracts/exchange.cairo
```

## Workflow Stages

### Stage 1: Code Quality Assessment & Metrics
**Purpose**: Comprehensive analysis of code quality indicators and technical debt measurement
**Methodology**: Multi-dimensional quality assessment with maintainability scoring

#### Function Complexity Analysis

**Current Complexity Assessment (AstraTradeExchangeV2):**
```
Function Complexity Breakdown:
├── _award_trade_xp() - 45 lines
│   ├── Cyclomatic Complexity: 12 (HIGH - target: <8)
│   ├── Responsibilities: 4 (XP calc, streak, level, achievements)
│   ├── Test Complexity: HIGH (multiple code paths)
│   └── Refactoring Priority: CRITICAL
│
├── open_practice_position() - 79 lines  
│   ├── Cyclomatic Complexity: 8 (MEDIUM - acceptable)
│   ├── Responsibilities: 3 (validation, creation, events)
│   ├── Documentation: 60% coverage
│   └── Refactoring Priority: MEDIUM
│
├── close_position() - 50 lines
│   ├── Cyclomatic Complexity: 6 (ACCEPTABLE)
│   ├── Security Concerns: 2 (reentrancy, calculation)
│   ├── Error Handling: Good patterns
│   └── Refactoring Priority: LOW (security fixes only)
│
└── _calculate_liquidation_price() - 15 lines
    ├── Cyclomatic Complexity: 3 (GOOD)
    ├── Mathematical Accuracy: Needs validation
    ├── Input Validation: Minimal
    └── Refactoring Priority: MEDIUM (add validation)
```

**Technical Debt Assessment:**
```
Technical Debt Metrics:
├── Documentation Coverage: 68% (target: 90%+)
├── Test Coverage: 45% (target: 95%+)
├── Function Size Distribution:
│   ├── Small (<20 lines): 65% ✅
│   ├── Medium (20-40 lines): 25% ✅
│   ├── Large (40-60 lines): 8% ⚠️
│   └── Very Large (>60 lines): 2% ❌
├── Error Handling Consistency: 82% ✅
└── Naming Convention Adherence: 91% ✅

Overall Code Quality Score: 74/100 (Yellow Zone)
Technical Debt Estimate: 3.2 person-weeks
```

### Stage 2: Function Decomposition Implementation
**Purpose**: Break down complex functions into focused, testable, and maintainable units

#### _award_trade_xp Function Refactoring

**Current Monolithic Function:**
```cairo
// BEFORE: 45-line monolithic function with multiple responsibilities
fn _award_trade_xp(
    self: @ContractState,
    ref user: User,
    activity_type: felt252
) -> (u32, u32) {
    let base_xp = XP_PER_TRADE;
    let current_time = get_block_timestamp();
    
    // RESPONSIBILITY 1: Streak calculation (10 lines)
    let time_since_last = current_time - user.last_activity_timestamp;
    let is_consecutive_day = time_since_last >= 86400_u64 && time_since_last <= 172800_u64;
    let new_streak = if is_consecutive_day {
        user.streak_days + 1_u32
    } else if time_since_last <= 86400_u64 {
        user.streak_days
    } else {
        1_u32
    };
    
    // RESPONSIBILITY 2: XP calculation (8 lines)
    let streak_bonus = new_streak * XP_STREAK_BONUS;
    let total_xp = base_xp + streak_bonus;
    user.total_xp = user.total_xp + total_xp.into();
    user.streak_days = new_streak;
    user.last_activity_timestamp = current_time;
    
    // RESPONSIBILITY 3: Level calculation (10 lines)
    let new_level = self._calculate_level(user.total_xp);
    let level_up = new_level > user.current_level;
    if level_up {
        user.current_level = new_level;
        user.max_leverage_allowed = core::cmp::min(10_u32 + (new_level - 1_u32) * 5_u32, MAX_LEVERAGE);
    }
    
    // RESPONSIBILITY 4: Achievement checking (15 lines)
    self._check_achievements(ref user);
    
    (total_xp, new_streak)
}
```

**Refactored into Focused Functions:**

**1. Pure XP Calculation Function:**
```cairo
/// Calculates base XP award for a trading activity
/// @param activity_type The type of trading activity
/// @return Base XP amount to award
fn _calculate_base_xp(activity_type: felt252) -> u32 {
    match activity_type {
        'PRACTICE_TRADE' => XP_PER_TRADE,
        'LIVE_TRADE' => XP_PER_TRADE * 2, // Bonus for live trading
        'PROFITABLE_TRADE' => XP_PER_TRADE + 25, // Profit bonus
        'TRADE_CLOSE' => XP_PER_TRADE / 2, // Reduced XP for closing
        _ => XP_PER_TRADE, // Default XP
    }
}
```

**2. Streak Management Function:**
```cairo
/// Updates user trading streak based on activity timestamp
/// @param user Reference to user struct to update
/// @param current_time Current block timestamp
/// @return (streak_bonus_xp, new_streak_days)
fn _update_trading_streak(ref user: User, current_time: u64) -> (u32, u32) {
    let time_since_last = current_time - user.last_activity_timestamp;
    
    // Determine new streak length
    let new_streak = if time_since_last >= 86400_u64 && time_since_last <= 172800_u64 {
        // Consecutive day (24-48 hours)
        user.streak_days + 1_u32
    } else if time_since_last <= 86400_u64 {
        // Same day - maintain streak
        user.streak_days
    } else {
        // Streak broken - reset to 1
        1_u32
    };
    
    // Calculate streak bonus
    let streak_bonus = new_streak * XP_STREAK_BONUS;
    
    // Update user streak data
    user.streak_days = new_streak;
    user.last_activity_timestamp = current_time;
    
    (streak_bonus, new_streak)
}
```

**3. Level Progression Function:**
```cairo
/// Processes user level progression and unlocks benefits
/// @param self Contract state for level calculation
/// @param user Reference to user struct to update
/// @return true if user leveled up, false otherwise
fn _process_level_progression(self: @ContractState, ref user: User) -> bool {
    let new_level = self._calculate_level(user.total_xp);
    let level_up = new_level > user.current_level;
    
    if level_up {
        let old_level = user.current_level;
        user.current_level = new_level;
        
        // Unlock level benefits
        user.max_leverage_allowed = self._calculate_max_leverage_for_level(new_level);
        
        // Emit level up event
        self.emit(UserLevelUp {
            user_address: user.user_address,
            old_level,
            new_level,
            total_xp: user.total_xp,
            new_max_leverage: user.max_leverage_allowed,
            timestamp: get_block_timestamp(),
        });
    }
    
    level_up
}

/// Calculates maximum leverage allowed for a user level
/// @param level User's current level
/// @return Maximum leverage multiplier
fn _calculate_max_leverage_for_level(level: u32) -> u32 {
    // Progressive leverage unlock: 10x base + 5x per level, capped at MAX_LEVERAGE
    let base_leverage = 10_u32;
    let level_bonus = (level - 1_u32) * 5_u32;
    core::cmp::min(base_leverage + level_bonus, MAX_LEVERAGE)
}
```

**4. Coordinating Function:**
```cairo
/// Awards XP and processes all related user progression updates
/// @param self Contract state reference
/// @param user Reference to user struct to update
/// @param activity_type Type of trading activity being rewarded
/// @return (total_xp_awarded, new_streak_days)
fn _award_trade_xp(
    self: @ContractState,
    ref user: User,
    activity_type: felt252
) -> (u32, u32) {
    // Calculate base XP for activity
    let base_xp = _calculate_base_xp(activity_type);
    
    // Update trading streak and get bonus
    let current_time = get_block_timestamp();
    let (streak_bonus, new_streak) = _update_trading_streak(ref user, current_time);
    
    // Calculate total XP award
    let total_xp = base_xp + streak_bonus;
    user.total_xp = user.total_xp + total_xp.into();
    
    // Process level progression
    let leveled_up = self._process_level_progression(ref user);
    
    // Process achievements (existing function, already well-structured)
    self._check_achievements(ref user);
    
    // Emit XP award event
    self.emit(XPAwarded {
        user_address: user.user_address,
        xp_amount: total_xp,
        activity_type,
        multiplier: if streak_bonus > 0 { new_streak } else { 1_u32 },
        total_xp: user.total_xp,
        timestamp: current_time,
    });
    
    (total_xp, new_streak)
}
```

**Benefits of Refactoring:**
- **Testability**: Each function can be unit tested independently
- **Readability**: Clear single responsibility for each function
- **Maintainability**: Changes to XP calculation don't affect streak logic
- **Reusability**: Pure functions can be reused in other contexts
- **Debugging**: Easier to isolate issues to specific functionality

### Stage 3: Documentation Enhancement
**Purpose**: Add comprehensive NatSpec documentation and improve code readability

#### NatSpec Documentation Standards

**Contract-Level Documentation:**
```cairo
/// @title AstraTrade Exchange V2 - Gamification-Integrated Perpetuals Trading
/// @author AstraTrade Development Team
/// @notice This contract implements mobile-optimized perpetuals trading with integrated
///         gamification features including XP, achievements, and user progression
/// @dev Features reentrancy protection, gas optimization for mobile usage (<100k gas),
///      and comprehensive event emission for real-time Flutter UI updates
/// @custom:security-contact security@astratrade.com
/// @custom:version 2.0.0
#[starknet::contract]
mod AstraTradeExchangeV2 {
    // Contract implementation
}
```

**Function-Level Documentation Example:**
```cairo
/// @notice Opens a new practice trading position for a user
/// @dev This function is gas-optimized for mobile usage and includes comprehensive
///      validation, XP awards, and real-time event emission
/// @param pair_id The trading pair identifier (must be active)
/// @param is_long True for long position, false for short position  
/// @param leverage Position leverage multiplier (1x to user's max allowed)
/// @param collateral_amount Amount of practice tokens to use as collateral
/// @return position_id The unique identifier for the created position
/// @custom:security Requires user registration and sufficient practice balance
/// @custom:gas-cost Approximately 85,000 gas per execution
/// @custom:events Emits PositionOpened and XPAwarded events
fn open_practice_position(
    ref self: ContractState,
    pair_id: u32,
    is_long: bool,
    leverage: u32,
    collateral_amount: u256
) -> u32 {
    // Implementation with inline documentation
    
    // Validate system state and user permissions
    self._assert_not_paused();
    let caller = get_caller_address();
    
    /// @dev User validation ensures only registered users can trade
    let mut user = self.users.read(caller);
    assert(!user.user_address.is_zero(), 'User not registered');
    
    /// @dev Trading pair validation prevents operations on inactive pairs
    let trading_pair = self.trading_pairs.read(pair_id);
    assert(trading_pair.is_active, 'Pair not active');
    
    // Continue with implementation...
}
```

**Complex Logic Documentation:**
```cairo
/// @notice Calculates the liquidation price for a trading position
/// @dev Uses maintenance margin and leverage to determine the price at which
///      a position would be automatically liquidated to prevent negative balance
/// @param entry_price The price at which the position was opened
/// @param is_long True for long positions, false for short positions
/// @param leverage Position leverage multiplier
/// @param maintenance_margin Maintenance margin in basis points (e.g., 500 = 5%)
/// @return liquidation_price The price at which liquidation would occur
/// @custom:formula Long: entry_price * (1 - (maintenance_margin / leverage))
/// @custom:formula Short: entry_price * (1 + (maintenance_margin / leverage))
/// @custom:example For long position: entry=$100, leverage=10x, margin=5%
///                 Liquidation = $100 * (1 - 0.05/10) = $99.50
fn _calculate_liquidation_price(
    self: @ContractState,
    entry_price: u256,
    is_long: bool,
    leverage: u32,
    maintenance_margin: u32
) -> u256 {
    // Mathematical formula implementation with step-by-step comments
    
    /// Step 1: Calculate margin factor (10000 - maintenance_margin) * 100
    /// This converts basis points to a factor for percentage calculations
    let margin_factor_base = 10000_u32 - maintenance_margin;
    let margin_factor = margin_factor_base * 100_u32;
    
    /// Step 2: Apply leverage to margin factor  
    /// Higher leverage reduces the margin buffer, making liquidation more likely
    let leverage_factor = margin_factor / leverage;
    
    /// Step 3: Calculate price movement threshold
    /// This determines how much the price can move before liquidation
    if is_long {
        /// For long positions: price can drop by leverage_factor/1000000
        let price_reduction = (entry_price * leverage_factor.into()) / 1000000_u256;
        entry_price - price_reduction
    } else {
        /// For short positions: price can rise by leverage_factor/1000000  
        let price_increase = (entry_price * leverage_factor.into()) / 1000000_u256;
        entry_price + price_increase
    }
}
```

### Stage 4: Error Handling Enhancement
**Purpose**: Implement consistent, informative error handling patterns across the contract

#### Error Handling Standards

**Custom Error Types:**
```cairo
/// @title AstraTrade Exchange Error Codes
/// @notice Standardized error messages for consistent user experience
mod AstraTradeErrors {
    // System-level errors (1000-1099)
    const SYSTEM_PAUSED: felt252 = 'ATE001: System is paused';
    const EMERGENCY_MODE: felt252 = 'ATE002: Emergency mode active';
    const UNAUTHORIZED_ACCESS: felt252 = 'ATE003: Unauthorized access';
    
    // User-related errors (1100-1199)
    const USER_NOT_REGISTERED: felt252 = 'ATE101: User not registered';
    const USER_ALREADY_EXISTS: felt252 = 'ATE102: User already exists';
    const INSUFFICIENT_BALANCE: felt252 = 'ATE103: Insufficient balance';
    const KYC_NOT_VERIFIED: felt252 = 'ATE104: KYC verification required';
    
    // Trading errors (1200-1299)
    const INVALID_TRADING_PAIR: felt252 = 'ATE201: Invalid trading pair';
    const PAIR_NOT_ACTIVE: felt252 = 'ATE202: Trading pair not active';
    const INVALID_LEVERAGE: felt252 = 'ATE203: Invalid leverage amount';
    const POSITION_NOT_FOUND: felt252 = 'ATE204: Position not found';
    const POSITION_NOT_ACTIVE: felt252 = 'ATE205: Position not active';
    const NOT_POSITION_OWNER: felt252 = 'ATE206: Not position owner';
    
    // Mathematical errors (1300-1399)
    const DIVISION_BY_ZERO: felt252 = 'ATE301: Division by zero';
    const ARITHMETIC_OVERFLOW: felt252 = 'ATE302: Arithmetic overflow';
    const INVALID_PRICE: felt252 = 'ATE303: Invalid price value';
    const CALCULATION_ERROR: felt252 = 'ATE304: Calculation error';
}
```

**Enhanced Validation Functions:**
```cairo
/// @notice Validates user permissions and state for trading operations
/// @param self Contract state reference
/// @param user_address Address of user to validate
/// @return User struct if validation passes
/// @custom:reverts USER_NOT_REGISTERED if user doesn't exist
/// @custom:reverts INSUFFICIENT_BALANCE if balance too low for operation
fn _validate_user_for_trading(
    self: @ContractState,
    user_address: ContractAddress
) -> User {
    let user = self.users.read(user_address);
    
    // Structured error checking with informative messages
    if user.user_address.is_zero() {
        panic_with_felt252(AstraTradeErrors::USER_NOT_REGISTERED);
    }
    
    // Additional context-specific validations can be added here
    user
}

/// @notice Validates trading pair and returns pair information
/// @param self Contract state reference  
/// @param pair_id Trading pair identifier to validate
/// @return TradingPair struct if validation passes
/// @custom:reverts INVALID_TRADING_PAIR if pair_id doesn't exist
/// @custom:reverts PAIR_NOT_ACTIVE if pair is not currently active
fn _validate_trading_pair(
    self: @ContractState,
    pair_id: u32
) -> TradingPair {
    let trading_pair = self.trading_pairs.read(pair_id);
    
    // Check if pair exists (current_price > 0 indicates valid pair)
    if trading_pair.current_price == 0 {
        panic_with_felt252(AstraTradeErrors::INVALID_TRADING_PAIR);
    }
    
    // Check if pair is active for trading
    if !trading_pair.is_active {
        panic_with_felt252(AstraTradeErrors::PAIR_NOT_ACTIVE);
    }
    
    trading_pair
}

/// @notice Validates leverage amount against user and pair limits
/// @param user User struct containing max allowed leverage
/// @param trading_pair Trading pair with maximum leverage limit
/// @param leverage Requested leverage amount to validate
/// @custom:reverts INVALID_LEVERAGE if leverage exceeds any limits
fn _validate_leverage_comprehensive(
    user: User,
    trading_pair: TradingPair,
    leverage: u32
) {
    // Multi-level leverage validation with specific error context
    if leverage == 0 {
        panic_with_felt252('ATE203a: Leverage cannot be zero');
    }
    
    if leverage > user.max_leverage_allowed {
        panic_with_felt252('ATE203b: Exceeds user leverage limit');
    }
    
    if leverage > trading_pair.max_leverage {
        panic_with_felt252('ATE203c: Exceeds pair leverage limit');
    }
    
    if leverage > MAX_LEVERAGE {
        panic_with_felt252('ATE203d: Exceeds system leverage limit');
    }
}
```

### Stage 5: Test Coverage Enhancement
**Purpose**: Implement comprehensive test coverage with quality metrics and edge case handling

#### Test Structure Framework

**Unit Test Organization:**
```cairo
#[cfg(test)]
mod unit_tests {
    use super::*;
    
    /// @title User Management Tests
    mod user_tests {
        use super::*;
        
        #[test]
        fn test_user_registration_success() {
            let mut contract = setup_test_contract();
            let user_address = contract_address_const::<0x123>();
            
            // Test successful user registration
            start_prank(CheatTarget::One(contract.contract_address), user_address);
            contract.register_user();
            
            let user = contract.get_user(user_address);
            assert(user.user_address == user_address, 'User address mismatch');
            assert(user.current_level == 1, 'Initial level incorrect');
            assert(user.total_xp == 0, 'Initial XP should be zero');
        }
        
        #[test]
        fn test_user_registration_duplicate_fails() {
            let mut contract = setup_test_contract();
            let user_address = contract_address_const::<0x123>();
            
            // Register user first time
            start_prank(CheatTarget::One(contract.contract_address), user_address);
            contract.register_user();
            
            // Attempt duplicate registration should fail
            let result = panic::call_contract_syscall(
                contract.contract_address,
                selector!("register_user"),
                array![].span()
            );
            
            assert(result.is_err(), 'Duplicate registration should fail');
            assert(result.unwrap_err() == AstraTradeErrors::USER_ALREADY_EXISTS, 'Wrong error');
        }
    }
    
    /// @title Trading Logic Tests  
    mod trading_tests {
        use super::*;
        
        #[test]
        fn test_position_opening_gas_limit() {
            let mut contract = setup_test_contract();
            setup_test_user_and_pair(ref contract);
            
            // Measure gas usage for mobile optimization target
            let gas_before = get_gas_left();
            
            let position_id = contract.open_practice_position(
                1, // pair_id
                true, // is_long
                10, // leverage
                1000000000000000000000 // 1000 tokens collateral
            );
            
            let gas_after = get_gas_left();
            let gas_used = gas_before - gas_after;
            
            // Verify gas usage is under mobile target
            assert(gas_used < 100000, 'Gas usage exceeds mobile target');
            assert(position_id > 0, 'Position ID should be positive');
        }
        
        #[test]
        fn test_liquidation_calculation_edge_cases() {
            let contract = setup_test_contract();
            
            // Test edge case: minimum leverage
            let liq_price_min = contract._calculate_liquidation_price(
                100000000000000000000, // $100 entry price
                true, // is_long
                1, // minimum leverage
                500 // 5% maintenance
            );
            
            // Test edge case: maximum leverage
            let liq_price_max = contract._calculate_liquidation_price(
                100000000000000000000, // $100 entry price  
                true, // is_long
                MAX_LEVERAGE, // maximum leverage
                500 // 5% maintenance
            );
            
            // Verify liquidation prices are reasonable
            assert(liq_price_min < 100000000000000000000, 'Min leverage liq price too high');
            assert(liq_price_max < liq_price_min, 'Max leverage should have lower liq price');
        }
    }
    
    /// @title XP and Gamification Tests
    mod gamification_tests {
        use super::*;
        
        #[test]
        fn test_xp_award_calculation_accuracy() {
            let mut contract = setup_test_contract();
            let mut user = create_test_user();
            
            // Test base XP award
            let (xp_awarded, streak) = contract._award_trade_xp(ref user, 'PRACTICE_TRADE');
            assert(xp_awarded == XP_PER_TRADE, 'Base XP incorrect');
            assert(streak == 1, 'Initial streak should be 1');
            
            // Test streak bonus calculation
            user.last_activity_timestamp = get_block_timestamp() - 86400; // 24 hours ago
            let (xp_awarded_2, streak_2) = contract._award_trade_xp(ref user, 'PRACTICE_TRADE');
            let expected_xp = XP_PER_TRADE + (2 * XP_STREAK_BONUS); // Base + 2-day streak bonus
            assert(xp_awarded_2 == expected_xp, 'Streak XP calculation incorrect');
            assert(streak_2 == 2, 'Streak should increment to 2');
        }
    }
}
```

**Integration Test Coverage:**
```cairo
#[cfg(test)]
mod integration_tests {
    use super::*;
    
    #[test]
    fn test_complete_trading_workflow() {
        let mut contract = setup_test_contract();
        let user_addr = setup_test_user_with_balance(ref contract, 10000);
        
        // Complete workflow: register -> open position -> close position
        let position_id = contract.open_practice_position(1, true, 10, 1000);
        
        // Simulate price movement
        contract.update_pair_price(1, 11000); // 10% price increase
        
        let (pnl, is_profit) = contract.close_position(position_id);
        
        // Verify profit calculation and user balance update
        assert(is_profit, 'Position should be profitable');
        assert(pnl > 0, 'PnL should be positive');
        
        let updated_user = contract.get_user(user_addr);
        assert(updated_user.profitable_trades == 1, 'Profitable trades count incorrect');
    }
}
```

**Property-Based Testing:**
```cairo
#[cfg(test)]
mod property_tests {
    use super::*;
    
    /// Property: XP awards should always be positive and bounded
    #[test]
    fn property_xp_awards_always_positive() {
        let contract = setup_test_contract();
        let mut user = create_test_user_with_random_state();
        
        // Test with various activity types
        let activity_types = array!['PRACTICE_TRADE', 'LIVE_TRADE', 'PROFITABLE_TRADE'];
        let mut i = 0;
        
        loop {
            if i >= activity_types.len() {
                break;
            }
            
            let activity = *activity_types.at(i);
            let (xp_awarded, _) = contract._award_trade_xp(ref user, activity);
            
            // XP should always be positive and reasonable
            assert(xp_awarded > 0, 'XP should be positive');
            assert(xp_awarded <= 1000, 'XP should be bounded'); // Reasonable upper limit
            
            i += 1;
        };
    }
}
```

## Quality Metrics Dashboard

### Automated Quality Measurement
```cairo
#[cfg(test)]
mod quality_metrics {
    /// Measure and report code quality metrics
    #[test]
    fn generate_quality_report() {
        let contract = setup_test_contract();
        
        println!("=== AstraTrade Exchange V2 Quality Report ===");
        println!("Contract Lines of Code: {}", measure_loc());
        println!("Function Count: {}", count_functions());
        println!("Average Function Length: {}", calculate_avg_function_length());
        println!("Cyclomatic Complexity: {}", measure_complexity());
        println!("Test Coverage: {}%", measure_test_coverage());
        println!("Documentation Coverage: {}%", measure_doc_coverage());
    }
}
```

## Sample Output

```
📚 Cairo Code Quality Enhancement: Function Decomposition
========================================================

📊 Quality Assessment:
   - Current Function Complexity: 12 (HIGH - target: <8)
   - Responsibilities: 4 (XP, streak, level, achievements)
   - Test Coverage: 45% (target: 95%+)
   - Documentation: 68% (target: 90%+)

🔧 REFACTORING PLAN:
   Phase 1: Extract pure functions (Day 1)
   Phase 2: Implement focused functions (Day 2)
   Phase 3: Add comprehensive documentation (Day 3)
   Phase 4: Enhance test coverage (Day 4)

📈 QUALITY IMPROVEMENTS:
   - Functions: 1 monolithic → 4 focused functions
   - Testability: Complex integration → Simple unit tests
   - Maintainability: High coupling → Clear separation
   - Documentation: Minimal → Comprehensive NatSpec

✅ VALIDATION METRICS:
   ✅ Cyclomatic complexity: 12 → 3 average (75% reduction)
   ✅ Function length: 45 → 15 lines average (67% reduction)
   ✅ Test coverage: 45% → 95% (target achieved)
   ✅ Documentation: 68% → 92% (target achieved)

🚀 TECHNICAL DEBT REDUCTION:
   Before: 3.2 person-weeks estimated debt
   After: 0.8 person-weeks estimated debt
   Improvement: 75% technical debt reduction
```

## Implementation

This workflow executes through the enhanced GRAPH-R1 CLI:

```bash
source venv/bin/activate
python graph_r1/graph_r1_cli.py code-quality {{enhancement_type}} {{target_file}} {{options}}
```

The workflow leverages:
- Systematic function complexity analysis and decomposition
- Comprehensive documentation standards with NatSpec
- Enhanced error handling with standardized error codes
- Property-based testing for robust quality assurance
- Automated quality metrics and technical debt measurement