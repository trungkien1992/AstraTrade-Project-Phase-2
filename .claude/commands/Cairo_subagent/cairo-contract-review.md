# Cairo Contract Review Workflow

Comprehensive code quality and architectural review workflow for Cairo smart contracts using HRM-style contextual analysis.

## Usage

```bash
@claude cairo-contract-review <contract_path>
```

## Sub-commands

- `@claude cairo-contract-review <path>`: Full contract review
- `@claude cairo-contract-review <path> --architecture`: Focus on architectural patterns
- `@claude cairo-contract-review <path> --quality`: Code quality and maintainability analysis
- `@claude cairo-contract-review <path> --performance`: Gas optimization and performance review

## Examples

```bash
# Complete contract review
@claude cairo-contract-review src/contracts/exchange.cairo

# Architecture-focused review
@claude cairo-contract-review apps/backend/contracts/ --architecture

# Code quality assessment
@claude cairo-contract-review src/contracts/vault.cairo --quality

# Performance and gas optimization review
@claude cairo-contract-review src/contracts/trading.cairo --performance
```

## Workflow Stages

### Stage 1: Architectural Assessment
**Purpose**: Evaluate contract structure, separation of concerns, and design patterns
**Adapts**: HRM Contextual Analysis + Research Framework

**Architectural Analysis Categories**:

**Contract Structure Assessment**:
- **Modularity**: Single responsibility principle adherence
- **Abstraction Layers**: Proper separation between interface, implementation, and storage
- **Dependency Management**: Import structure and circular dependency detection
- **Interface Design**: External function organization and discoverability

**Design Pattern Evaluation**:
- **Access Control Patterns**: Owner, role-based, multi-signature implementations
- **State Management**: Storage organization, state transitions, invariant maintenance
- **Event Architecture**: Comprehensive event emission for off-chain integration
- **Upgrade Patterns**: Proxy patterns, migration strategies, versioning

**Domain Alignment**:
- **AstraTrade Concepts**: Trading, gamification, user management integration
- **Business Logic Separation**: Core domain logic vs infrastructure concerns
- **Cross-Contract Integration**: API design for ecosystem interoperability

**Actions**:
- Parse contract structure and identify architectural layers
- Map function responsibilities and interaction patterns
- Validate design patterns against Cairo best practices
- Assess alignment with AstraTrade domain architecture

**Outputs**:
- `artifacts/architecture_assessment.md`: Structural analysis with diagrams
- `artifacts/pattern_evaluation.md`: Design pattern adherence scoring
- `artifacts/domain_alignment.md`: Business logic organization review

### Stage 2: Code Quality Analysis
**Purpose**: Assess code maintainability, readability, and development best practices
**Adapts**: HRM Deep Analysis + Testing Strategies

**Code Quality Metrics**:

**Complexity Analysis**:
```
Function Complexity Scoring:
- Simple (1-10 lines): Low complexity
- Medium (11-30 lines): Moderate complexity  
- Complex (31-50 lines): High complexity
- Very Complex (50+ lines): Refactoring candidate
```

**Documentation Coverage**:
- [ ] Contract-level documentation with purpose and usage
- [ ] Function-level NatSpec comments with parameters and returns
- [ ] Complex logic inline comments
- [ ] Storage variable documentation
- [ ] Event documentation for off-chain integration

**Error Handling Patterns**:
- [ ] Consistent error message conventions
- [ ] Proper use of assert vs require patterns
- [ ] Input validation coverage
- [ ] Edge case handling
- [ ] Graceful degradation strategies

**Code Style Consistency**:
- [ ] Naming conventions (snake_case, descriptive names)
- [ ] Function ordering and organization
- [ ] Consistent indentation and formatting
- [ ] Type usage patterns (felt252 vs u256 appropriateness)

**Actions**:
- Calculate function complexity scores using cyclomatic complexity
- Assess documentation coverage and quality
- Evaluate error handling patterns and consistency
- Check adherence to Cairo style guidelines

**Outputs**:
- `artifacts/complexity_analysis.md`: Function-by-function complexity scoring
- `artifacts/documentation_review.md`: Documentation coverage and quality assessment
- `artifacts/style_consistency.md`: Code style and convention adherence

### Stage 3: Performance & Optimization Review
**Purpose**: Analyze gas usage, storage efficiency, and performance characteristics
**Adapts**: Observability-Backed Testing + Property-Based concepts

**Performance Analysis Categories**:

**Gas Usage Optimization**:
```cairo
// Gas-inefficient pattern
for i in 0..user_count {
    storage.write(user_data[i]);  // Multiple storage writes
}

// Gas-optimized pattern  
let batch_data = prepare_batch(user_data);
storage.write_batch(batch_data);  // Single batch operation
```

