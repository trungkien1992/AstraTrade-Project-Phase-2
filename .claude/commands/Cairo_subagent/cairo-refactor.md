# Cairo Refactoring Workflow

Safe, incremental refactoring workflow for Cairo smart contracts with comprehensive impact analysis and rollback strategies.

## Usage

```bash
@claude cairo-refactor "<refactoring_request>"
```

## Sub-commands

- `@claude cairo-refactor "request"`: Full refactoring analysis and plan
- `@claude cairo-refactor "request" --impact`: Deep impact analysis only
- `@claude cairo-refactor "request" --incremental`: Step-by-step refactoring guide
- `@claude cairo-refactor "request" --rollback`: Focus on rollback and safety strategies

## Examples

```bash
# Complete refactoring analysis
@claude cairo-refactor "Extract common trading logic into reusable functions"

# Impact analysis before refactoring
@claude cairo-refactor "Split large User struct into smaller components" --impact

# Incremental refactoring steps
@claude cairo-refactor "Optimize storage layout for gas efficiency" --incremental

# Rollback-focused planning
@claude cairo-refactor "Migrate from direct storage to mapped storage" --rollback
```

## Workflow Stages

### Stage 1: Refactoring Impact Assessment
**Purpose**: Comprehensive analysis of refactoring scope, dependencies, and risks
**Adapts**: HRM Deep Analysis + Comprehensive Debug + Risk Assessment

**Impact Analysis Categories**:

**Code Impact Assessment**:
- **Direct Dependencies**: Functions, structs, storage directly affected
- **Indirect Dependencies**: Downstream effects on dependent contracts
- **Interface Changes**: Breaking vs non-breaking API modifications
- **Storage Layout Changes**: Data migration requirements and compatibility

**Business Impact Scoring**:
```
Impact Severity Matrix:
- CRITICAL: Revenue-affecting functions, user fund safety
- HIGH: Core trading functionality, user experience
- MEDIUM: Optimization features, non-core functionality  
- LOW: Internal improvements, developer experience
```

**Technical Complexity Assessment**:
- **Refactoring Complexity Score**: Based on lines of code, dependency count, test coverage
- **Migration Complexity**: Data transformation requirements
- **Testing Complexity**: New test scenarios and validation requirements
- **Deployment Complexity**: Staging, migration scripts, feature flag requirements

**Risk Factor Analysis**:
- **Regression Risk**: Potential for introducing bugs in existing functionality
- **Performance Risk**: Gas cost implications and optimization trade-offs  
- **Security Risk**: New attack vectors or weakened security patterns
- **Integration Risk**: Impact on external contracts and off-chain systems

**Actions**:
- Parse target code and build comprehensive dependency graph
- Calculate complexity scores using HRM-style analysis
- Assess business criticality of affected functions
- Generate risk matrix with likelihood and impact scoring

**Outputs**:
- `artifacts/impact_assessment.md`: Comprehensive dependency and risk analysis
- `artifacts/complexity_scoring.md`: Technical complexity breakdown
- `artifacts/business_impact.md`: Revenue and user experience implications

### Stage 2: Conservative Refactoring Plan
**Purpose**: Design minimal, safe refactoring approach with explicit boundaries and rollback strategy
**Adapts**: Lean Hypothesis + Conservative Validation + Feature Flag patterns

**Refactoring Strategy Development**:

**Minimal Viable Refactoring (MVR)**:
- Define smallest possible scope that delivers value
- Identify "no-go" boundaries to prevent scope creep
- Establish success criteria and regression detection metrics
- Plan incremental delivery with validation checkpoints

**Boundary Definition**:
```
✅ SAFE REFACTORING BOUNDARIES:
- Internal function reorganization without interface changes
- Storage optimization with backward compatibility
- Code extraction with identical behavior preservation
- Documentation and naming improvements

❌ HIGH-RISK BOUNDARIES (Require special approval):
- External function signature changes
- Storage layout modifications affecting existing data
- Security pattern changes
- Cross-contract interface modifications
```

