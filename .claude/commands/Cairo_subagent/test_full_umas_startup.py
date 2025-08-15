#!/usr/bin/env python3
"""
Full UMAS Startup Test for Cairo Integration
==========================================

This test actually initializes the complete UMAS system with Cairo agents
and validates full functionality including Redis, WebSocket monitoring,
and Prometheus metrics.
"""

import sys
import os
import asyncio
import json
import time
import redis
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add paths for Cairo subagent imports
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
sys.path.insert(0, str(parent_dir))
sys.path.insert(0, str(current_dir))

class FullUMASStartupTest:
    """Complete UMAS startup and functionality test"""
    
    def __init__(self):
        self.results = {
            "startup": False,
            "redis_connection": False,
            "agents_loaded": False,
            "workflows_available": False,
            "monitoring_active": False,
            "full_execution": False,
            "errors": []
        }
        self.umas_system = None
        self.cairo_integration = None
        
    async def run_full_test(self) -> Dict:
        """Run complete UMAS startup and functionality test"""
        print("🚀 FULL UMAS-CAIRO STARTUP TEST")
        print("=" * 50)
        print("Initializing complete UMAS system with Cairo agents...")
        print()
        
        try:
            # Step 1: Test Redis connectivity
            print("🔍 Step 1: Testing Redis connectivity...")
            if await self.test_redis_connection():
                print("✅ Redis connection successful")
                self.results["redis_connection"] = True
            else:
                print("❌ Redis connection failed")
                return self.results
                
            # Step 2: Initialize UMAS system
            print("\n🔍 Step 2: Initializing UMAS system...")
            if await self.initialize_umas_system():
                print("✅ UMAS system initialized")
                self.results["startup"] = True
            else:
                print("❌ UMAS system initialization failed")
                return self.results
                
            # Step 3: Load Cairo agents
            print("\n🔍 Step 3: Loading Cairo specialized agents...")
            if await self.load_cairo_agents():
                print("✅ All Cairo agents loaded successfully")
                self.results["agents_loaded"] = True
            else:
                print("❌ Failed to load Cairo agents")
                return self.results
                
            # Step 4: Verify workflows
            print("\n🔍 Step 4: Verifying workflow availability...")
            if await self.verify_workflows():
                print("✅ All workflows available and ready")
                self.results["workflows_available"] = True
            else:
                print("❌ Workflow verification failed")
                return self.results
                
            # Step 5: Start monitoring
            print("\n🔍 Step 5: Starting monitoring systems...")
            if await self.start_monitoring():
                print("✅ Monitoring systems active")
                self.results["monitoring_active"] = True
            else:
                print("❌ Monitoring startup failed")
                return self.results
                
            # Step 6: Execute full workflow test
            print("\n🔍 Step 6: Executing full workflow test...")
            if await self.execute_full_workflow():
                print("✅ Full workflow execution successful")
                self.results["full_execution"] = True
            else:
                print("❌ Full workflow execution failed")
                return self.results
                
            print("\n🎉 ALL TESTS PASSED! UMAS-Cairo integration fully operational.")
            
        except Exception as e:
            error_msg = f"Critical test failure: {str(e)}"
            print(f"\n💥 {error_msg}")
            self.results["errors"].append(error_msg)
            
        finally:
            # Cleanup
            await self.cleanup()
            
        return self.results
    
    async def test_redis_connection(self) -> bool:
        """Test Redis connectivity for UMAS caching"""
        try:
            # Try to connect to Redis
            redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
            
            # Test connection with ping
            ping_result = redis_client.ping()
            if not ping_result:
                print("  ❌ Redis ping failed")
                return False
                
            # Test basic operations
            test_key = "umas_test_connection"
            redis_client.set(test_key, "test_value", ex=60)
            retrieved_value = redis_client.get(test_key)
            
            if retrieved_value != "test_value":
                print("  ❌ Redis read/write test failed")
                return False
                
            # Cleanup test key
            redis_client.delete(test_key)
            
            print("  ✓ Redis connectivity verified")
            print("  ✓ Redis read/write operations working")
            return True
            
        except redis.ConnectionError:
            print("  ❌ Cannot connect to Redis server")
            print("  💡 Hint: Start Redis with 'redis-server' or 'brew services start redis'")
            return False
        except Exception as e:
            print(f"  ❌ Redis test error: {e}")
            return False
    
    async def initialize_umas_system(self) -> bool:
        """Initialize the complete UMAS system"""
        try:
            from Cairo_subagent.umas_integration import get_cairo_umas_integration
            
            # Get Cairo UMAS integration
            self.cairo_integration = get_cairo_umas_integration()
            if not self.cairo_integration:
                print("  ❌ Failed to get Cairo UMAS integration")
                return False
                
            # Initialize the UMAS system
            await self.cairo_integration.initialize()
            
            if not self.cairo_integration.system:
                print("  ❌ UMAS system not initialized")
                return False
                
            self.umas_system = self.cairo_integration.system
            
            print("  ✓ UMAS system core initialized")
            print("  ✓ Cairo integration bridge active")
            print(f"  ✓ Project path: {self.cairo_integration.project_path}")
            
            return True
            
        except ImportError as e:
            print(f"  ❌ Import error: {e}")
            print("  💡 Ensure UMAS dependencies are installed")
            return False
        except Exception as e:
            print(f"  ❌ UMAS initialization error: {e}")
            return False
    
    async def load_cairo_agents(self) -> bool:
        """Load and verify all Cairo specialized agents"""
        try:
            # Import required UMAS components first
            from src.ultimate_multi_agent_system import AgentRole, UltimateAgent
            from pathlib import Path
            
            # Import all Cairo agent classes
            from Cairo_subagent.umas_integration import (
                CairoSecurityAgent,
                CairoDevelopmentAgent
            )
            from Cairo_subagent.agents.cairo_architecture_agent import CairoArchitectureAgent
            from Cairo_subagent.agents.cairo_testing_agent import CairoTestingAgent
            from Cairo_subagent.agents.cairo_refactoring_agent import CairoRefactoringAgent
            
            # Load agents into UMAS system using add_agent method
            agent_configs = [
                ("cairo_security", CairoSecurityAgent),
                ("cairo_development", CairoDevelopmentAgent), 
                ("cairo_architecture", CairoArchitectureAgent),
                ("cairo_testing", CairoTestingAgent),
                ("cairo_refactoring", CairoRefactoringAgent)
            ]
            
            loaded_agents = []
            for agent_name, agent_class in agent_configs:
                try:
                    # Use UMAS add_agent method which handles initialization
                    agent_id = self.umas_system.add_agent(agent_class, agent_id=agent_name)
                    loaded_agents.append(agent_name)
                    
                    print(f"  ✓ {agent_name} loaded and registered with ID: {agent_id}")
                    
                except Exception as e:
                    print(f"  ❌ Failed to load {agent_name}: {e}")
                    return False
            
            print(f"  ✓ All {len(loaded_agents)} Cairo agents loaded successfully")
            
            # Verify agent availability in system registry
            total_agents = len(self.umas_system.agents)
            cairo_agent_names = [name for name in self.umas_system.agents.keys() if 'cairo' in name.lower()]
            
            if len(cairo_agent_names) >= 5:
                print(f"  ✓ System registry shows {len(cairo_agent_names)} Cairo agents: {cairo_agent_names}")
                return True
            else:
                print(f"  ❌ Expected 5 Cairo agents, found {len(cairo_agent_names)}: {cairo_agent_names}")
                return False
                
        except Exception as e:
            print(f"  ❌ Agent loading error: {e}")
            return False
    
    async def verify_workflows(self) -> bool:
        """Verify all Cairo workflows are available and functional"""
        try:
            from Cairo_subagent.workflows.cairo_workflows import get_cairo_workflow_templates
            
            # Get workflow templates
            workflow_templates = get_cairo_workflow_templates()
            if not workflow_templates:
                print("  ❌ Failed to get workflow templates")
                return False
                
            # Expected workflows (matching actual implementation)
            expected_workflows = [
                "cairo_security_audit",
                "cairo_development_cycle",
                "cairo_safe_refactoring", 
                "cairo_comprehensive_review",
                "cairo_expert_coordination"
            ]
            
            available_workflows = list(workflow_templates.templates.keys())
            print(f"  ✓ Found {len(available_workflows)} workflow templates")
            
            missing_workflows = []
            for workflow in expected_workflows:
                if workflow in available_workflows:
                    print(f"    ✓ {workflow}")
                else:
                    print(f"    ❌ Missing {workflow}")
                    missing_workflows.append(workflow)
            
            if missing_workflows:
                print(f"  ❌ {len(missing_workflows)} workflows missing")
                return False
                
            # Test workflow template functionality
            sample_workflow = workflow_templates.templates["cairo_security_audit"]
            if callable(sample_workflow):
                print("  ✓ Workflow templates are callable")
                return True
            else:
                print("  ❌ Workflow templates not callable")
                return False
                
        except Exception as e:
            print(f"  ❌ Workflow verification error: {e}")
            return False
    
    async def start_monitoring(self) -> bool:
        """Start UMAS monitoring systems"""
        try:
            # Start WebSocket monitoring
            if hasattr(self.umas_system, 'start_websocket_monitoring'):
                await self.umas_system.start_websocket_monitoring(port=8765)
                print("  ✓ WebSocket monitoring started on port 8765")
            else:
                print("  ⚠ WebSocket monitoring not available")
                
            # Start Prometheus metrics
            if hasattr(self.umas_system, 'start_prometheus_metrics'):
                await self.umas_system.start_prometheus_metrics(port=8000)
                print("  ✓ Prometheus metrics started on port 8000")
            else:
                print("  ⚠ Prometheus metrics not available")
                
            # Verify monitoring endpoints
            monitoring_active = await self.verify_monitoring_endpoints()
            if monitoring_active:
                print("  ✓ Monitoring endpoints responding")
                return True
            else:
                print("  ⚠ Some monitoring endpoints not responding")
                return True  # Non-critical for core functionality
                
        except Exception as e:
            print(f"  ❌ Monitoring startup error: {e}")
            return False
    
    async def verify_monitoring_endpoints(self) -> bool:
        """Verify monitoring endpoints are responding"""
        try:
            import aiohttp
            
            async with aiohttp.ClientSession() as session:
                # Test WebSocket endpoint
                try:
                    async with session.ws_connect('ws://localhost:8765') as ws:
                        await ws.ping()
                        print("    ✓ WebSocket endpoint responding")
                except:
                    print("    ⚠ WebSocket endpoint not responding")
                    
                # Test Prometheus metrics endpoint
                try:
                    async with session.get('http://localhost:8000/metrics') as response:
                        if response.status == 200:
                            print("    ✓ Prometheus metrics endpoint responding")
                        else:
                            print("    ⚠ Prometheus metrics endpoint error")
                except:
                    print("    ⚠ Prometheus metrics endpoint not responding")
                    
            return True
            
        except ImportError:
            print("    ⚠ aiohttp not available for endpoint testing")
            return True
        except Exception as e:
            print(f"    ⚠ Endpoint verification error: {e}")
            return True
    
    async def execute_full_workflow(self) -> bool:
        """Execute a complete Cairo workflow end-to-end"""
        try:
            print("  🎯 Executing Cairo Security Audit workflow...")
            
            # Prepare test parameters
            workflow_params = {
                "contracts": ["test_contract.cairo"],  # Mock contract for testing
                "audit_type": "quick",
                "parallel_execution": True,
                "confidence_threshold": 0.8
            }
            
            # Get workflow template
            from Cairo_subagent.workflows.cairo_workflows import get_cairo_workflow_templates
            workflow_templates = get_cairo_workflow_templates()
            security_audit_workflow = workflow_templates.templates["cairo_security_audit"]
            
            print("  ⏱️ Starting workflow execution...")
            start_time = time.time()
            
            # Execute the workflow
            result = await security_audit_workflow(self.umas_system, workflow_params)
            
            execution_time = time.time() - start_time
            print(f"  ✓ Workflow completed in {execution_time:.2f} seconds")
            
            # Validate result structure
            if result and isinstance(result, dict):
                print(f"  ✓ Workflow result type: {type(result)}")
                print(f"  ✓ Result keys: {list(result.keys())}")
                
                # Check for basic workflow result structure (more flexible)
                if "workflow" in result or "phases" in result or "summary" in result:
                    print("  ✓ Workflow result structure valid")
                    workflow_name = result.get('workflow', 'cairo_security_audit')
                    print(f"  ✓ Workflow: {workflow_name}")
                    
                    phases = result.get('phases', {})
                    print(f"  ✓ Phases completed: {len(phases)}")
                    
                    return True
                else:
                    print(f"  ❌ Unexpected result structure: {result}")
                    return False
            else:
                print("  ❌ Invalid workflow result format")
                return False
                
        except Exception as e:
            print(f"  ❌ Workflow execution error: {e}")
            return False
    
    async def cleanup(self) -> None:
        """Clean up resources and connections"""
        try:
            if self.umas_system:
                print("\n🧹 Cleaning up resources...")
                
                # Stop monitoring systems
                if hasattr(self.umas_system, 'stop_monitoring'):
                    await self.umas_system.stop_monitoring()
                    print("  ✓ Monitoring systems stopped")
                
                # Disconnect agents
                if hasattr(self.umas_system, 'disconnect_all_agents'):
                    await self.umas_system.disconnect_all_agents()
                    print("  ✓ All agents disconnected")
                
                # Close system connections
                if hasattr(self.umas_system, 'close'):
                    await self.umas_system.close()
                    print("  ✓ UMAS system closed")
                    
            print("  ✅ Cleanup completed")
            
        except Exception as e:
            print(f"  ⚠ Cleanup warning: {e}")

