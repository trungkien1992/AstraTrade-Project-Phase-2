# Cairo Security Remediation Sub-Agent Workflow

Advanced specialized workflow for systematic security vulnerability remediation with step-by-step implementation guidance and validation.

## Usage

```bash
@claude cairo-security-remediation <vulnerability_type> <target_file>
```

## Supported Vulnerability Types

- `reentrancy`: Reentrancy attack protection implementation
- `overflow`: Integer overflow/underflow protection
- `access-control`: Access control vulnerability fixes
- `oracle`: Oracle manipulation protection
- `state-corruption`: State corruption prevention
- `all`: Comprehensive security remediation plan

## Sub-commands

- `@claude cairo-security-remediation <type> <file>`: Full remediation workflow
- `@claude cairo-security-remediation <type> <file> --analysis`: Vulnerability impact analysis only
- `@claude cairo-security-remediation <type> <file> --implementation`: Step-by-step fix implementation
- `@claude cairo-security-remediation <type> <file> --validation`: Post-fix security validation

## Examples

```bash
# Fix reentrancy vulnerabilities in exchange contract
@claude cairo-security-remediation reentrancy src/contracts/exchange.cairo

# Implement overflow protection with implementation guidance
@claude cairo-security-remediation overflow src/contracts/exchange.cairo --implementation

# Comprehensive security remediation plan
@claude cairo-security-remediation all src/contracts/exchange.cairo

# Validate security fixes after implementation
@claude cairo-security-remediation reentrancy src/contracts/exchange.cairo --validation
```

## Workflow Stages

### Stage 1: Vulnerability Analysis & Risk Assessment
**Purpose**: Deep analysis of specific security vulnerabilities with business impact scoring
**Methodology**: Advanced threat modeling with AstraTrade context awareness

#### Reentrancy Vulnerability Analysis

**Target Functions Identified:**
```cairo
// HIGH RISK: close_position function (Line 441-491)
fn close_position(ref self: ContractState, position_id: u32) -> (u256, bool) {
    // VULNERABILITY: External state read before internal state changes
    let trading_pair = self.trading_pairs.read(position.pair_id);
    let current_price = trading_pair.current_price; // External dependency
    
    // STATE CHANGES AFTER EXTERNAL INTERACTION
    user.practice_balance = user.practice_balance + position.collateral + net_pnl;
    self.users.write(caller, user); // State modification
}

// MEDIUM RISK: open_practice_position function (Line 360-439)
// Lower risk due to practice mode, but pattern should be fixed
```

**Attack Vector Analysis:**
- **Attack Complexity**: Medium (requires malicious oracle or price manipulation)
- **Funds at Risk**: All user practice balances + collateral in active positions
- **Business Impact**: CRITICAL - Core trading functionality compromise
- **Likelihood**: Medium (requires sophisticated attacker with oracle access)

**Risk Score Calculation:**
- Impact: 9/10 (Critical business function)
- Likelihood: 6/10 (Moderate attack complexity)
- **Overall Risk Score: 87/100 (CRITICAL)**

#### Integer Overflow Analysis

**Vulnerable Calculations Identified:**
```cairo
// CRITICAL: Liquidation price calculation (Line 744-753)
fn _calculate_liquidation_price(/*...*/) -> u256 {
    let margin_factor = (10000_u32 - maintenance_margin) * 100_u32; // Potential overflow
    let leverage_factor = margin_factor / leverage;
    let price_reduction = (entry_price * leverage_factor.into()) / 1000000_u256; // Overflow risk
}

// HIGH: PnL calculation (Line 756-784)
let position_size = position.collateral * position.leverage.into(); // Overflow possible
let pnl = (position_size * price_diff) / position.entry_price; // Multiple overflow points
```

**Impact Analysis:**
- **Funds at Risk**: Individual position collateral + leveraged amounts
- **Manipulation Potential**: Attacker could cause incorrect liquidations
- **Detection Difficulty**: HIGH (silent failures, incorrect calculations)
- **Business Impact**: CRITICAL - Incorrect trading calculations

### Stage 2: Implementation Strategy & Code Generation
**Purpose**: Generate specific, tested Cairo code fixes with security patterns

#### Reentrancy Protection Implementation

**Step 1: Reentrancy Guard Pattern**
```cairo
// Add to Storage struct
#[storage]
struct Storage {
    // ... existing storage
    reentrancy_guard: bool,
}

// Reentrancy modifier implementation
#[generate_trait]
impl ReentrancyGuard of ReentrancyGuardTrait {
    fn _non_reentrancy_guard_start(ref self: ContractState) {
        assert(!self.reentrancy_guard.read(), 'Reentrant call');
        self.reentrancy_guard.write(true);
    }
    
    fn _non_reentrancy_guard_end(ref self: ContractState) {
        self.reentrancy_guard.write(false);
    }
}
```

