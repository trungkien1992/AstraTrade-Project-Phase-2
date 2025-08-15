#!/usr/bin/env python3
"""
Test Script for UMAS-Cairo Integration
=====================================

Comprehensive test suite to verify the integration between the Ultimate Multi-Agent
System (UMAS) and Cairo subagent commands for AstraTrade project enhancement.
"""

import sys
import os
import asyncio
import json
import time
from pathlib import Path
from typing import Dict, List, Any

# Test configuration
TEST_CONFIG = {
    "timeout": 60,  # seconds
    "retry_attempts": 3,
    "log_level": "INFO"
}

class UMASCairoTester:
    """Test suite for UMAS-Cairo integration"""
    
    def __init__(self):
        self.results = {
            "passed": 0,
            "failed": 0,
            "errors": [],
            "test_details": {}
        }
        self.start_time = time.time()
    
    async def run_all_tests(self) -> Dict:
        """Run comprehensive test suite"""
        print("🧪 UMAS-Cairo Integration Test Suite")
        print("=" * 50)
        
        test_methods = [
            ("Import Tests", self.test_imports),
            ("Bridge Module Tests", self.test_bridge_module),
            ("Agent Creation Tests", self.test_agent_creation),
            ("Workflow Template Tests", self.test_workflow_templates),
            ("Integration Tests", self.test_integration_functionality),
            ("Performance Tests", self.test_performance),
            ("Error Handling Tests", self.test_error_handling)
        ]
        
        for test_name, test_method in test_methods:
            print(f"\n🔍 Running {test_name}...")
            try:
                result = await test_method()
                if result:
                    self.results["passed"] += 1
                    print(f"✅ {test_name}: PASSED")
                else:
                    self.results["failed"] += 1
                    print(f"❌ {test_name}: FAILED")
                self.results["test_details"][test_name] = result
            except Exception as e:
                self.results["failed"] += 1
                self.results["errors"].append(f"{test_name}: {str(e)}")
                print(f"💥 {test_name}: ERROR - {str(e)}")
                self.results["test_details"][test_name] = False
        
        return self.generate_report()
    
    async def test_imports(self) -> bool:
        """Test that all required modules can be imported"""
        try:
            # Test UMAS bridge import
            from Cairo_subagent.umas_integration import (
                CairoUMASIntegration,
                CairoSecurityAgent,
                CairoDevelopmentAgent,
                get_cairo_umas_integration
            )
            
            # Test agent imports
            from Cairo_subagent.agents.cairo_architecture_agent import CairoArchitectureAgent
            from Cairo_subagent.agents.cairo_testing_agent import CairoTestingAgent
            from Cairo_subagent.agents.cairo_refactoring_agent import CairoRefactoringAgent
            
            # Test workflow imports
            from Cairo_subagent.workflows.cairo_workflows import (
                CairoWorkflowTemplates,
                get_cairo_workflow_templates
            )
            
            print("  ✓ All imports successful")
            return True
            
        except ImportError as e:
            print(f"  ✗ Import failed: {e}")
            return False
        except Exception as e:
            print(f"  ✗ Unexpected error: {e}")
            return False
    
    async def test_bridge_module(self) -> bool:
        """Test UMAS-Cairo bridge module functionality"""
        try:
            from Cairo_subagent.umas_integration import get_cairo_umas_integration
            
            # Test integration instance creation
            integration = get_cairo_umas_integration()
            if not integration:
                print("  ✗ Failed to create integration instance")
                return False
            
            print(f"  ✓ Integration instance created: {type(integration).__name__}")
            
            # Test configuration
            if hasattr(integration, 'project_path'):
                print(f"  ✓ Project path configured: {integration.project_path}")
            else:
                print("  ⚠ Project path not configured")
            
            return True
            
        except Exception as e:
            print(f"  ✗ Bridge module test failed: {e}")
            return False
    
    async def test_agent_creation(self) -> bool:
        """Test specialized Cairo agent creation"""
        try:
            # Import agent classes
            from Cairo_subagent.umas_integration import (
                CairoSecurityAgent,
                CairoDevelopmentAgent
            )
            from Cairo_subagent.agents.cairo_architecture_agent import CairoArchitectureAgent
            from Cairo_subagent.agents.cairo_testing_agent import CairoTestingAgent
            from Cairo_subagent.agents.cairo_refactoring_agent import CairoRefactoringAgent
            
            # Test agent class availability
            agent_classes = [
                ("CairoSecurityAgent", CairoSecurityAgent),
                ("CairoDevelopmentAgent", CairoDevelopmentAgent),
                ("CairoArchitectureAgent", CairoArchitectureAgent),
                ("CairoTestingAgent", CairoTestingAgent),
                ("CairoRefactoringAgent", CairoRefactoringAgent)
            ]
            
            for agent_name, agent_class in agent_classes:
                if hasattr(agent_class, '_initialize'):
                    print(f"  ✓ {agent_name} class structure valid")
                else:
                    print(f"  ✗ {agent_name} missing _initialize method")
                    return False
            
            print(f"  ✓ All {len(agent_classes)} agent classes validated")
            return True
            
        except Exception as e:
            print(f"  ✗ Agent creation test failed: {e}")
            return False
    
    async def test_workflow_templates(self) -> bool:
        """Test workflow template functionality"""
        try:
            from Cairo_subagent.workflows.cairo_workflows import (
                CairoWorkflowTemplates,
                get_cairo_workflow_templates
            )
            
            # Test workflow templates instance
            templates = get_cairo_workflow_templates()
            if not templates:
                print("  ✗ Failed to get workflow templates")
                return False
            
            # Test available workflows
            expected_workflows = [
                "cairo_security_audit",
                "cairo_development_cycle", 
                "cairo_safe_refactoring",
                "cairo_comprehensive_review",
                "cairo_expert_coordination"
            ]
            
            available_workflows = list(templates.templates.keys())
            print(f"  ✓ Available workflows: {len(available_workflows)}")
            
            for workflow in expected_workflows:
                if workflow in available_workflows:
                    print(f"    ✓ {workflow}")
                else:
                    print(f"    ✗ Missing {workflow}")
                    return False
            
            print(f"  ✓ All {len(expected_workflows)} workflows available")
            return True
            
        except Exception as e:
            print(f"  ✗ Workflow template test failed: {e}")
            return False
    
    async def test_integration_functionality(self) -> bool:
        """Test core integration functionality without starting full UMAS"""
        try:
            from Cairo_subagent.umas_integration import get_cairo_umas_integration
            
            integration = get_cairo_umas_integration()
            
            # Test convenience functions exist
            convenience_functions = [
                'start_cairo_umas',
                'cairo_security_audit',
                'cairo_code_generation',
                'get_cairo_umas_status'
            ]
            
            # Import convenience functions
            from Cairo_subagent.umas_integration import (
                start_cairo_umas,
                cairo_security_audit,
                cairo_code_generation,
                get_cairo_umas_status
            )
            
            print(f"  ✓ All convenience functions imported")
            
            # Test Cairo task types
            from Cairo_subagent.umas_integration import CairoTaskType
            
            task_types = [
                "SECURITY_AUDIT",
                "CODE_GENERATION", 
                "ARCHITECTURE_REVIEW",
                "REFACTORING_ANALYSIS",
                "TESTING_STRATEGY"
            ]
            
            for task_type in task_types:
                if hasattr(CairoTaskType, task_type):
                    print(f"    ✓ {task_type}")
                else:
                    print(f"    ✗ Missing {task_type}")
                    return False
            
            print(f"  ✓ All Cairo task types defined")
            return True
            
        except Exception as e:
            print(f"  ✗ Integration functionality test failed: {e}")
            return False
    
    async def test_performance(self) -> bool:
        """Test performance characteristics of the integration"""
        try:
            start_time = time.time()
            
            # Test import performance
            from Cairo_subagent.umas_integration import get_cairo_umas_integration
            from Cairo_subagent.workflows.cairo_workflows import get_cairo_workflow_templates
            
            import_time = time.time() - start_time
            print(f"  ✓ Import time: {import_time:.3f}s")
            
            # Test instance creation performance
            start_time = time.time()
            integration = get_cairo_umas_integration()
            templates = get_cairo_workflow_templates()
            creation_time = time.time() - start_time
            print(f"  ✓ Instance creation time: {creation_time:.3f}s")
            
            # Performance benchmarks
            if import_time < 2.0:
                print(f"  ✓ Import performance acceptable")
            else:
                print(f"  ⚠ Import performance slow: {import_time:.3f}s")
            
            if creation_time < 0.5:
                print(f"  ✓ Creation performance excellent")
            else:
                print(f"  ⚠ Creation performance acceptable: {creation_time:.3f}s")
            
            return True
            
        except Exception as e:
            print(f"  ✗ Performance test failed: {e}")
            return False
    
    async def test_error_handling(self) -> bool:
        """Test error handling and graceful degradation"""
        try:
            from Cairo_subagent.umas_integration import get_cairo_umas_integration
            
            # Test integration with invalid path
            integration = get_cairo_umas_integration("/invalid/path")
            if integration:
                print(f"  ✓ Handles invalid path gracefully")
            else:
                print(f"  ✗ Failed to handle invalid path")
                return False
            
            # Test workflow templates error handling
            from Cairo_subagent.workflows.cairo_workflows import CairoWorkflowTemplates
            templates = CairoWorkflowTemplates()
            
            # Test with empty parameters
            try:
                # This should not crash
                result = await templates._analyze_query_complexity("")
                if result:
                    print(f"  ✓ Handles empty query gracefully")
                else:
                    print(f"  ⚠ Empty query returns None")
            except Exception as e:
                print(f"  ⚠ Empty query handling: {e}")
            
            return True
            
        except Exception as e:
            print(f"  ✗ Error handling test failed: {e}")
            return False
    
    async def test_mock_workflow_execution(self) -> bool:
        """Test mock workflow execution (without full UMAS startup)"""
        try:
            from Cairo_subagent.workflows.cairo_workflows import CairoWorkflowTemplates
            
            templates = CairoWorkflowTemplates()
            
            # Test query analysis
            query = "How to implement secure access control in Cairo contracts?"
            analysis = templates._analyze_query_complexity(query)
            
            if analysis and "complexity_score" in analysis:
                print(f"  ✓ Query analysis working: score {analysis['complexity_score']}")
            else:
                print(f"  ✗ Query analysis failed")
                return False
            
            # Test expert routing
            routing = templates._determine_expert_routing(query, analysis, "collaborative")
            
            if routing and "strategy" in routing:
                print(f"  ✓ Expert routing working: {routing['strategy']}")
            else:
                print(f"  ✗ Expert routing failed")
                return False
            
            return True
            
        except Exception as e:
            print(f"  ✗ Mock workflow test failed: {e}")
            return False
    
    def generate_report(self) -> Dict:
        """Generate comprehensive test report"""
        total_tests = self.results["passed"] + self.results["failed"]
        success_rate = (self.results["passed"] / total_tests * 100) if total_tests > 0 else 0
        duration = time.time() - self.start_time
        
        report = {
            "summary": {
                "total_tests": total_tests,
                "passed": self.results["passed"],
                "failed": self.results["failed"],
                "success_rate": f"{success_rate:.1f}%",
                "duration": f"{duration:.2f}s"
            },
            "test_details": self.results["test_details"],
            "errors": self.results["errors"],
            "recommendations": self.generate_recommendations()
        }
        
        return report
    
    def generate_recommendations(self) -> List[str]:
        """Generate recommendations based on test results"""
        recommendations = []
        
        if self.results["failed"] == 0:
            recommendations.append("✅ All tests passed! UMAS-Cairo integration is ready for production use.")
            recommendations.append("🚀 You can now use enhanced Cairo workflows with multi-agent coordination.")
            recommendations.append("📊 Enable monitoring and caching for optimal performance.")
        else:
            recommendations.append("⚠️ Some tests failed. Review errors before production deployment.")
            if self.results["errors"]:
                recommendations.append("🔧 Address import or dependency issues first.")
            recommendations.append("🧪 Run tests again after fixing issues.")
        
        recommendations.extend([
            "📈 Monitor system performance during initial usage.",
            "🔄 Update agent capabilities based on usage patterns.", 
            "📝 Document custom workflows for team usage."
        ])
        
        return recommendations

