#!/usr/bin/env python3
"""
AstraTrade Integration Example

Demonstrates how to use HRM Reasoning Assistant specifically for 
AstraTrade development challenges and patterns.
"""

import sys
import os
from pathlib import Path

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from reasoning.code_analyzer import CodeAnalyzer
from reasoning.architecture_advisor import ArchitectureAdvisor
from reasoning.debug_assistant import DebugAssistant
from reasoning.performance_optimizer import PerformanceOptimizer


def analyze_trading_domain():
    """Analyze AstraTrade trading domain patterns"""
    print("🎯 Trading Domain Analysis")
    print("=" * 40)
    
    # Path to AstraTrade trading domain
    trading_path = "../../../apps/backend/domains/trading"
    
    if not Path(trading_path).exists():
        print("ℹ️  Trading domain path not found - using simulated analysis")
        print("   In real usage, this would analyze:")
        print(f"   - {trading_path}/services.py")
        print(f"   - {trading_path}/entities.py") 
        print(f"   - {trading_path}/value_objects.py")
        print()
        
        # Simulate analysis results
        print("📊 Simulated Analysis Results:")
        print("- **Domain Service Pattern**: Detected in services.py")
        print("- **Repository Pattern**: Well implemented")
        print("- **Entity Design**: Following DDD principles")
        print("- **Value Objects**: Proper immutability")
        print()
        print("🔍 Potential Issues:")
        print("- Complex execute_trade method could be broken down")
        print("- Consider adding circuit breaker for exchange calls")
        print("- Portfolio calculations might benefit from caching")
        print()
        return
    
    try:
        analyzer = CodeAnalyzer()
        results = analyzer.analyze_directory(trading_path)
        
        print(f"📊 Analysis Results ({len(results)} files):")
        for result in results:
            print(f"- {Path(result.file_path).name}: {result.complexity_score:.1f} complexity")
            
        # Generate comprehensive report
        report = analyzer.generate_report(results)
        print("\n📄 Full Report:")
        print(report[:500] + "..." if len(report) > 500 else report)
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
    
    print()


def architecture_advice_for_astratrade():
    """Get architecture advice for common AstraTrade scenarios"""
    print("🏗️  AstraTrade Architecture Guidance")
    print("=" * 40)
    
    advisor = ArchitectureAdvisor()
    
    # AstraTrade-specific architectural questions
    astratrade_questions = [
        {
            "question": "How should I handle real-time price updates for the trading system?",
            "context": "High-frequency trading with WebSocket feeds and database persistence"
        },
        {
            "question": "What's the best way to ensure consistency between trading and gamification domains?",
            "context": "Event-driven architecture with potential consistency issues"
        },
        {
            "question": "Should I implement CQRS for the portfolio management system?",
            "context": "Heavy read operations for portfolio display vs. write operations for trades"
        }
    ]
    
    for i, item in enumerate(astratrade_questions, 1):
        print(f"\n{i}. **Scenario**: {item['question']}")
        print(f"   **Context**: {item['context']}")
        
        try:
            advice = advisor.get_advice(item['question'])
            
            # Extract key recommendation
            lines = advice.split('\n')
            for line in lines:
                if line.strip().startswith('1.') and 'Recommendation' not in line:
                    print(f"   **Key Advice**: {line.strip()}")
                    break
            else:
                print("   **Status**: Analysis complete - see full output for details")
                
        except Exception as e:
            print(f"   ❌ Failed: {e}")
    
    print()


