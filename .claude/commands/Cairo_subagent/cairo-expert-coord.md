# Cairo Expert Coordination Workflow

Intelligent multi-expert coordination workflow for complex Cairo development tasks requiring collaboration between specialized agents.

## Usage

```bash
@claude cairo-expert-coord "<complex_query>"
```

## Sub-commands

- `@claude cairo-expert-coord "query"`: Auto-route to best expert with confidence scoring
- `@claude cairo-expert-coord "query" --collaborative`: Multi-expert analysis and synthesis
- `@claude cairo-expert-coord "query" --consensus`: Require expert consensus for recommendations
- `@claude cairo-expert-coord "query" --validate`: Conservative validation with clarification requests

## Examples

```bash
# Auto-route to most appropriate expert
@claude cairo-expert-coord "How to implement secure access control with gas optimization?"

# Multi-expert collaborative analysis
@claude cairo-expert-coord "Design a contract upgrade mechanism" --collaborative

# Consensus-based recommendations for critical decisions
@claude cairo-expert-coord "Should we refactor the trading engine?" --consensus

# Conservative validation with clarification
@claude cairo-expert-coord "improve security" --validate
```

## Workflow Stages

### Stage 1: Query Classification & Expert Routing
**Purpose**: Intelligent query analysis and optimal expert agent selection
**Adapts**: Research Framework + HRM Analysis + Conservative Validation

**Query Analysis Process**:

**Intent Classification**:
```
Query Types:
- DEVELOPMENT: Implementation, patterns, best practices
- SECURITY: Vulnerabilities, audit, attack vectors
- ARCHITECTURE: Design patterns, system structure
- REFACTORING: Code improvement, optimization
- REVIEW: Quality assessment, code analysis
- OPTIMIZATION: Gas efficiency, performance
```

**Complexity Assessment**:
```
Complexity Scoring:
- Simple (0-30): Single expert, straightforward answer
- Medium (31-70): Possible multi-expert, some context needed
- Complex (71-90): Multi-expert recommended, significant context
- Critical (91-100): Mandatory multi-expert, high stakes
```

**Expert Confidence Scoring**:
```python
def calculate_expert_confidence(query: str, expert_type: str) -> float:
    """Conservative confidence calculation"""
    # Keyword matching with domain expertise
    keyword_score = match_expertise_keywords(query, expert_type)
    
    # Query clarity and specificity
    clarity_score = assess_query_clarity(query) 
    
    # Domain context relevance
    context_score = evaluate_domain_context(query, expert_type)
    
    # Conservative weighting (prevents overconfidence)
    return min(0.95, (keyword_score * 0.4 + clarity_score * 0.3 + context_score * 0.3))
```

**Routing Decision Logic**:
- **High Confidence (90%+)**: Single expert assignment
- **Medium Confidence (70-89%)**: Primary expert with secondary consultation
- **Low Confidence (50-69%)**: Multi-expert collaboration required
- **Very Low Confidence (<50%)**: Clarification request or reject

**Actions**:
- Parse query for intent, complexity, and domain keywords
- Calculate confidence scores for each available expert agent
- Determine optimal routing strategy (single, multi, or clarification)
- Generate routing explanation with confidence justification

**Outputs**:
- `artifacts/query_analysis.md`: Intent classification and complexity assessment
- `artifacts/routing_decision.md`: Expert selection with confidence scores
- `artifacts/context_extraction.md`: Relevant domain context and requirements

### Stage 2: Collaborative Expert Analysis
**Purpose**: Coordinate multiple expert agents for comprehensive analysis and synthesis
**Adapts**: Comprehensive Workflow + Research Framework + Collaborative patterns

**Multi-Expert Coordination Strategies**:

**Parallel Analysis Pattern**:
```
Security Expert    Development Expert    Architecture Expert
      ↓                    ↓                     ↓
Security Analysis    Implementation    System Design
      ↓                    ↓                     ↓
        ↘                  ↓                   ↙
          → Synthesis Agent (Coordinator) ←
                           ↓
            Unified Recommendation
```

**Sequential Analysis Pattern**:
```
Architecture Expert → Development Expert → Security Expert → Coordinator
(Design Framework)   (Implementation)    (Security Review)   (Integration)
```

**Consensus Building Process**:
1. **Independent Analysis**: Each expert provides assessment without seeing others
2. **Conflict Identification**: Coordinator identifies disagreements or contradictions
3. **Evidence Review**: Present conflicting viewpoints with supporting evidence
4. **Consensus Negotiation**: Facilitate discussion between expert viewpoints
5. **Final Recommendation**: Synthesized solution with confidence scoring

