# Cairo Development Assistant Workflow

Intelligent development assistance workflow for Cairo smart contracts using domain-specific expertise and conservative validation.

## Usage

```bash
@claude cairo-dev-assist "<development_query>"
```

## Sub-commands

- `@claude cairo-dev-assist "query"`: General development assistance
- `@claude cairo-dev-assist "query" --pattern`: Show implementation patterns and examples
- `@claude cairo-dev-assist "query" --optimize`: Focus on gas optimization and performance
- `@claude cairo-dev-assist "query" --test`: Include testing strategies and examples

## Examples

```bash
# General development guidance
@claude cairo-dev-assist "How do I implement a constructor with multiple parameters?"

# Pattern-focused assistance with code examples
@claude cairo-dev-assist "Best practices for storage management" --pattern

# Gas optimization guidance
@claude cairo-dev-assist "Optimize my trading position calculations" --optimize

# Testing strategy assistance
@claude cairo-dev-assist "How to test contract upgrades safely" --test
```

## Workflow Stages

### Stage 1: Context Gathering & Requirements Analysis
**Purpose**: Understand existing codebase context and specific development needs
**Adapts**: Comprehensive Workflow + Research Framework

**Context Analysis**:
- **Existing Contract Structure**: Parse current contract architecture
- **Domain Patterns**: Identify AstraTrade-specific patterns (trading, gamification, etc.)
- **Dependency Mapping**: Analyze contract imports and inheritance chains
- **Interface Contracts**: Map external dependencies and integrations

**Requirements Extraction**:
- **Functional Requirements**: What specific functionality is needed
- **Non-Functional Requirements**: Performance, gas limits, security constraints
- **Integration Requirements**: How new code fits with existing system
- **Testing Requirements**: Unit, integration, and scenario testing needs

**Actions**:
- Scan existing contracts for established patterns
- Identify reusable components and libraries
- Map domain-specific terminology and concepts
- Extract current gas optimization strategies

**Outputs**:
- `artifacts/context_analysis.md`: Current codebase understanding
- `artifacts/dev_requirements.md`: Specific development needs
- `artifacts/pattern_inventory.md`: Reusable patterns and components

### Stage 2: Conservative Design Validation
**Purpose**: Validate proposed changes against Cairo best practices with safety checks
**Adapts**: Lean Hypothesis + Conservative Validation

**Design Validation Checklist**:

**Interface Compatibility**:
- [ ] No breaking changes to existing function signatures
- [ ] Backward compatibility with existing integrations
- [ ] Event schema compatibility maintained
- [ ] Storage layout changes don't break existing data

**Security Implications**:
- [ ] No new attack vectors introduced
- [ ] Access control patterns maintained
- [ ] State transition safety preserved
- [ ] Reentrancy protection considerations

**Gas Optimization**:
- [ ] Storage operations minimized
- [ ] Batch operations where possible
- [ ] Efficient data structures chosen
- [ ] Loop bounds validated

**Testing Feasibility**:
- [ ] Unit testing approach defined
- [ ] Integration testing strategy clear
- [ ] Edge cases identified
- [ ] Performance benchmarking plan

**Conservative Validation Rules**:
- 95% confidence threshold for design recommendations
- Mandatory clarification for vague or broad requests
- Minimal change principle - suggest smallest viable implementation
- Explicit approval gates for significant architectural changes

**Actions**:
- Validate against Cairo language best practices
- Check compatibility with existing AstraTrade contracts
- Estimate gas costs and optimization opportunities
- Generate alternative implementation approaches

**Outputs**:
- `artifacts/design_validation.md`: Safety and compatibility analysis
- `artifacts/alternatives.md`: Multiple implementation options
- `artifacts/risk_assessment.md`: Implementation risks and mitigations

### Stage 3: Implementation Guidance & Code Generation
**Purpose**: Provide specific, actionable development guidance with examples
**Adapts**: Testing Strategies + Property-Based patterns

**Implementation Categories**:

**Core Contract Patterns**:
```cairo
// Constructor patterns
#[constructor]
fn constructor(ref self: ContractState, param1: type1, param2: type2) {
    // Validation and initialization
}

// Storage patterns
#[storage]
struct Storage {
    // Optimized storage layout
}

// Function patterns with access control
#[external(v0)]
fn secure_function(ref self: ContractState) {
    self._assert_only_owner();
    // Implementation
}
```