def debug_astratrade_issues():
    """Debug common AstraTrade development issues"""
    print("🐛 AstraTrade Debugging Scenarios")
    print("=" * 40)
    
    debugger = DebugAssistant()
    
    # Real AstraTrade debugging scenarios
    debug_scenarios = [
        {
            "problem": "Trading orders are being rejected with 'Insufficient balance' even when balance is adequate",
            "context": "Concurrent trading operations, database transaction isolation"
        },
        {
            "problem": "Gamification XP points are not updating when trades are executed",
            "context": "Event-driven integration between trading and gamification domains"
        },
        {
            "problem": "WebSocket connections for real-time price updates keep disconnecting under load",
            "context": "High-frequency trading system with multiple concurrent users"
        },
        {
            "problem": "Portfolio calculations show inconsistent values after recent domain service refactoring",
            "context": "Domain-driven design implementation with complex aggregates"
        }
    ]
    
    for i, scenario in enumerate(debug_scenarios, 1):
        print(f"\n{i}. **Problem**: {scenario['problem']}")
        print(f"   **Context**: {scenario['context']}")
        
        try:
            analysis = debugger.debug_problem(scenario['problem'])
            
            # Extract root cause
            lines = analysis.split('\n')
            in_root_cause = False
            
            for line in lines:
                if "Root Cause Analysis" in line:
                    in_root_cause = True
                    continue
                elif line.startswith('##') and in_root_cause:
                    break
                elif in_root_cause and line.strip() and not line.startswith('#'):
                    print(f"   **Analysis**: {line.strip()[:100]}...")
                    break
                    
        except Exception as e:
            print(f"   ❌ Debug failed: {e}")
    
    print()


def optimize_astratrade_performance():
    """Optimize performance for AstraTrade-specific scenarios"""
    print("⚡ AstraTrade Performance Optimization")
    print("=" * 40)
    
    optimizer = PerformanceOptimizer()
    
    # AstraTrade performance optimization scenarios
    perf_scenarios = [
        {
            "issue": "Order execution latency increases during market volatility",
            "context": "High-frequency trading requirements, sub-100ms target"
        },
        {
            "issue": "Portfolio value calculations are slow with large position counts",
            "context": "Real-time portfolio display, complex asset calculations"
        },
        {
            "issue": "Gamification leaderboard updates cause database lock contention",
            "context": "Real-time leaderboard with frequent XP updates"
        },
        {
            "issue": "WebSocket message processing creates memory pressure under high load",
            "context": "Real-time market data feeds, multiple concurrent connections"
        }
    ]
    
    for i, scenario in enumerate(perf_scenarios, 1):
        print(f"\n{i}. **Issue**: {scenario['issue']}")
        print(f"   **Context**: {scenario['context']}")
        
        try:  
            recommendations = optimizer.optimize(scenario['issue'])
            
            # Extract key strategy
            lines = recommendations.split('\n')
            in_strategy = False
            
            for line in lines:
                if "Optimization Strategy" in line:
                    in_strategy = True
                    continue
                elif line.startswith('##') and in_strategy:
                    break
                elif in_strategy and line.strip().startswith('1.'):
                    print(f"   **Strategy**: {line.strip()}")
                    break
                    
        except Exception as e:
            print(f"   ❌ Optimization failed: {e}")
    
    print()


def domain_integration_analysis():
    """Analyze cross-domain integration patterns"""
    print("🔗 Cross-Domain Integration Analysis")
    print("=" * 40)
    
    print("Analyzing integration patterns between AstraTrade domains:")
    print()
    
    # Domain integration scenarios
    integrations = [
        {
            "domains": ["Trading", "Gamification"],
            "challenge": "Ensuring XP awards are consistent with trade execution",
            "pattern": "Event-driven with eventual consistency"
        },
        {
            "domains": ["Trading", "Financial"], 
            "challenge": "Synchronizing trade settlements with billing cycles",
            "pattern": "Transactional outbox pattern"
        },
        {
            "domains": ["Gamification", "Social"],
            "challenge": "Updating leaderboards with social achievements",
            "pattern": "CQRS with shared read models"
        },
        {
            "domains": ["All Domains", "NFT"],
            "challenge": "Minting achievement NFTs across all domains",
            "pattern": "Blockchain integration with retry mechanisms"
        }
    ]
    
    advisor = ArchitectureAdvisor()
    
    for i, integration in enumerate(integrations, 1):
        print(f"{i}. **Integration**: {' ↔ '.join(integration['domains'])}")
        print(f"   **Challenge**: {integration['challenge']}")
        print(f"   **Current Pattern**: {integration['pattern']}")
        
        # Get integration advice
        question = f"How should I improve integration between {integration['domains'][0].lower()} and {integration['domains'][1].lower() if len(integration['domains']) > 1 else 'other'} domains for {integration['challenge'].lower()}?"
        
        try:
            advice = advisor.get_advice(question)
            # Extract first recommendation
            lines = advice.split('\n')
            for line in lines:
                if line.strip().startswith('1.') and len(line.strip()) > 10:
                    print(f"   **Advice**: {line.strip()[:80]}...")
                    break
            else:
                print(f"   **Status**: Integration analysis complete")
                
        except Exception as e:
            print(f"   ❌ Analysis failed: {e}")
        
        print()