**Expert Interaction Protocols**:

**Information Sharing**:
- Each expert maintains independent analysis initially
- Shared context: code snippets, requirements, domain knowledge
- Conflict resolution through evidence-based discussion

**Quality Assurance**:
- Cross-validation of recommendations between experts
- Confidence scoring aggregation with conservative weighting
- Dissenting opinion documentation for transparency

**Actions**:
- Coordinate parallel or sequential expert consultation
- Facilitate information sharing while maintaining independence
- Identify and resolve conflicts between expert recommendations
- Synthesize multiple perspectives into coherent recommendations

**Outputs**:
- `artifacts/expert_analyses.md`: Individual expert assessments
- `artifacts/conflict_resolution.md`: Disagreement analysis and resolution
- `artifacts/synthesis.md`: Unified recommendations with confidence scoring

### Stage 3: Conservative Validation & Quality Assurance
**Purpose**: Apply conservative validation gates and ensure recommendation quality
**Adapts**: Conservative Validation + HRM Contextual Analysis + Quality Gates

**Validation Gate Categories**:

**Query Clarity Validation**:
```
Clarity Assessment Checklist:
- [ ] Specific scope and boundaries defined
- [ ] Clear success criteria provided
- [ ] Context and constraints specified
- [ ] Implementation timeline indicated
- [ ] Risk tolerance communicated
```

**Recommendation Confidence Validation**:
```
Confidence Thresholds:
- Implementation Changes: 95%+ confidence required
- Architectural Decisions: 90%+ confidence required
- Security Recommendations: 95%+ confidence required
- Optimization Suggestions: 85%+ confidence required
- Analysis-Only Responses: 75%+ confidence required
```

**Conservative Response Patterns**:

**High Confidence Response**:
```
✅ RECOMMENDATION (96% confidence):
Primary approach: [Specific recommendation]
Implementation: [Step-by-step guidance]
Risks: [Identified and mitigated]
Alternatives: [Other viable options]
```

**Medium Confidence Response**:
```
⚠️ ANALYSIS WITH CAVEATS (78% confidence):
Likely approach: [Best current understanding]
Assumptions: [Key assumptions made]
Validation needed: [Additional information required]
Alternative paths: [Other options to consider]
```

**Low Confidence Response**:
```
❓ CLARIFICATION REQUIRED (<75% confidence):
Current understanding: [What we think you're asking]
Missing information: [What we need to know]
Suggested clarifications: [Specific questions]
Partial guidance: [What we can help with now]
```

**Quality Assurance Processes**:

**Recommendation Validation**:
- Evidence-based justification for all suggestions
- Risk assessment with mitigation strategies
- Alternative approach consideration
- Implementation complexity estimation

**Conflict Resolution Documentation**:
- Record of expert disagreements and resolution process
- Evidence evaluation and decision rationale
- Dissenting opinions and their consideration
- Final recommendation justification

**Actions**:
- Apply conservative confidence thresholds to all recommendations
- Validate query clarity and request clarification when needed
- Document conflict resolution process and expert consensus
- Ensure all recommendations meet quality and safety standards

**Outputs**:
- `artifacts/validation_report.md`: Quality assurance assessment
- `artifacts/confidence_scoring.md`: Detailed confidence analysis
- `artifacts/clarification_requests.md`: Questions for unclear queries

## Expert Agent Specializations

### Cairo Development Expert
- **Expertise**: Contract implementation, design patterns, best practices
- **Strengths**: Code generation, optimization, testing strategies
- **Focus Areas**: Function design, storage patterns, gas optimization

### Cairo Security Expert  
- **Expertise**: Vulnerability analysis, attack vectors, security patterns
- **Strengths**: Threat modeling, audit procedures, risk assessment
- **Focus Areas**: Access control, reentrancy, arithmetic safety

### Cairo Architecture Expert
- **Expertise**: System design, contract interaction, upgrade patterns
- **Strengths**: High-level design, integration patterns, scalability
- **Focus Areas**: Contract composition, proxy patterns, modularity

### Coordination Intelligence
- **Meta-Expertise**: Expert selection, conflict resolution, synthesis
- **Strengths**: Multi-perspective analysis, consensus building
- **Focus Areas**: Complex decision-making, quality assurance

## Conservative Safety Features

### Clarity Requirements
```
❌ Vague Query: "help with my contract"
✅ Clear Query: "add reentrancy protection to my close_position function in exchange.cairo"

❌ Broad Scope: "make everything better"  
✅ Specific Scope: "optimize gas usage in User struct storage operations"
```

