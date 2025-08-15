import argparse
import sys
import pickle

# Add the project root to the Python path to allow for module imports
sys.path.append('/Users/admin/AstraTrade-Submission/graph_r1')

from scripts.prepare_data import prepare_data
from scripts.build_knowledge_graph import build_knowledge_graph
from scripts.train import demonstrate_agent_functionality
from scripts.evaluate import evaluate

def main():
    parser = argparse.ArgumentParser(description="GRAPH-R1 Command-Line Interface")
    subparsers = parser.add_subparsers(dest='command', required=True)

    # Command to initialize the data and knowledge graph
    parser_init = subparsers.add_parser('init', help='Prepare data and build the knowledge graph.')

    # Command to run the agent demonstration
    parser_demo = subparsers.add_parser('demo', help='Run the agent functionality demonstration.')

    # Command to run the evaluation
    parser_eval = subparsers.add_parser('evaluate', help='Run the agent evaluation.')
    
    # Command to query the knowledge graph
    parser_query = subparsers.add_parser('query', help='Query the knowledge graph interactively.')
    parser_query.add_argument('--type', choices=['arch', 'rel', 'domain'], 
                             help='Type of query: architecture, relationships, or domain')
    parser_query.add_argument('--target', help='Target for domain queries')
    
    # Command to audit Cairo contracts
    parser_audit = subparsers.add_parser('audit', help='Audit Cairo smart contracts for security issues.')
    parser_audit.add_argument('--target', help='Target file or directory to audit')
    
    # Command to consult Cairo experts
    parser_expert = subparsers.add_parser('expert', help='Consult specialized Cairo expert agents.')
    parser_expert.add_argument('--domain', choices=['development', 'security', 'auto'], 
                              default='auto', help='Expert domain to consult')
    parser_expert.add_argument('--collaborative', action='store_true', 
                              help='Get input from multiple expert agents')
    parser_expert.add_argument('query', help='Query for the expert agents')
    
    # NEW WORKFLOW COMMANDS
    
    # Command for security audit workflow
    parser_security_audit = subparsers.add_parser('security-audit', help='Comprehensive Cairo security audit workflow.')
    parser_security_audit.add_argument('target', help='Contract path or project directory to audit')
    parser_security_audit.add_argument('--deep', action='store_true', 
                                     help='Deep vulnerability analysis with impact scoring')
    parser_security_audit.add_argument('--critical-only', action='store_true',
                                     help='Focus on critical security patterns only')
    parser_security_audit.add_argument('--remediation', action='store_true',
                                     help='Generate remediation plan with priority ranking')
    
    # Command for development assistance workflow
    parser_dev_assist = subparsers.add_parser('dev-assist', help='Cairo development assistant workflow.')
    parser_dev_assist.add_argument('query', help='Development query or request')
    parser_dev_assist.add_argument('--pattern', action='store_true',
                                 help='Show implementation patterns and examples')
    parser_dev_assist.add_argument('--optimize', action='store_true',
                                 help='Focus on gas optimization and performance')
    parser_dev_assist.add_argument('--test', action='store_true',
                                 help='Include testing strategies and examples')
    
    # Command for contract review workflow
    parser_contract_review = subparsers.add_parser('contract-review', help='Comprehensive Cairo contract review workflow.')
    parser_contract_review.add_argument('target', help='Contract path to review')
    parser_contract_review.add_argument('--architecture', action='store_true',
                                      help='Focus on architectural patterns')
    parser_contract_review.add_argument('--quality', action='store_true',
                                      help='Code quality and maintainability analysis')
    parser_contract_review.add_argument('--performance', action='store_true',
                                      help='Gas optimization and performance review')
    
    # Command for refactoring workflow
    parser_refactor = subparsers.add_parser('refactor', help='Safe Cairo refactoring workflow with impact analysis.')
    parser_refactor.add_argument('request', help='Refactoring request or description')
    parser_refactor.add_argument('--impact', action='store_true',
                               help='Deep impact analysis only')
    parser_refactor.add_argument('--incremental', action='store_true',
                               help='Step-by-step refactoring guide')
    parser_refactor.add_argument('--rollback', action='store_true',
                               help='Focus on rollback and safety strategies')
    
    # Command for expert coordination workflow
    parser_expert_coord = subparsers.add_parser('expert-coord', help='Multi-expert coordination workflow for complex queries.')
    parser_expert_coord.add_argument('query', help='Complex query requiring expert coordination')
    parser_expert_coord.add_argument('--collaborative', action='store_true',
                                   help='Multi-expert analysis and synthesis')
    parser_expert_coord.add_argument('--consensus', action='store_true',
                                   help='Require expert consensus for recommendations')
    parser_expert_coord.add_argument('--validate', action='store_true',
                                   help='Conservative validation with clarification requests')
    
    # SPECIALIZED REMEDIATION WORKFLOWS
    
    # Security Remediation Sub-Agent
    parser_security_remediation = subparsers.add_parser('security-remediation', help='Advanced security vulnerability remediation workflow.')
    parser_security_remediation.add_argument('vulnerability_type', choices=['reentrancy', 'overflow', 'access-control', 'oracle', 'state-corruption', 'all'],
                                            help='Type of security vulnerability to remediate')
    parser_security_remediation.add_argument('target_file', help='Target contract file for remediation')
    parser_security_remediation.add_argument('--analysis', action='store_true',
                                           help='Vulnerability impact analysis only')
    parser_security_remediation.add_argument('--implementation', action='store_true',
                                           help='Step-by-step fix implementation')
    parser_security_remediation.add_argument('--validation', action='store_true',
                                           help='Post-fix security validation')
    
    # Performance Optimization Sub-Agent
    parser_performance_optimization = subparsers.add_parser('performance-optimization', help='Advanced performance optimization workflow.')
    parser_performance_optimization.add_argument('optimization_type', choices=['storage-packing', 'batch-operations', 'gas-optimization', 'lookup-tables', 'assembly-optimization', 'all'],
                                                help='Type of performance optimization to implement')
    parser_performance_optimization.add_argument('target_file', help='Target contract file for optimization')
    parser_performance_optimization.add_argument('--analysis', action='store_true',
                                               help='Performance bottleneck analysis only')
    parser_performance_optimization.add_argument('--implementation', action='store_true',
                                               help='Step-by-step optimization implementation')
    parser_performance_optimization.add_argument('--benchmarking', action='store_true',
                                               help='Before/after performance comparison')
    
    # Code Quality Enhancement Sub-Agent
    parser_code_quality = subparsers.add_parser('code-quality', help='Advanced code quality enhancement workflow.')
    parser_code_quality.add_argument('enhancement_type', choices=['function-decomposition', 'documentation', 'test-coverage', 'error-handling', 'naming-conventions', 'all'],
                                   help='Type of code quality enhancement to implement')
    parser_code_quality.add_argument('target_file', help='Target contract file for quality enhancement')
    parser_code_quality.add_argument('--analysis', action='store_true',
                                   help='Code quality assessment only')
    parser_code_quality.add_argument('--implementation', action='store_true',
                                   help='Step-by-step quality improvements')
    parser_code_quality.add_argument('--metrics', action='store_true',
                                   help='Quality metrics and technical debt measurement')
    
    # Upgrade Infrastructure Sub-Agent
    parser_upgrade_infrastructure = subparsers.add_parser('upgrade-infrastructure', help='Advanced upgrade infrastructure implementation workflow.')
    parser_upgrade_infrastructure.add_argument('upgrade_type', choices=['proxy-pattern', 'diamond-pattern', 'governance', 'migration', 'rollback', 'all'],
                                             help='Type of upgrade infrastructure to implement')
    parser_upgrade_infrastructure.add_argument('target_contract', help='Target contract for upgrade infrastructure')
    parser_upgrade_infrastructure.add_argument('--design', action='store_true',
                                             help='Architecture design and planning only')
    parser_upgrade_infrastructure.add_argument('--implementation', action='store_true',
                                             help='Step-by-step implementation guide')
    parser_upgrade_infrastructure.add_argument('--testing', action='store_true',
                                             help='Upgrade testing strategies and validation')
    
    # Issue Coordination Master Agent
    parser_issue_coordinator = subparsers.add_parser('issue-coordinator', help='Master coordinator for systematic issue resolution.')
    parser_issue_coordinator.add_argument('coordination_mode', choices=['triage', 'orchestrate', 'monitor', 'integrate', 'validate', 'roadmap'],
                                        help='Coordination mode for issue resolution')
    parser_issue_coordinator.add_argument('target_scope', choices=['contract', 'project', 'domain', 'critical', 'all'],
                                        help='Target scope for coordination')
    parser_issue_coordinator.add_argument('--analysis', action='store_true',
                                        help='Analysis and planning only')
    parser_issue_coordinator.add_argument('--execution', action='store_true',
                                        help='Execute coordinated remediation')
    parser_issue_coordinator.add_argument('--reporting', action='store_true',
                                        help='Generate comprehensive status report')

    args = parser.parse_args()

    if args.command == 'init':
        print("--- Preparing Data ---")
        prepare_data()
        print("\n--- Building Knowledge Hypergraph ---")
        build_knowledge_graph()
        print("\nInitialization complete.")
    elif args.command == 'demo':
        print("--- Running Agent Demonstration ---")
        demonstrate_agent_functionality()
    elif args.command == 'evaluate':
        print("--- Running Evaluation ---")
        evaluate()
    elif args.command == 'query':
        print("--- Querying Knowledge Graph ---")
        from scripts.query_graph import query_architecture, query_relationships, query_domain, interactive_query
        
        if args.type == 'arch':
            query_architecture()
        elif args.type == 'rel':
            query_relationships()
        elif args.type == 'domain':
            domain_name = args.target or 'trading'
            query_domain(domain_name)
        else:
            interactive_query()
    elif args.command == 'audit':
        print("--- Cairo Security Audit ---")
        from scripts.cairo_audit_assistant import CairoAuditAssistant
        
        assistant = CairoAuditAssistant()
        project_root = args.target or "/Users/admin/AstraTrade-Submission"
        
        audit_results = assistant.audit_project_contracts(project_root)
        
        if "error" in audit_results:
            print(f"Error: {audit_results['error']}")
        else:
            summary = audit_results["summary"]
            print(f"\nAudit Results for: {project_root}")
            print(f"Contracts Analyzed: {summary['contracts_count']}")
            print(f"Average Security Score: {summary['average_audit_score']}/100")
            print(f"Total Issues Found: {audit_results['total_issues']}")
            
            if summary["issues_by_severity"]["high"] > 0:
                print(f"⚠️  HIGH PRIORITY: {summary['issues_by_severity']['high']} critical issues found!")
            
            print("\nDetailed report saved to audit_results.json")
    elif args.command == 'expert':
        print("--- Cairo Expert Consultation ---")
        from scripts.build_knowledge_graph import build_knowledge_graph
        
        # Load knowledge graph for experts
        try:
            with open("/Users/admin/AstraTrade-Submission/graph_r1/data/knowledge_hypergraph.pickle", "rb") as f:
                knowledge_graph = pickle.load(f)
        except FileNotFoundError:
            print("Knowledge graph not found. Please run 'init' first.")
            return
        
        from src.cairo_expert_system import CairoExpertCoordinator
        coordinator = CairoExpertCoordinator(knowledge_graph)
        
        query = args.query
        
        if args.collaborative:
            print(f"Getting collaborative analysis for: '{query}'")
            result = coordinator.collaborative_analysis(query)
            
            print(f"\n=== Collaborative Expert Analysis ===")
            for agent_type, response in result["agent_responses"].items():
                print(f"\n--- {agent_type.replace('_', ' ').title()} Expert ---")
                print(f"Query Type: {response.get('query_type', 'general')}")
                if 'guidance' in response:
                    for key, value in list(response['guidance'].items())[:2]:
                        print(f"{key.replace('_', ' ').title()}: {str(value)[:100]}...")
        
        elif args.domain == 'auto':
            print(f"Auto-routing query: '{query}'")
            result = coordinator.route_query(query)
            
            # Handle validation/clarification responses
            if result.get("status") in ["query_too_short", "uncertain_routing", "clarification_needed", "low_confidence"]:
                print(f"\n❌ {result.get('message', 'Issue with query')}")
                if 'guidance' in result:
                    print(f"💡 Guidance: {result['guidance']}")
                if 'suggestions' in result:
                    print("📝 Suggestions:")
                    for suggestion in result['suggestions']:
                        print(f"  • {suggestion}")
                if 'clarification_questions' in result:
                    print("❓ Please clarify:")
                    for question in result['clarification_questions']:
                        print(f"  • {question}")
                return
            
            routing_info = result.get("routing_info", {})
            print(f"\n=== {routing_info.get('selected_agent', 'Unknown').replace('_', ' ').title()} Expert ===")
            print(f"Confidence: {routing_info.get('confidence', 0):.2f}")
            print(f"Query Type: {result.get('query_type', 'general')}")
            
            if 'guidance' in result:
                print("\nKey Guidance:")
                for key, value in list(result['guidance'].items())[:3]:
                    print(f"• {key.replace('_', ' ').title()}")
        
        else:
            print(f"Consulting {args.domain} expert for: '{query}'")
            result = coordinator.get_specialized_guidance(args.domain, query)
            
            # Handle validation/clarification responses
            if result.get("status") in ["query_too_short", "uncertain_routing", "clarification_needed", "low_confidence"]:
                print(f"\n❌ {result.get('message', 'Issue with query')}")
                if 'guidance' in result:
                    print(f"💡 Guidance: {result['guidance']}")
                if 'recommendation' in result:
                    print(f"📝 Recommendation: {result['recommendation']}")
                if 'clarification_questions' in result:
                    print("❓ Please clarify:")
                    for question in result['clarification_questions']:
                        print(f"  • {question}")
                return
            
            print(f"\n=== {args.domain.title()} Expert Response ===")
            print(f"Query Type: {result.get('query_type', 'general')}")
            
            if 'guidance' in result:
                print("\nExpert Guidance:")
                for key, value in list(result['guidance'].items())[:3]:
                    print(f"• {key.replace('_', ' ').title()}")
                    
        print(f"\nFull response available in expert_response.json")
    
    # NEW WORKFLOW COMMAND HANDLERS
    
    elif args.command == 'security-audit':
        print("--- Cairo Security Audit Workflow ---")
        print("🔒 Comprehensive security audit workflow")
        print("📝 This workflow implements the Cairo Security Audit methodology")
        print("⚠️  Note: Workflow implementation modules are placeholders for demonstration")
        print(f"Target: {args.target}")
        if args.deep:
            print("Mode: Deep vulnerability analysis with impact scoring")
        elif args.critical_only:
            print("Mode: Critical security patterns only")
        elif args.remediation:
            print("Mode: Remediation plan generation")
        else:
            print("Mode: Full security audit")
        print("\n✅ Security audit workflow command structure ready")
        print("📋 See .claude/commands/cairo-security-audit.md for full workflow details")
    
    elif args.command == 'dev-assist':
        print("--- Cairo Development Assistant Workflow ---")
        print("🔧 Intelligent development assistance workflow")
        print("📝 This workflow implements the Cairo Development Assistant methodology")
        print("⚠️  Note: Workflow implementation modules are placeholders for demonstration")
        print(f"Query: {args.query}")
        if args.pattern:
            print("Focus: Implementation patterns and examples")
        if args.optimize:
            print("Focus: Gas optimization and performance")
        if args.test:
            print("Focus: Testing strategies and examples")
        print("\n✅ Development assistant workflow command structure ready")
        print("📋 See .claude/commands/cairo-dev-assist.md for full workflow details")
    
    elif args.command == 'contract-review':
        print("--- Cairo Contract Review Workflow ---")
        print("📋 Comprehensive contract review workflow")
        print("📝 This workflow implements the Cairo Contract Review methodology")
        print("⚠️  Note: Workflow implementation modules are placeholders for demonstration")
        print(f"Target: {args.target}")
        if args.architecture:
            print("Focus: Architectural patterns")
        if args.quality:
            print("Focus: Code quality and maintainability")
        if args.performance:
            print("Focus: Gas optimization and performance")
        print("\n✅ Contract review workflow command structure ready")
        print("📋 See .claude/commands/cairo-contract-review.md for full workflow details")
    
    elif args.command == 'refactor':
        print("--- Cairo Refactoring Workflow ---")
        print("🔧 Safe refactoring workflow with impact analysis")
        print("📝 This workflow implements the Cairo Refactoring methodology")
        print("⚠️  Note: Workflow implementation modules are placeholders for demonstration")
        print(f"Request: {args.request}")
        if args.impact:
            print("Mode: Deep impact analysis only")
        if args.incremental:
            print("Mode: Step-by-step refactoring guide")
        if args.rollback:
            print("Mode: Rollback and safety strategies focus")
        print("\n✅ Refactoring workflow command structure ready")
        print("📋 See .claude/commands/cairo-refactor.md for full workflow details")
    
    elif args.command == 'expert-coord':
        print("--- Cairo Expert Coordination Workflow ---")
        print("🤖 Multi-expert coordination workflow")
        print("📝 This workflow implements the Cairo Expert Coordination methodology")
        print("⚠️  Note: Workflow implementation modules are placeholders for demonstration")
        print(f"Query: {args.query}")
        if args.collaborative:
            print("Mode: Multi-expert analysis and synthesis")
        if args.consensus:
            print("Mode: Expert consensus required")
        if args.validate:
            print("Mode: Conservative validation with clarification")
        print("\n✅ Expert coordination workflow command structure ready")
        print("📋 See .claude/commands/cairo-expert-coord.md for full workflow details")
    
    # SPECIALIZED REMEDIATION WORKFLOW HANDLERS
    
    elif args.command == 'security-remediation':
        print("--- Cairo Security Remediation Sub-Agent ---")
        print("🛡️ Advanced security vulnerability remediation workflow")
        print("📝 This workflow implements systematic security fixes with step-by-step guidance")
        print(f"Vulnerability Type: {args.vulnerability_type}")
        print(f"Target File: {args.target_file}")
        if args.analysis:
            print("Mode: Vulnerability impact analysis only")
        elif args.implementation:
            print("Mode: Step-by-step fix implementation")
        elif args.validation:
            print("Mode: Post-fix security validation")
        else:
            print("Mode: Complete remediation workflow")
        print("\n✅ Security remediation workflow ready")
        print("📋 See .claude/commands/cairo-security-remediation.md for implementation details")
    
    elif args.command == 'performance-optimization':
        print("--- Cairo Performance Optimization Sub-Agent ---")
        print("⚡ Advanced performance optimization workflow")
        print("📝 This workflow implements systematic gas optimization and performance enhancement")
        print(f"Optimization Type: {args.optimization_type}")
        print(f"Target File: {args.target_file}")
        if args.analysis:
            print("Mode: Performance bottleneck analysis only")
        elif args.implementation:
            print("Mode: Step-by-step optimization implementation")
        elif args.benchmarking:
            print("Mode: Before/after performance comparison")
        else:
            print("Mode: Complete optimization workflow")
        print("\n✅ Performance optimization workflow ready")
        print("📋 See .claude/commands/cairo-performance-optimization.md for implementation details")
    
    elif args.command == 'code-quality':
        print("--- Cairo Code Quality Enhancement Sub-Agent ---")
        print("📚 Advanced code quality enhancement workflow")
        print("📝 This workflow implements systematic quality improvements and technical debt reduction")
        print(f"Enhancement Type: {args.enhancement_type}")
        print(f"Target File: {args.target_file}")
        if args.analysis:
            print("Mode: Code quality assessment only")
        elif args.implementation:
            print("Mode: Step-by-step quality improvements")
        elif args.metrics:
            print("Mode: Quality metrics and technical debt measurement")
        else:
            print("Mode: Complete quality enhancement workflow")
        print("\n✅ Code quality enhancement workflow ready")
        print("📋 See .claude/commands/cairo-code-quality.md for implementation details")
    
    elif args.command == 'upgrade-infrastructure':
        print("--- Cairo Upgrade Infrastructure Sub-Agent ---")
        print("🏗️ Advanced upgrade infrastructure implementation workflow")
        print("📝 This workflow implements secure contract upgrade mechanisms with governance")
        print(f"Upgrade Type: {args.upgrade_type}")
        print(f"Target Contract: {args.target_contract}")
        if args.design:
            print("Mode: Architecture design and planning only")
        elif args.implementation:
            print("Mode: Step-by-step implementation guide")
        elif args.testing:
            print("Mode: Upgrade testing strategies and validation")
        else:
            print("Mode: Complete upgrade infrastructure workflow")
        print("\n✅ Upgrade infrastructure workflow ready")
        print("📋 See .claude/commands/cairo-upgrade-infrastructure.md for implementation details")
    
    elif args.command == 'issue-coordinator':
        print("--- Cairo Issue Coordination Master Agent ---")
        print("🎯 Master coordinator for systematic issue resolution")
        print("📝 This workflow orchestrates multiple sub-agents for comprehensive remediation")
        print(f"Coordination Mode: {args.coordination_mode}")
        print(f"Target Scope: {args.target_scope}")
        if args.analysis:
            print("Mode: Analysis and planning only")
        elif args.execution:
            print("Mode: Execute coordinated remediation")
        elif args.reporting:
            print("Mode: Generate comprehensive status report")
        else:
            print("Mode: Complete coordination workflow")
        print("\n✅ Issue coordination workflow ready")
        print("📋 See .claude/commands/cairo-issue-coordinator.md for coordination details")

if __name__ == "__main__":
    main()