def generate_astratrade_report():
    """Generate comprehensive AstraTrade analysis report"""
    print("📊 Comprehensive AstraTrade Analysis Report")
    print("=" * 50)
    
    print("This report would include:")
    print()
    
    report_sections = [
        "🏗️  **Architecture Assessment**",
        "   - Domain-driven design implementation quality",
        "   - Microservices architecture effectiveness", 
        "   - Event-driven patterns and consistency",
        "   - API design and integration patterns",
        "",
        "🔧 **Code Quality Analysis**",
        "   - Domain service implementations",
        "   - Entity and value object design",
        "   - Repository pattern adherence",
        "   - Test coverage and quality",
        "",
        "⚡ **Performance Profile**",
        "   - Trading latency characteristics",
        "   - Database query optimization opportunities",
        "   - Caching strategy effectiveness",
        "   - Resource utilization patterns",
        "",
        "🐛 **Risk Assessment**",
        "   - Potential failure points",
        "   - Scalability bottlenecks",
        "   - Security considerations",
        "   - Operational complexity",
        "",
        "🎯 **Optimization Roadmap**",
        "   - High-impact improvements (Phase 1)",
        "   - Medium-term enhancements (Phase 2)", 
        "   - Long-term architectural evolution (Phase 3)",
        "   - Success metrics and monitoring"
    ]
    
    for section in report_sections:
        print(section)
    
    print()
    print("To generate this report:")
    print("./hrm-reason analyze /path/to/AstraTrade-Submission --output astratrade_report.md")
    print()


def main():
    """Run AstraTrade-specific demonstrations"""
    print("🎯 HRM Reasoning Assistant - AstraTrade Integration")
    print("=" * 60)
    print("Specialized AI assistance for AstraTrade development challenges")
    print("=" * 60)
    print()
    
    try:
        # Run AstraTrade-specific demos
        analyze_trading_domain()
        architecture_advice_for_astratrade()
        debug_astratrade_issues()  
        optimize_astratrade_performance()
        domain_integration_analysis()
        generate_astratrade_report()
        
        print("🎉 AstraTrade Integration Demo Complete!")
        print("=" * 50)
        print()
        print("🚀 **Next Steps for AstraTrade Development**:")
        print()
        print("1. **Immediate Usage**:")
        print("   ./hrm-reason analyze apps/backend/domains/trading/")
        print("   ./hrm-reason architecture 'How should I optimize order processing?'")
        print()
        print("2. **Training Customization**:")
        print("   ./hrm-reason train /path/to/AstraTrade-Submission")
        print("   # This builds AstraTrade-specific reasoning patterns")
        print()
        print("3. **Workflow Integration**:")
        print("   - Use before major refactoring decisions")
        print("   - Integrate into code review process")
        print("   - Apply to performance optimization cycles")
        print("   - Leverage for debugging complex integration issues")
        print()
        print("4. **Team Collaboration**:")
        print("   - Share analysis reports with team members")
        print("   - Use for architectural decision documentation")
        print("   - Apply to onboarding new developers")
        print()
        print("💡 **Key Benefits for AstraTrade**:")
        print("   - 🎯 Domain-specific reasoning for trading systems")
        print("   - 🏗️  Architecture decisions aligned with HFT requirements")
        print("   - 🐛 Systematic debugging of complex integration issues")
        print("   - ⚡ Performance optimization for trading latency")
        print("   - 🔗 Cross-domain integration guidance")
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Demo interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Demo failed: {e}")
        print("Note: Some features require trained models or actual AstraTrade codebase access")


if __name__ == "__main__":
    main()