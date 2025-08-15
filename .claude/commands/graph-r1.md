# Graph-R1 Tool (Cairo-Enhanced)

This command provides an interface to the enhanced GRAPH-R1 tool with comprehensive Cairo language knowledge and AstraTrade codebase analysis.

## Usage

`@claude graph-r1 <sub-command>`

## Sub-commands

*   `init`: Analyzes AstraTrade codebase and builds enhanced knowledge graph with Cairo expertise.
*   `demo`: Runs the Cairo-aware agent functionality demonstration.
*   `evaluate`: Runs the agent evaluation.
*   `query`: Interactive knowledge graph query interface.
    *   `query --type arch`: Show architecture overview  
    *   `query --type rel`: Show relationships
    *   `query --type domain --target <name>`: Query specific domain
*   `audit`: Cairo smart contract security audit.
    *   `audit --target <path>`: Audit specific contracts or project
*   `expert`: Consult specialized Cairo expert agents.
    *   `expert --domain development "query"`: Development guidance
    *   `expert --domain security "query"`: Security analysis  
    *   `expert --domain auto "query"`: Auto-route to best expert
    *   `expert --collaborative "query"`: Multi-expert analysis
*   `security-audit`: Comprehensive Cairo security audit workflow.
    *   `security-audit <path>`: Full security audit
    *   `security-audit <path> --deep`: Deep vulnerability analysis
    *   `security-audit <path> --critical-only`: Critical patterns only
    *   `security-audit <path> --remediation`: Generate remediation plan
*   `dev-assist`: Cairo development assistant workflow.
    *   `dev-assist "query"`: General development assistance
    *   `dev-assist "query" --pattern`: Show patterns and examples
    *   `dev-assist "query" --optimize`: Focus on gas optimization
    *   `dev-assist "query" --test`: Include testing strategies
*   `contract-review`: Comprehensive Cairo contract review workflow.
    *   `contract-review <path>`: Full contract review
    *   `contract-review <path> --architecture`: Architectural focus
    *   `contract-review <path> --quality`: Code quality analysis
    *   `contract-review <path> --performance`: Performance review
*   `refactor`: Safe Cairo refactoring workflow with impact analysis.
    *   `refactor "request"`: Full refactoring analysis
    *   `refactor "request" --impact`: Impact analysis only
    *   `refactor "request" --incremental`: Step-by-step guide
    *   `refactor "request" --rollback`: Rollback strategies
*   `expert-coord`: Multi-expert coordination for complex queries.
    *   `expert-coord "query"`: Auto-coordinate expert analysis
    *   `expert-coord "query" --collaborative`: Multi-expert synthesis
    *   `expert-coord "query" --consensus`: Require expert consensus
    *   `expert-coord "query" --validate`: Conservative validation

## Examples

`@claude graph-r1 init`
`@claude graph-r1 demo`  
`@claude graph-r1 query --type arch`
`@claude graph-r1 query --type domain --target trading`
`@claude graph-r1 audit --target src/contracts/`
`@claude graph-r1 expert --domain development "How to implement storage?"`
`@claude graph-r1 expert --domain security "What are access control risks?"`
`@claude graph-r1 expert --collaborative "How to audit Cairo contracts?"`
`@claude graph-r1 security-audit src/contracts/ --deep`
`@claude graph-r1 dev-assist "Optimize User struct storage" --pattern`
`@claude graph-r1 contract-review src/contracts/exchange.cairo --performance`
`@claude graph-r1 refactor "Extract trading logic functions" --incremental`
`@claude graph-r1 expert-coord "Design secure upgrade mechanism" --consensus`

## Cairo-Enhanced Features

- **Cairo Language Expertise**: Comprehensive knowledge of Cairo syntax, patterns, and best practices
- **Security Analysis**: Built-in Cairo contract security audit capabilities
- **Development Guidance**: Access control patterns, function types, storage management
- **Vulnerability Detection**: Automated security issue identification and recommendations
- **Architecture Integration**: Maps Cairo contracts to AstraTrade domain structure
- **Specialized Expert Agents**: Domain-specific sub-agents for development and security
- **Intelligent Routing**: Auto-routes queries to most appropriate expert
- **Collaborative Analysis**: Multi-expert consultation for complex queries
- **Conservative Validation**: 75% confidence threshold with clarification requests for unclear tasks
- **Specific Task Focus**: Requires detailed, specific queries and asks for clarification when unclear
- **Specialized Workflows**: Dedicated workflows for security audit, development assistance, contract review, refactoring, and expert coordination
- **Impact Analysis**: HRM-style deep analysis with business impact assessment and risk scoring
- **Incremental Implementation**: Step-by-step guidance with validation checkpoints and rollback strategies

## Cairo Knowledge Areas

- **Smart Contract Development**: Function types, storage, events, interfaces
- **Security Patterns**: Access control, input validation, CEI pattern, ownership system
- **Audit Checklist**: Architecture review, code quality, security checks, testing coverage
- **Starknet Integration**: System calls, fee optimization, deployment patterns
- **Development Tools**: Testing strategies, optimization techniques, library usage

## Implementation

This command executes the Cairo-enhanced `graph_r1_cli.py` script.

```bash
source venv/bin/activate
python graph_r1/graph_r1_cli.py {{command}}
```