### Confidence Thresholds
- **Code Changes**: 95% confidence minimum
- **Architecture Decisions**: 90% confidence minimum  
- **Analysis Only**: 75% confidence minimum
- **Clarification Required**: <75% confidence

### Validation Checkpoints
- All recommendations require evidence-based justification
- Conflicting expert opinions must be resolved with documentation
- High-risk suggestions require explicit approval acknowledgment
- Alternative approaches must be considered and presented

## Sample Output

```
🤖 Cairo Expert Coordination: Access Control Implementation
=========================================================

📊 Query Analysis:
   - Intent: DEVELOPMENT + SECURITY (hybrid query)
   - Complexity: 73/100 (Complex - multi-expert recommended)
   - Domain Context: AstraTrade trading contract access patterns

🎯 EXPERT ROUTING:
   Primary: Development Expert (87% confidence)
   Secondary: Security Expert (91% confidence)
   Coordination: Multi-expert collaborative analysis

👥 COLLABORATIVE ANALYSIS:
   
   🔧 Development Expert Input:
   - Recommends role-based access control pattern
   - Suggests Ownable + AccessControl combination
   - Confidence: 89%
   
   🛡️ Security Expert Input:
   - Validates access control security patterns
   - Identifies potential privilege escalation risks
   - Confidence: 93%
   
   🏗️ Architecture Expert Input:
   - Evaluates integration with existing AstraTrade patterns  
   - Recommends upgrade-safe implementation approach
   - Confidence: 85%

✅ SYNTHESIZED RECOMMENDATION (91% confidence):
   
   Implementation Approach:
   1. Implement OpenZeppelin-style AccessControl pattern
   2. Add role hierarchy for admin/trader/viewer permissions
   3. Include emergency pause mechanism with time-lock
   4. Maintain compatibility with existing owner patterns
   
   Security Considerations:
   - Multi-signature requirement for admin role changes
   - Time-delayed privilege modifications
   - Comprehensive access event logging
   
   Implementation Timeline: 3-4 days
   Risk Level: MEDIUM (existing patterns, well-tested approach)
   
🔍 EXPERT CONSENSUS: All experts agree on core approach
   Minor disagreement on time-lock duration (resolved: 24 hours)
```

## Implementation

### UMAS-Enhanced Expert Coordination

This workflow now executes through the Ultimate Multi-Agent System (UMAS) for enhanced performance and reliability:

```bash
# Start UMAS with Cairo experts
@claude cairo-umas-start --agents 5 --experts security,development,architecture

# Execute expert coordination with UMAS
@claude cairo-umas-execute expert_coordination --query "{{query}}" --mode {{mode}}

# Alternative: Direct UMAS integration
python -c "
from Cairo_subagent.umas_integration import get_cairo_umas_integration
import asyncio

async def coordinate_experts():
    integration = get_cairo_umas_integration()
    await integration.initialize()
    result = await integration.system.execute_workflow('cairo_expert_coordination', {
        'query': '{{query}}',
        'mode': '{{mode}}'
    })
    print(result)

asyncio.run(coordinate_experts())
"
```

### Legacy Implementation (Fallback)

If UMAS is unavailable, falls back to GRAPH-R1 CLI:

```bash
source venv/bin/activate
python graph_r1/graph_r1_cli.py expert-coord "{{query}}" {{options}}
```

## UMAS Enhancements

The UMAS-powered workflow provides:

### Enterprise Features
- **Parallel Agent Processing**: Multiple experts analyze simultaneously
- **Intelligent Caching**: Cached responses for similar queries (80% faster)
- **Real-time Monitoring**: WebSocket updates on expert analysis progress
- **Load Balancing**: Optimal agent assignment based on capability and load
- **Fault Tolerance**: Automatic recovery from agent failures

### Performance Improvements
- **60% faster analysis** through parallel expert consultation  
- **Intelligent agent routing** based on query complexity and intent
- **Confidence scoring aggregation** from multiple expert perspectives
- **Automated consensus building** with conflict resolution

### Quality Assurance
- Multi-agent validation with confidence thresholds
- Conservative validation with clarification requests  
- Consensus building and conflict resolution processes
- Quality assurance gates and evidence-based recommendations
- Comprehensive audit trails for all expert decisions

### Monitoring and Analytics
```bash
# Check UMAS system status
@claude cairo-umas-status

# View expert performance metrics
@claude cairo-umas-status --detailed --experts

# Monitor workflow execution
@claude cairo-umas-monitor --workflow expert_coordination
```