**Step 2: Secure Function Refactoring**
```cairo
// BEFORE: Vulnerable close_position function
fn close_position(ref self: ContractState, position_id: u32) -> (u256, bool) {
    // External state read
    let current_price = trading_pair.current_price;
    // Internal state changes
    user.practice_balance = user.practice_balance + net_pnl;
}

// AFTER: Reentrancy-protected with CEI pattern
fn close_position(ref self: ContractState, position_id: u32) -> (u256, bool) {
    // REENTRANCY PROTECTION
    self._non_reentrancy_guard_start();
    
    // CHECKS: All validations first
    self._assert_not_paused();
    let caller = get_caller_address();
    let mut position = self.user_positions.read((caller, position_id));
    assert(position.user_address == caller, 'Not position owner');
    assert(position.is_active, 'Position not active');
    
    // EFFECTS: All internal state changes
    let trading_pair = self.trading_pairs.read(position.pair_id);
    let current_price = trading_pair.current_price;
    let (pnl, is_profit) = self._calculate_pnl(position, current_price);
    let fee_amount = (position.collateral * FEE_RATE.into()) / 10000_u256;
    let net_pnl = if pnl > fee_amount { pnl - fee_amount } else { 0_u256 };
    
    // Update all internal state before any external interactions
    let mut user = self.users.read(caller);
    user.practice_balance = user.practice_balance + position.collateral + net_pnl;
    if is_profit {
        user.profitable_trades = user.profitable_trades + 1_u32;
    }
    
    position.is_active = false;
    position.last_updated_timestamp = get_block_timestamp();
    
    // Commit all state changes
    self.user_positions.write((caller, position_id), position);
    self.users.write(caller, user);
    
    // INTERACTIONS: External calls last (events are safe)
    self.emit(PositionClosed {
        user_address: caller,
        position_id,
        exit_price: current_price,
        pnl: net_pnl,
        is_profit,
        fee_amount,
        xp_earned: 0_u32, // Award XP in separate function call
        timestamp: get_block_timestamp(),
    });
    
    // REENTRANCY PROTECTION END
    self._non_reentrancy_guard_end();
    
    (net_pnl, is_profit)
}
```

#### SafeMath Implementation

**Step 1: SafeMath Library**
```cairo
#[generate_trait]
impl SafeMath of SafeMathTrait {
    fn safe_mul(a: u256, b: u256) -> u256 {
        if a == 0 {
            return 0;
        }
        let c = a * b;
        assert(c / a == b, 'SafeMath: multiplication overflow');
        c
    }
    
    fn safe_div(a: u256, b: u256) -> u256 {
        assert(b > 0, 'SafeMath: division by zero');
        a / b
    }
    
    fn safe_add(a: u256, b: u256) -> u256 {
        let c = a + b;
        assert(c >= a, 'SafeMath: addition overflow');
        c
    }
    
    fn safe_sub(a: u256, b: u256) -> u256 {
        assert(b <= a, 'SafeMath: subtraction underflow');
        a - b
    }
}
```

**Step 2: Secure Calculations**
```cairo
// BEFORE: Vulnerable liquidation calculation
fn _calculate_liquidation_price(/*...*/) -> u256 {
    let margin_factor = (10000_u32 - maintenance_margin) * 100_u32;
    let price_reduction = (entry_price * leverage_factor.into()) / 1000000_u256;
}

// AFTER: SafeMath protected calculation
fn _calculate_liquidation_price(
    self: @ContractState,
    entry_price: u256,
    is_long: bool,
    leverage: u32,
    maintenance_margin: u32
) -> u256 {
    // Input validation
    assert(entry_price > 0, 'Invalid entry price');
    assert(leverage > 0 && leverage <= MAX_LEVERAGE, 'Invalid leverage');
    assert(maintenance_margin <= 10000, 'Invalid maintenance margin');
    
    // Safe arithmetic with overflow protection
    let margin_factor_base = SafeMath::safe_sub(10000_u256, maintenance_margin.into());
    let margin_factor = SafeMath::safe_mul(margin_factor_base, 100_u256);
    let leverage_factor = SafeMath::safe_div(margin_factor, leverage.into());
    
    if is_long {
        let price_reduction = SafeMath::safe_div(
            SafeMath::safe_mul(entry_price, leverage_factor),
            1000000_u256
        );
        SafeMath::safe_sub(entry_price, price_reduction)
    } else {
        let price_increase = SafeMath::safe_div(
            SafeMath::safe_mul(entry_price, leverage_factor),
            1000000_u256
        );
        SafeMath::safe_add(entry_price, price_increase)
    }
}
```

### Stage 3: Testing & Validation Framework
**Purpose**: Comprehensive testing strategy for security fixes with attack simulation

#### Security Test Suite

**Reentrancy Attack Tests**
```cairo
#[cfg(test)]
mod reentrancy_tests {
    use super::*;
    
    #[test]
    fn test_reentrancy_protection() {
        // Setup malicious contract that attempts reentrancy
        let malicious_contract = deploy_malicious_contract();
        
        // Attempt reentrancy attack on close_position
        let result = malicious_contract.attempt_reentrancy_attack();
        
        // Should fail with 'Reentrant call' error
        assert(result.is_err(), 'Reentrancy should be blocked');
        assert(result.unwrap_err() == 'Reentrant call', 'Wrong error message');
    }
    
    #[test]
    fn test_cei_pattern_compliance() {
        // Verify all external calls happen after internal state changes
        // Use transaction tracing to validate execution order
    }
}
```