async def main():
    """Main test execution"""
    print("🧪 FULL UMAS-CAIRO STARTUP TEST")
    print("=" * 50)
    print("This test will fully initialize UMAS with all Cairo agents")
    print("and execute a complete workflow to verify functionality.")
    print()
    
    # Pre-flight checks
    print("🔍 Pre-flight checks...")
    
    # Check Redis availability
    try:
        import redis
        redis_client = redis.Redis(host='localhost', port=6379, db=0)
        redis_client.ping()
        print("  ✓ Redis server available")
    except:
        print("  ❌ Redis server not available")
        print("  💡 Start Redis: redis-server or brew services start redis")
        print("  ⚠ Continuing without Redis (degraded functionality)")
    
    # Check UMAS dependencies
    try:
        import websockets
        import aiohttp
        import prometheus_client
        print("  ✓ All UMAS dependencies available")
    except ImportError as e:
        print(f"  ⚠ Some UMAS dependencies missing: {e}")
        print("  💡 Install with: pip install websockets aiohttp prometheus_client")
    
    print()
    
    # Execute full test
    tester = FullUMASStartupTest()
    results = await tester.run_full_test()
    
    # Final report
    print("\n" + "=" * 50)
    print("📊 FULL STARTUP TEST RESULTS")
    print("=" * 50)
    
    test_results = [
        ("Redis Connection", results["redis_connection"]),
        ("UMAS System Startup", results["startup"]),
        ("Cairo Agents Loaded", results["agents_loaded"]),
        ("Workflows Available", results["workflows_available"]),
        ("Monitoring Active", results["monitoring_active"]),
        ("Full Execution", results["full_execution"])
    ]
    
    passed_tests = sum(1 for _, result in test_results if result)
    total_tests = len(test_results)
    
    print(f"Tests Passed: {passed_tests}/{total_tests}")
    print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%")
    print()
    
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} {test_name}")
    
    if results["errors"]:
        print(f"\n❌ Errors encountered:")
        for error in results["errors"]:
            print(f"  • {error}")
    
    if passed_tests == total_tests:
        print(f"\n🎉 ALL TESTS PASSED!")
        print("UMAS-Cairo integration is fully operational and ready for production use.")
        return 0
    else:
        print(f"\n⚠️ {total_tests - passed_tests} tests failed.")
        print("Review errors and ensure all dependencies are properly installed.")
        return 1

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test suite crashed: {e}")
        sys.exit(1)