**Feature Flag Strategy**:
```cairo
// Example feature flag pattern for refactoring
#[storage]
struct Storage {
    use_new_calculation_method: bool,
    // ... other storage
}

fn calculate_position_value(self: @ContractState, position: Position) -> u256 {
    if self.use_new_calculation_method.read() {
        self._calculate_position_value_v2(position)
    } else {
        self._calculate_position_value_v1(position)
    }
}
```

**Rollback Strategy Components**:
- **Feature Flags**: Runtime switching between old and new implementations
- **Data Migration Scripts**: Forward and backward migration capabilities
- **Monitoring Alerts**: Automated detection of regression issues
- **Emergency Procedures**: Rapid rollback processes and communication plans

**Actions**:
- Design incremental refactoring phases with validation gates
- Create feature flag implementation for risky changes
- Develop comprehensive rollback procedures
- Establish success metrics and regression detection methods

**Outputs**:
- `artifacts/refactoring_plan.md`: Detailed phase-by-phase implementation plan
- `artifacts/rollback_strategy.md`: Complete emergency procedures and feature flags
- `artifacts/validation_gates.md`: Success criteria and regression detection

### Stage 3: Step-by-Step Implementation Guide
**Purpose**: Provide detailed, incremental refactoring steps with validation at each phase
**Adapts**: Testing Strategies + Property-Based validation + Observability patterns

**Implementation Phases**:

**Phase 1: Preparation and Safety Setup**
```bash
# 1. Create feature branch with descriptive name
git checkout -b refactor/extract-trading-logic-2024-01

# 2. Backup current state and create rollback point
git tag refactor-start-$(date +%Y%m%d)

# 3. Add comprehensive tests for current behavior
# 4. Set up monitoring and alerting for target functions
# 5. Implement feature flags for risky changes
```

**Phase 2: Incremental Implementation**
```cairo
// Step 1: Extract pure functions (lowest risk)
fn _calculate_pnl_pure(entry_price: u256, current_price: u256, position_size: u256, is_long: bool) -> (u256, bool) {
    // Pure calculation logic
}

// Step 2: Refactor impure functions to use pure functions
fn _calculate_pnl(self: @ContractState, position: Position, current_price: u256) -> (u256, bool) {
    _calculate_pnl_pure(position.entry_price, current_price, 
                       position.collateral * position.leverage.into(), position.is_long)
}

// Step 3: Update calling functions incrementally with feature flags
```

**Phase 3: Validation and Rollout**
- **Unit Test Validation**: All existing tests pass + new tests for refactored code
- **Integration Testing**: Cross-contract interactions function correctly
- **Gas Benchmarking**: Performance regression testing
- **Security Review**: Ensure no new vulnerabilities introduced

**Testing Strategy Integration**:

**Regression Test Suite**:
- **Golden Master Tests**: Snapshot current behavior for comparison
- **Property-Based Tests**: Verify mathematical invariants maintained
- **Integration Tests**: End-to-end workflow validation
- **Performance Tests**: Gas usage and execution time benchmarks

**Validation Checkpoints**:
```
Checkpoint 1: Pure function extraction
- ✅ All existing tests pass
- ✅ New functions have 100% test coverage
- ✅ No gas regression detected

Checkpoint 2: Integration with feature flags
- ✅ Both code paths produce identical results
- ✅ Feature flag switching works correctly
- ✅ Monitoring alerts configured

Checkpoint 3: Full migration
- ✅ All tests pass with new implementation
- ✅ Performance benchmarks meet targets
- ✅ Security review approved
```

**Actions**:
- Generate step-by-step implementation checklist
- Create comprehensive test suite for current and new behavior
- Implement monitoring and alerting for refactored functions
- Design validation checkpoints with go/no-go criteria

**Outputs**:
- `artifacts/implementation_steps.md`: Detailed step-by-step checklist
- `artifacts/testing_suite.md`: Complete test strategy and implementation
- `artifacts/monitoring_plan.md`: Observability and alerting setup

### Stage 4: Post-Refactoring Validation
**Purpose**: Comprehensive validation of refactoring success and system health
**Adapts**: Observability-Backed Testing + HRM contextual analysis