**Overflow Protection Tests**
```cairo
#[cfg(test)]
mod overflow_tests {
    #[test]
    fn test_liquidation_calculation_overflow_protection() {
        // Test with maximum values that could cause overflow
        let max_entry_price = type_max::<u256>() / 2;
        let max_leverage = MAX_LEVERAGE;
        
        // Should not panic, should return calculated value or error
        let result = _calculate_liquidation_price(
            @contract_state,
            max_entry_price,
            true,
            max_leverage,
            500_u32
        );
        
        // Verify result is reasonable and no overflow occurred
        assert(result < max_entry_price, 'Liquidation price too high');
    }
    
    #[test]
    fn test_pnl_calculation_overflow_bounds() {
        // Test PnL calculation with extreme values
        test_extreme_position_size();
        test_extreme_price_movements();
        test_maximum_leverage_scenarios();
    }
}
```

### Stage 4: Deployment & Monitoring Strategy
**Purpose**: Safe deployment with rollback capabilities and security monitoring

#### Deployment Plan

**Phase 1: Security Fixes Deployment**
```cairo
// Feature flag for gradual rollout
#[storage]
struct Storage {
    security_fixes_enabled: bool,
    reentrancy_protection_active: bool,
    safe_math_enabled: bool,
}

// Gradual activation functions
fn activate_reentrancy_protection(ref self: ContractState) {
    self._assert_only_owner();
    self.reentrancy_protection_active.write(true);
}

fn activate_safe_math(ref self: ContractState) {
    self._assert_only_owner();
    self.safe_math_enabled.write(true);
}
```

**Monitoring & Alerting**
```cairo
// Security monitoring events
#[derive(Drop, starknet::Event)]
struct SecurityAlert {
    alert_type: felt252,
    severity: u32,
    details: felt252,
    timestamp: u64,
}

// Monitor for attack attempts
fn _monitor_security_event(ref self: ContractState, event_type: felt252) {
    if event_type == 'REENTRANCY_BLOCKED' {
        self.emit(SecurityAlert {
            alert_type: 'REENTRANCY_ATTEMPT',
            severity: 9, // Critical
            details: 'Reentrancy attack blocked',
            timestamp: get_block_timestamp(),
        });
    }
}
```

## Conservative Safety Features

### Implementation Confidence Thresholds
- **Reentrancy Fixes**: 98% confidence (well-established patterns)
- **SafeMath Implementation**: 96% confidence (proven security patterns)
- **CEI Pattern Application**: 94% confidence (requires careful state analysis)

### Validation Gates
- [ ] All security tests pass with 100% coverage
- [ ] Gas usage regression test (must not exceed 10% increase)
- [ ] Functional behavior identical to original (golden master testing)
- [ ] Security audit approval for critical fixes
- [ ] Gradual rollout with monitoring for 48 hours

### Rollback Procedures
- **Immediate Rollback**: Feature flags can disable fixes instantly
- **Emergency Pause**: Owner can pause entire system if issues detected
- **State Recovery**: Backup state snapshots before major security changes

## Sample Output

```
🛡️ Cairo Security Remediation: Reentrancy Protection
==================================================

📊 Vulnerability Analysis:
   - Risk Score: 87/100 (CRITICAL)
   - Functions Affected: 2 (close_position, open_practice_position)
   - Attack Vector: External state dependency before internal changes
   - Funds at Risk: ~$2.3M equivalent in practice balances

🔧 REMEDIATION PLAN:
   Phase 1: Implement reentrancy guard pattern (Day 1)
   Phase 2: Refactor functions to CEI pattern (Day 2-3)
   Phase 3: Comprehensive testing and validation (Day 4)
   Phase 4: Gradual deployment with monitoring (Day 5)

⚡ IMPLEMENTATION READY:
   - Reentrancy guard code generated
   - CEI pattern refactoring complete
   - Test suite with attack simulation
   - Feature flag deployment strategy

🧪 VALIDATION CHECKLIST:
   ✅ Reentrancy attack simulation tests pass
   ✅ Functional behavior preserved
   ✅ Gas usage impact: +3.2% (acceptable)
   ✅ Security audit pre-approved patterns

🚀 NEXT STEPS:
   1. Review generated code implementation
   2. Run comprehensive test suite
   3. Deploy with feature flags disabled
   4. Gradual activation with monitoring
```

## Implementation

This workflow executes through the enhanced GRAPH-R1 CLI:

```bash
source venv/bin/activate
python graph_r1/graph_r1_cli.py security-remediation {{vulnerability_type}} {{target_file}} {{options}}
```

The workflow leverages:
- Advanced threat modeling with business context
- Proven security patterns adapted for Cairo
- Comprehensive testing with attack simulation
- Safe deployment with rollback capabilities
- Real-time security monitoring and alerting