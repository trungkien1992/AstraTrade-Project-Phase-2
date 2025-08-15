# HRM Code Analysis

Analyze code using the Hierarchical Reasoning Model (HRM) for intelligent insights and recommendations.

## Usage

```bash
# Analyze a specific file
hrm-analyze <file_path>

# Deep impact analysis for large classes
hrm-analyze <file_path> --deep --class <class_name> --lines <line_count>

# Get reasoned recommendations
hrm-analyze <file_path> --recommend --class <class_name> --lines <line_count>

# Contextual analysis (understands when rules should apply)
hrm-analyze <file_path> --contextual --class <class_name> --lines <line_count>
```

## Examples

```bash
# Basic analysis
hrm-analyze apps/backend/domains/trading/services.py

# Deep impact analysis for concerning large class
hrm-analyze apps/backend/domains/nft/entities.py --deep --class GenesisNFT --lines 330

# Get intelligent recommendations with reasoning
hrm-analyze apps/backend/domains/gamification/services.py --recommend --class GamificationDomainService --lines 461

# Contextual analysis that reasons about rule exceptions
hrm-analyze apps/backend/domains/financial/entities.py --contextual --class Account --lines 250
```

## What It Does

### Basic Analysis (`hrm-analyze <file>`)
- **Pattern Detection**: Identifies design patterns, architectural patterns
- **Quality Metrics**: Type hints, documentation, error handling coverage
- **Complexity Scoring**: Quantified complexity assessment (0-100)
- **Domain Awareness**: Recognizes AstraTrade-specific concepts
- **Issue Detection**: Finds potential problems with confidence levels

### Deep Impact Analysis (`--deep`)
- **Root Cause Analysis**: Why issues exist and how they developed
- **Multi-Dimensional Impact**: Business, technical, collaboration, testing impacts
- **Cost Estimation**: Maintenance costs, refactoring effort in person-days
- **Risk Assessment**: Immediate, short-term, and long-term risks
- **Timeline Analysis**: When impacts will affect development

### Reasoned Recommendations (`--recommend`)
- **Contextual Reasoning**: WHY each recommendation makes sense
- **Multi-Criteria Scoring**: Business value, feasibility, risk assessment
- **Implementation Guidance**: Specific steps, sequencing, prerequisites
- **Resource Planning**: Time estimates, skill requirements, success probability
- **Alternative Analysis**: Multiple options with trade-off comparison

### Contextual Analysis (`--contextual`)
- **Rule Exception Reasoning**: When large classes are acceptable vs concerning
- **Architectural Justification**: Domain services, consolidation patterns
- **Business Context**: Critical vs non-critical functionality
- **Risk-Benefit Analysis**: When technical debt is justified

## Sample Output

```
🧠 HRM Analysis: GenesisNFT (365 lines)
============================================================

📊 Analysis Results:
   - Complexity Score: 45.2/100
   - Patterns Detected: 6 (Value Object, Domain Entity, etc.)
   - Issues Found: 1 
   - Confidence: 95.3%

🎯 DEEP IMPACT ASSESSMENT (--deep):
   - Concern Level: MEDIUM
   - Priority Score: 65/100
   - Business Risk: Revenue-critical NFT functionality
   - Maintenance Cost: $15K annual overhead

💡 REASONED RECOMMENDATIONS (--recommend):
   🏆 PRIMARY: Extract Value Objects (85% confidence)
   WHY: NFT entities have rich metadata forming natural boundaries
   IMPLEMENTATION: Start with NFTMetadata, NFTAttributes, NFTRoyalty
   TIMELINE: 1-2 weeks for 30% size reduction

🧠 CONTEXTUAL REASONING (--contextual):
   ✅ Recent refactoring detected - class was simplified
   ✅ Value objects already extracted (metadata, attributes, royalty)
   ✅ Business logic moved to domain services  
   VERDICT: ACCEPTABLE - Proper entity design with extracted concerns
```

## Integration with Development Workflow

- **Before Refactoring**: Use `--deep` to understand full impact
- **Architecture Decisions**: Use `--recommend` for guidance with reasoning
- **Code Reviews**: Use basic analysis for objective quality assessment
- **Technical Debt**: Use `--contextual` to prioritize what actually needs attention

The HRM system provides intelligent, context-aware analysis that goes beyond simple rule checking to understand the WHY behind code quality decisions.