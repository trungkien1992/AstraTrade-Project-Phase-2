# Cairo Security Audit Workflow

Comprehensive security analysis workflow for Cairo smart contracts using the GRAPH-R1 Cairo expert system.

## Usage

```bash
@claude cairo-security-audit <contract_path_or_project>
```

## Sub-commands

- `@claude cairo-security-audit <path>`: Full security audit
- `@claude cairo-security-audit <path> --deep`: Deep vulnerability analysis with impact scoring
- `@claude cairo-security-audit <path> --critical-only`: Focus on critical security patterns only
- `@claude cairo-security-audit <path> --remediation`: Generate remediation plan with priority ranking

## Examples

```bash
# Full security audit of specific contract
@claude cairo-security-audit src/contracts/exchange.cairo

# Deep analysis with business impact scoring
@claude cairo-security-audit src/contracts/ --deep

# Critical vulnerabilities only (access control, reentrancy, arithmetic)
@claude cairo-security-audit apps/backend/contracts --critical-only

# Generate prioritized remediation roadmap
@claude cairo-security-audit . --remediation
```

## Workflow Stages

### Stage 1: Contract Discovery & Risk Profiling
**Purpose**: Identify Cairo contracts and establish baseline risk assessment
**Adapts**: HRM Analysis + Research Framework

**Actions**:
- Scan for `.cairo` files using pattern matching
- Parse contract structure and identify:
  - Entry points (external/internal functions)
  - Storage variables and access patterns
  - Event emissions and data flows
  - Import dependencies and external calls
- Apply HRM-style complexity scoring:
  - Function complexity (cyclomatic complexity)
  - Storage complexity (nested mappings, struct depth)
  - Interface complexity (number of external functions)
- Generate initial risk profile with confidence scoring

**Outputs**:
- `artifacts/contract_inventory.md`: Complete contract mapping
- `artifacts/complexity_analysis.md`: HRM-style complexity scores
- `artifacts/risk_profile.md`: Initial security risk assessment

### Stage 2: Deep Security Pattern Analysis
**Purpose**: Systematic vulnerability detection using Cairo-specific patterns
**Adapts**: Risk-Based Testing + Property-Based Testing concepts

**Security Pattern Categories**:

**Access Control Patterns**:
- Owner/admin privilege escalation
- Function visibility modifiers
- Role-based access control implementation
- Multi-signature requirements

**State Management Patterns**:
- Storage collision vulnerabilities
- State transition validation
- Initialization security
- Emergency pause mechanisms

**Arithmetic & Logic Patterns**:
- Integer overflow/underflow protection
- Division by zero checks
- Precision loss in calculations
- Rounding error accumulation

**Integration Patterns**:
- External contract call safety
- Oracle data validation
- Cross-contract reentrancy
- Event emission completeness

**Gas & Performance Patterns**:
- Unbounded loops and gas exhaustion
- Storage optimization patterns
- Batch operation efficiency

**Actions**:
- Pattern-based vulnerability scanning
- CEI (Checks-Effects-Interactions) pattern validation
- State invariant verification
- Cross-reference with OWASP Smart Contract Security Top 10

**Outputs**:
- `artifacts/vulnerability_scan.md`: Detailed findings with line numbers
- `artifacts/pattern_analysis.md`: Security pattern compliance
- `artifacts/invariant_violations.md`: State consistency issues

### Stage 3: Contextual Risk Assessment & Prioritization
**Purpose**: Business-context risk scoring with conservative validation
**Adapts**: HRM Contextual Analysis + Conservative Validation

**Risk Factors**:
- **Business Impact**: Revenue-critical vs non-critical functions
- **Attack Vector Complexity**: Simple vs sophisticated attacks
- **Exploitability**: Immediate vs conditional vulnerabilities
- **Asset Value**: Funds at risk, user data exposure
- **Network Effects**: Impact on ecosystem or other contracts

**Conservative Validation**:
- 95% confidence threshold for vulnerability classification
- Expert agent consensus for medium/high risk findings
- Mandatory clarification for ambiguous security patterns
- Evidence-based risk scoring with audit trail

**Actions**:
- Calculate composite risk scores (Impact × Likelihood × Exploitability)
- Generate prioritized remediation roadmap
- Estimate fix complexity and security debt
- Create monitoring and detection recommendations

**Outputs**:
- `artifacts/risk_assessment.md`: Quantified risk matrix
- `artifacts/remediation_plan.md`: Prioritized action items
- `artifacts/monitoring_recommendations.md`: Detection strategies

## Security Checklist Integration

### Critical Security Patterns (Must-Have)
- [ ] Owner/admin access control with multi-sig
- [ ] Reentrancy protection on state-changing functions
- [ ] Integer overflow/underflow protection
- [ ] Emergency pause mechanism
- [ ] Input validation on all external functions

### Advanced Security Patterns (Should-Have)
- [ ] Time-lock for critical operations
- [ ] Rate limiting for high-risk functions
- [ ] Oracle failure handling
- [ ] Cross-contract call validation
- [ ] Event emission for all state changes

### Optimization Patterns (Nice-to-Have)
- [ ] Gas-efficient storage patterns
- [ ] Batch operations for multiple updates
- [ ] Storage collision prevention
- [ ] Upgrade mechanism security

## Conservative Safety Features

### Confidence Scoring
- **High Confidence (95%+)**: Clear vulnerability with reproducible exploit
- **Medium Confidence (75-94%)**: Likely issue requiring additional context
- **Low Confidence (<75%)**: Potential concern requiring manual review

### Validation Gates
- Unclear security queries trigger clarification requests
- Analysis-only mode by default (no automatic fixes)
- Explicit approval required for remediation suggestions
- Minimal change principle for security improvements

### Expert Agent Integration
- Security-focused agent provides specialized analysis
- Development agent validates proposed fixes
- Coordinator agent synthesizes multi-perspective analysis

## Sample Output

```
🔒 Cairo Security Audit: AstraTradeExchangeV2
================================================================

📊 Security Analysis Results:
   - Contracts Analyzed: 1
   - Functions Scanned: 23
   - Critical Issues: 2
   - High Priority: 1
   - Medium Priority: 3
   - Security Score: 72/100

🚨 CRITICAL FINDINGS:
   1. Missing reentrancy protection in close_position() [Line 441]
      Impact: HIGH | Exploitability: MEDIUM | Confidence: 96%
      
   2. Integer overflow in liquidation calculation [Line 744]
      Impact: CRITICAL | Exploitability: HIGH | Confidence: 89%

💡 REMEDIATION ROADMAP:
   🏆 PRIORITY 1: Add reentrancy guard (2-3 days, High confidence)
   🔧 PRIORITY 2: Implement SafeMath patterns (1-2 days, High confidence)
   📊 PRIORITY 3: Enhance input validation (3-5 days, Medium confidence)

🛡️ MONITORING RECOMMENDATIONS:
   - Add position manipulation alerts
   - Monitor large liquidation events
   - Track unusual trading patterns
```

## Implementation

This workflow executes through the enhanced GRAPH-R1 CLI:

```bash
source venv/bin/activate
python graph_r1/graph_r1_cli.py security-audit {{target_path}} {{options}}
```

The workflow leverages:
- Cairo Expert Security Agent for specialized analysis
- Knowledge graph for contextual understanding
- Conservative validation with high confidence thresholds
- HRM-inspired impact and complexity analysis