**Storage Pattern Analysis**:
- **Storage Layout Efficiency**: Struct packing, slot utilization
- **Access Pattern Optimization**: Frequently accessed data organization
- **Storage Operation Minimization**: Batch operations, temporary variables
- **Data Structure Selection**: Arrays vs mappings vs custom structures

**Computational Efficiency**:
- **Algorithm Complexity**: O(n) vs O(1) operation preferences
- **Mathematical Optimizations**: Bitwise operations, lookup tables
- **Loop Optimization**: Bounds checking, early termination
- **Memory Management**: Temporary variable usage, scope optimization

**Integration Performance**:
- **External Call Efficiency**: Minimizing cross-contract calls
- **Event Emission Patterns**: Efficient event data structures
- **Oracle Integration**: Caching strategies, fallback mechanisms

**Actions**:
- Analyze storage operations for optimization opportunities
- Identify computational hotspots and algorithm improvements
- Evaluate gas costs for typical operation scenarios
- Suggest batch operation patterns and caching strategies

**Outputs**:
- `artifacts/gas_analysis.md`: Function-level gas usage assessment
- `artifacts/storage_optimization.md`: Storage pattern improvement suggestions
- `artifacts/performance_recommendations.md`: Algorithm and efficiency improvements

## Quality Assessment Framework

### Contract Quality Scoring
```
Overall Quality Score: Weighted average of:
- Architecture (30%): Design patterns, modularity, domain alignment
- Code Quality (25%): Complexity, documentation, error handling
- Performance (25%): Gas efficiency, storage optimization
- Security (20%): Security pattern adherence, vulnerability absence
```

### Review Categories

**Green Zone (85-100)**:
- Well-architected with clear separation of concerns
- Comprehensive documentation and error handling
- Gas-optimized with efficient storage patterns
- Security best practices consistently applied

**Yellow Zone (70-84)**:
- Generally good architecture with minor improvements needed
- Adequate documentation with some gaps
- Reasonable performance with optimization opportunities
- Basic security patterns with enhancement areas

**Red Zone (<70)**:
- Architectural issues requiring significant refactoring
- Poor documentation and inconsistent error handling
- Inefficient gas usage and storage patterns
- Security vulnerabilities or missing critical protections

## Contextual Intelligence Features

### AstraTrade-Specific Analysis
- **Trading Logic Review**: Position calculations, liquidation safety, fee handling
- **Gamification Integration**: XP calculations, achievement logic, streak management
- **Mobile Optimization**: Gas limits for mobile transactions (<100k gas target)
- **Flutter Integration**: Event structure for real-time UI updates

### Business Context Awareness
- **Revenue Impact**: Critical vs non-critical function classification
- **User Experience**: Transaction flow optimization for mobile users
- **Scalability Considerations**: Volume handling and batch operation capabilities
- **Compliance Requirements**: KYC integration, audit trail maintenance

## Sample Output

```
📋 Cairo Contract Review: AstraTradeExchangeV2
=============================================

📊 Overall Quality Score: 78/100 (Yellow Zone)
   - Architecture: 85/100 (Good separation of concerns)
   - Code Quality: 72/100 (Documentation gaps identified)
   - Performance: 76/100 (Some optimization opportunities)
   - Security: 78/100 (Basic patterns present, enhancements recommended)

🏗️ ARCHITECTURAL ASSESSMENT:
   ✅ Clear domain separation (trading, gamification, user management)
   ✅ Proper access control with owner patterns
   ⚠️  Event architecture could be enhanced for mobile integration
   ❌ Missing upgrade mechanism for contract evolution

📝 CODE QUALITY FINDINGS:
   - Function Complexity: 3 functions exceed recommended 30-line limit
   - Documentation: 68% coverage (target: 90%+)
   - Error Handling: Consistent patterns, good assert usage
   - Style: Generally consistent, minor naming convention issues

⚡ PERFORMANCE OPPORTUNITIES:
   - Storage optimization in User struct (potential 20% gas savings)
   - Batch operations for multiple position updates
   - Liquidation calculation can be optimized with lookup tables
   - Event emission can be more gas-efficient

🎯 PRIORITY RECOMMENDATIONS:
   1. Add comprehensive NatSpec documentation (2-3 days)
   2. Implement User struct packing optimization (1-2 days)
   3. Enhance event architecture for mobile integration (3-4 days)
   4. Add contract upgrade mechanism (5-7 days)
```

## Implementation

This workflow executes through the enhanced GRAPH-R1 CLI:

```bash
source venv/bin/activate
python graph_r1/graph_r1_cli.py contract-review {{contract_path}} {{options}}
```

The workflow leverages:
- Multi-expert agent collaboration for comprehensive analysis
- HRM-style contextual understanding with business impact assessment
- AstraTrade domain-specific knowledge for relevant recommendations
- Conservative validation with evidence-based scoring