**State Management Patterns**:
- Storage optimization techniques
- Batch update patterns
- Event emission best practices
- State transition validation

**Integration Patterns**:
- External contract calls
- Oracle integration
- Cross-contract communication
- Error handling strategies

**Testing Patterns**:
- Unit test structure and mocking
- Integration test scenarios
- Property-based test cases
- Gas benchmarking tests

**Actions**:
- Generate specific code examples tailored to the request
- Provide step-by-step implementation guidance
- Include comprehensive testing strategies
- Suggest gas optimization techniques

**Outputs**:
- `artifacts/implementation_guide.md`: Step-by-step development plan
- `artifacts/code_examples.md`: Specific Cairo code patterns
- `artifacts/testing_strategy.md`: Comprehensive testing approach
- `artifacts/optimization_tips.md`: Gas and performance recommendations

## Development Best Practices Integration

### Cairo Language Best Practices
- **Type Safety**: Use appropriate felt252, u256, ContractAddress types
- **Storage Efficiency**: Minimize storage operations, use packed structs
- **Error Handling**: Consistent error messages and proper assert usage
- **Documentation**: Comprehensive NatSpec comments
- **Modularity**: Proper separation of concerns and reusable components

### AstraTrade-Specific Patterns
- **Gamification Integration**: XP awards, achievement unlocking, streak tracking
- **Trading Logic**: Position management, liquidation calculations, fee handling
- **Access Control**: Owner patterns, user verification, role-based permissions
- **Event Emission**: Comprehensive events for Flutter UI integration
- **Gas Optimization**: Mobile-optimized operations under 100k gas

### Testing Strategy Integration
- **Unit Tests**: Core business logic validation
- **Integration Tests**: Cross-contract interaction testing
- **Scenario Tests**: End-to-end user workflow validation
- **Property Tests**: Invariant checking and edge case discovery
- **Gas Tests**: Performance benchmarking and optimization validation

## Conservative Safety Features

### Query Validation
```
❌ Vague Query: "improve my contract"
✅ Specific Query: "add reentrancy protection to my close_position function"

❌ Broad Scope: "optimize everything"
✅ Focused Scope: "optimize storage layout for User struct"
```

### Confidence Scoring
- **High Confidence (95%+)**: Established patterns with proven implementations
- **Medium Confidence (75-94%)**: Good practices requiring some customization
- **Low Confidence (<75%)**: Experimental approaches needing careful validation

### Clarification System
When queries are unclear, the system provides:
- Specific questions to clarify requirements
- Example queries for better results
- Alternative approaches to consider
- Implementation complexity estimates

## Sample Output

```
🔧 Cairo Development Assistant: Storage Optimization
==================================================

📊 Analysis Results:
   - Query Type: Storage optimization
   - Confidence: 92%
   - Complexity: Medium
   - Estimated Time: 2-3 days

💡 RECOMMENDED APPROACH:
   Primary: Pack User struct fields for gas efficiency
   - Combine boolean flags into bitmask (saves 3 storage slots)
   - Optimize address + small int packing
   - Implement getter functions for unpacked access

📝 IMPLEMENTATION STEPS:
   1. Backup current User struct definition
   2. Implement PackedUser with optimized layout
   3. Add helper functions for pack/unpack operations
   4. Update all contract functions to use new format
   5. Add migration function for existing data

🧪 TESTING STRATEGY:
   - Unit tests for pack/unpack functions
   - Migration tests with sample data
   - Gas comparison tests (before/after)
   - Integration tests with all User operations

⚡ GAS SAVINGS: Estimated 15-20% reduction in user operations
```

## Implementation

This workflow executes through the enhanced GRAPH-R1 CLI:

```bash
source venv/bin/activate
python graph_r1/graph_r1_cli.py dev-assist "{{query}}" {{options}}
```

The workflow leverages:
- Cairo Expert Development Agent for specialized guidance
- Knowledge graph for contextual code understanding
- Conservative validation with clarity requirements
- Pattern matching against established Cairo best practices