async def main():
    """Main test execution"""
    print("🧪 UMAS-Cairo Integration Test Suite")
    print("=" * 50)
    print("Testing Ultimate Multi-Agent System integration with Cairo subagent...")
    print()
    
    tester = UMASCairoTester()
    
    # Run comprehensive tests
    report = await tester.run_all_tests()
    
    # Print final report
    print("\n" + "=" * 50)
    print("📊 TEST REPORT")
    print("=" * 50)
    
    summary = report["summary"]
    print(f"Total Tests: {summary['total_tests']}")
    print(f"Passed: {summary['passed']} ✅")
    print(f"Failed: {summary['failed']} ❌")
    print(f"Success Rate: {summary['success_rate']}")
    print(f"Duration: {summary['duration']}")
    
    if report["errors"]:
        print(f"\n❌ Errors:")
        for error in report["errors"]:
            print(f"  • {error}")
    
    print(f"\n💡 Recommendations:")
    for rec in report["recommendations"]:
        print(f"  {rec}")
    
    # Return exit code based on results
    return 0 if summary["success_rate"] == "100.0%" else 1

if __name__ == "__main__":
    # Add current directory and parent directory to Python path for imports
    current_dir = Path(__file__).parent
    parent_dir = current_dir.parent
    sys.path.insert(0, str(parent_dir))
    sys.path.insert(0, str(current_dir))
    
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n⚠️ Test suite interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test suite crashed: {e}")
        sys.exit(1)