**Validation Categories**:

**Functional Validation**:
- **Behavior Preservation**: All existing functionality works identically
- **Interface Compatibility**: External contracts can interact without changes
- **Data Integrity**: No data corruption or loss during migration
- **Error Handling**: Edge cases and error conditions handled properly

**Performance Validation**:
- **Gas Usage Comparison**: Before/after gas consumption analysis
- **Execution Time**: Function performance benchmarking
- **Storage Efficiency**: Storage slot utilization improvements
- **Throughput**: High-load scenario performance testing

**Security Validation**:
- **Attack Vector Analysis**: No new security vulnerabilities introduced
- **Access Control**: Permission systems function correctly
- **State Invariants**: Contract invariants maintained
- **Audit Trail**: All changes properly logged and traceable

**Maintenance Validation**:
- **Code Quality**: Improved readability and maintainability metrics
- **Documentation**: Updated documentation and code comments
- **Test Coverage**: Comprehensive test coverage for new code paths
- **Developer Experience**: Easier development and debugging capabilities

## Conservative Safety Features

### Confidence Requirements
- **95% Confidence Threshold**: Required for recommending any refactoring
- **Mandatory Clarification**: Vague refactoring requests trigger detailed questioning
- **Impact Assessment**: Always perform before suggesting implementation
- **Approval Gates**: Explicit approval required for high-risk refactoring

### Risk Mitigation Strategies
- **Feature Flags**: Runtime switching for all risky changes
- **Incremental Rollout**: Phase-by-phase implementation with validation
- **Automated Rollback**: Monitoring-triggered automatic rollback capabilities
- **Emergency Procedures**: Clear escalation and communication protocols

### Query Validation Examples
```
❌ Vague Request: "optimize my contract"
✅ Specific Request: "extract duplicate liquidation logic from close_position and liquidate_position functions"

❌ High-Risk Scope: "completely rewrite the trading system"
✅ Bounded Scope: "refactor User struct to improve gas efficiency while maintaining interface compatibility"
```

## Sample Output

```
🔧 Cairo Refactoring Analysis: User Struct Optimization
====================================================

📊 Impact Assessment:
   - Complexity Score: 42/100 (Medium complexity)
   - Business Impact: HIGH (affects all user operations)
   - Technical Risk: MEDIUM (storage layout changes)
   - Confidence: 94% (high confidence in approach)

🎯 REFACTORING PLAN:
   Objective: Optimize User struct storage layout for 20% gas savings
   Approach: Pack boolean fields into bitmask, optimize field ordering
   Timeline: 4-5 days including testing and rollout

⚠️  RISK ASSESSMENT:
   - Data Migration Required: YES (automated script provided)
   - Interface Breaking: NO (getter functions maintain compatibility)
   - Rollback Complexity: LOW (feature flag enables instant rollback)

📋 IMPLEMENTATION PHASES:
   Phase 1: Create optimized struct definition (Day 1)
   Phase 2: Implement pack/unpack helper functions (Day 1-2)
   Phase 3: Add feature flag switching mechanism (Day 2)
   Phase 4: Update all contract functions incrementally (Day 2-3)
   Phase 5: Testing and validation (Day 4)
   Phase 6: Migration and rollout (Day 5)

🛡️ SAFETY MEASURES:
   - Feature flag for instant rollback
   - Comprehensive migration testing
   - Gas benchmarking at each phase
   - Automated regression detection

💡 NEXT STEPS:
   1. Review and approve refactoring plan
   2. Set up monitoring and alerting
   3. Begin Phase 1 implementation
   4. Schedule security review checkpoint
```

## Implementation

This workflow executes through the enhanced GRAPH-R1 CLI:

```bash
source venv/bin/activate
python graph_r1/graph_r1_cli.py refactor "{{refactoring_request}}" {{options}}
```

The workflow leverages:
- Multi-expert agent collaboration for comprehensive impact analysis
- HRM-style deep analysis with business context awareness
- Conservative validation with explicit approval gates
- Feature flag patterns and rollback strategies for safe deployment