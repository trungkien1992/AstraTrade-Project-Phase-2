#!/usr/bin/env python3
"""
AstraTrade Comprehensive Performance Optimization Suite
Orchestrates all performance optimization modules and generates unified report.
"""

import asyncio
import time
import json
import logging
from datetime import datetime
from typing import Dict, Any, List
from pathlib import Path

# Import our optimization modules
from load_testing_framework import AstraTradeLoadTester
from database_optimization import DatabaseOptimizer
from redis_optimization import RedisOptimizer
from api_optimization import APIOptimizer

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("performance-suite")

class ComprehensivePerformanceOptimizer:
    """Orchestrates all performance optimization modules."""
    
    def __init__(self, base_url: str = "http://localhost:8000", 
                 database_url: str = "postgresql+asyncpg://postgres:password@localhost/astradb",
                 redis_url: str = "redis://localhost:6379"):
        self.base_url = base_url
        self.database_url = database_url
        self.redis_url = redis_url
        self.results = {}
        
    async def run_load_testing(self) -> Dict[str, Any]:
        """Run comprehensive load testing."""
        logger.info("🚀 Starting Load Testing Suite...")
        
        try:
            tester = AstraTradeLoadTester(self.base_url)
            results = await tester.run_comprehensive_load_test()
            
            self.results["load_testing"] = {
                "status": "completed",
                "summary": results["summary"],
                "performance_metrics": results["performance_metrics"],
                "recommendations": results["recommendations"],
                "completion_time": datetime.now().isoformat()
            }
            
            logger.info("✅ Load Testing completed successfully")
            return results
            
        except Exception as e:
            logger.error(f"❌ Load Testing failed: {e}")
            self.results["load_testing"] = {
                "status": "failed",
                "error": str(e),
                "completion_time": datetime.now().isoformat()
            }
            return {}
    
    async def run_database_optimization(self) -> Dict[str, Any]:
        """Run database optimization."""
        logger.info("🗄️ Starting Database Optimization...")
        
        try:
            optimizer = DatabaseOptimizer(self.database_url)
            results = await optimizer.run_comprehensive_optimization()
            await optimizer.cleanup()
            
            self.results["database_optimization"] = {
                "status": "completed",
                "summary": results["optimization_summary"],
                "recommendations": results["recommendations"],
                "completion_time": datetime.now().isoformat()
            }
            
            logger.info("✅ Database Optimization completed successfully")
            return results
            
        except Exception as e:
            logger.error(f"❌ Database Optimization failed: {e}")
            self.results["database_optimization"] = {
                "status": "failed", 
                "error": str(e),
                "completion_time": datetime.now().isoformat()
            }
            return {}
    
    async def run_redis_optimization(self) -> Dict[str, Any]:
        """Run Redis optimization."""
        logger.info("📊 Starting Redis Optimization...")
        
        try:
            optimizer = RedisOptimizer(self.redis_url)
            results = await optimizer.run_comprehensive_optimization()
            await optimizer.cleanup()
            
            self.results["redis_optimization"] = {
                "status": "completed",
                "summary": results["optimization_summary"],
                "performance_metrics": results["performance_metrics"],
                "memory_metrics": results["memory_metrics"],
                "recommendations": results["recommendations"],
                "completion_time": datetime.now().isoformat()
            }
            
            logger.info("✅ Redis Optimization completed successfully")
            return results
            
        except Exception as e:
            logger.error(f"❌ Redis Optimization failed: {e}")
            self.results["redis_optimization"] = {
                "status": "failed",
                "error": str(e),
                "completion_time": datetime.now().isoformat()
            }
            return {}
    
    async def run_api_optimization(self) -> Dict[str, Any]:
        """Run API optimization."""
        logger.info("⚡ Starting API Optimization...")
        
        try:
            optimizer = APIOptimizer(self.base_url)
            results = await optimizer.run_comprehensive_optimization()
            
            self.results["api_optimization"] = {
                "status": "completed",
                "summary": results["optimization_summary"],
                "baseline_performance": results["baseline_performance"],
                "post_optimization_performance": results["post_optimization_performance"],
                "optimization_techniques": results["optimization_techniques"],
                "recommendations": results["recommendations"],
                "completion_time": datetime.now().isoformat()
            }
            
            logger.info("✅ API Optimization completed successfully")
            return results
            
        except Exception as e:
            logger.error(f"❌ API Optimization failed: {e}")
            self.results["api_optimization"] = {
                "status": "failed",
                "error": str(e),
                "completion_time": datetime.now().isoformat()
            }
            return {}
    
    async def run_comprehensive_optimization(self) -> Dict[str, Any]:
        """Run all optimization modules in sequence."""
        logger.info("🌟 Starting Comprehensive Performance Optimization Suite")
        logger.info("=" * 80)
        
        suite_start_time = time.time()
        
        # Phase 1: Infrastructure Optimization (parallel where safe)
        logger.info("\n📋 Phase 1: Infrastructure Optimization")
        
        # Run database and Redis optimization in parallel (they don't conflict)
        db_task = asyncio.create_task(self.run_database_optimization())
        redis_task = asyncio.create_task(self.run_redis_optimization())
        
        db_results, redis_results = await asyncio.gather(db_task, redis_task, return_exceptions=True)
        
        # Phase 2: API Optimization (after infrastructure is optimized)
        logger.info("\n📋 Phase 2: API Performance Optimization")
        api_results = await self.run_api_optimization()
        
        # Phase 3: Load Testing (final validation)
        logger.info("\n📋 Phase 3: Load Testing Validation")
        load_test_results = await self.run_load_testing()
        
        suite_end_time = time.time()
        total_duration = suite_end_time - suite_start_time
        
        # Generate comprehensive report
        comprehensive_report = self._generate_comprehensive_report(total_duration)
        
        logger.info("\n" + "=" * 80)
        logger.info("🎉 Comprehensive Performance Optimization Complete!")
        logger.info(f"Total Duration: {total_duration:.1f} seconds")
        logger.info(f"Modules Completed: {sum(1 for r in self.results.values() if r.get('status') == 'completed')}")
        logger.info(f"Modules Failed: {sum(1 for r in self.results.values() if r.get('status') == 'failed')}")
        
        return comprehensive_report
    
    def _generate_comprehensive_report(self, total_duration: float) -> Dict[str, Any]:
        """Generate comprehensive optimization report."""
        
        # Count completed vs failed modules
        completed_modules = [name for name, result in self.results.items() if result.get("status") == "completed"]
        failed_modules = [name for name, result in self.results.items() if result.get("status") == "failed"]
        
        # Aggregate recommendations
        all_recommendations = []
        for module_name, result in self.results.items():
            if result.get("status") == "completed" and "recommendations" in result:
                module_recs = [f"{module_name.title()}: {rec}" for rec in result["recommendations"]]
                all_recommendations.extend(module_recs)
        
        # Calculate overall success metrics
        success_rate = (len(completed_modules) / len(self.results)) * 100 if self.results else 0
        
        # Extract key performance metrics
        performance_summary = {}
        
        # Load testing metrics
        if "load_testing" in self.results and self.results["load_testing"].get("status") == "completed":
            load_summary = self.results["load_testing"]["summary"]
            performance_summary["load_testing"] = {
                "total_requests": load_summary.get("total_requests", 0),
                "success_rate": load_summary.get("overall_success_rate", 0),
                "requests_per_second": load_summary.get("overall_requests_per_second", 0)
            }
        
        # API optimization metrics
        if "api_optimization" in self.results and self.results["api_optimization"].get("status") == "completed":
            api_summary = self.results["api_optimization"]["summary"]
            performance_summary["api_optimization"] = {
                "endpoints_tested": api_summary.get("endpoints_tested", 0),
                "overall_improvement": api_summary.get("overall_improvement_percent", 0),
                "optimizations_applied": api_summary.get("optimizations_applied", 0)
            }
        
        # Database optimization metrics
        if "database_optimization" in self.results and self.results["database_optimization"].get("status") == "completed":
            db_summary = self.results["database_optimization"]["summary"]
            performance_summary["database_optimization"] = {
                "indexes_created": db_summary.get("indexes_created", 0),
                "queries_analyzed": db_summary.get("queries_analyzed", 0),
                "settings_applied": db_summary.get("settings_applied", 0)
            }
        
        # Redis optimization metrics
        if "redis_optimization" in self.results and self.results["redis_optimization"].get("status") == "completed":
            redis_summary = self.results["redis_optimization"]["summary"]
            redis_perf = self.results["redis_optimization"]["performance_metrics"]
            performance_summary["redis_optimization"] = {
                "operations_benchmarked": redis_summary.get("operations_benchmarked", 0),
                "success_rate": redis_perf.get("success_rate_percent", 0),
                "avg_response_time": redis_perf.get("avg_response_time_ms", 0),
                "streams_analyzed": redis_summary.get("streams_analyzed", 0)
            }
        
        # Generate executive summary
        executive_summary = self._generate_executive_summary(
            completed_modules, failed_modules, performance_summary
        )
        
        comprehensive_report = {
            "executive_summary": executive_summary,
            "optimization_suite_summary": {
                "total_duration_seconds": total_duration,
                "modules_executed": len(self.results),
                "modules_completed": len(completed_modules),
                "modules_failed": len(failed_modules),
                "overall_success_rate": success_rate,
                "execution_timestamp": datetime.now().isoformat()
            },
            "performance_summary": performance_summary,
            "module_results": self.results,
            "consolidated_recommendations": all_recommendations,
            "next_steps": self._generate_next_steps(completed_modules, failed_modules)
        }
        
        return comprehensive_report
    
    def _generate_executive_summary(self, completed_modules: List[str], 
                                  failed_modules: List[str],
                                  performance_summary: Dict[str, Any]) -> Dict[str, Any]:
        """Generate executive summary for stakeholders."""
        
        # Calculate key business metrics
        total_improvement_areas = len(completed_modules)
        critical_failures = len(failed_modules)
        
        # Extract key performance improvements
        improvements = []
        
        if "api_optimization" in performance_summary:
            api_improvement = performance_summary["api_optimization"].get("overall_improvement", 0)
            if api_improvement > 0:
                improvements.append(f"API response time improved by {api_improvement:.1f}%")
        
        if "load_testing" in performance_summary:
            success_rate = performance_summary["load_testing"].get("success_rate", 0)
            rps = performance_summary["load_testing"].get("requests_per_second", 0)
            improvements.append(f"System handles {rps:.0f} requests/second with {success_rate:.1f}% success rate")
        
        # Business impact assessment
        if success_rate := performance_summary.get("load_testing", {}).get("success_rate", 0):
            if success_rate >= 99:
                reliability_status = "EXCELLENT"
            elif success_rate >= 95:
                reliability_status = "GOOD"
            elif success_rate >= 90:
                reliability_status = "ACCEPTABLE"
            else:
                reliability_status = "NEEDS_IMPROVEMENT"
        else:
            reliability_status = "UNKNOWN"
        
        return {
            "optimization_status": "COMPLETED" if not failed_modules else "PARTIALLY_COMPLETED",
            "reliability_status": reliability_status,
            "business_impact": {
                "performance_improvements": improvements,
                "infrastructure_optimizations": total_improvement_areas,
                "critical_issues": critical_failures,
                "production_readiness": "READY" if not failed_modules and success_rate >= 95 else "REVIEW_REQUIRED"
            },
            "key_achievements": [
                f"Successfully optimized {len(completed_modules)} infrastructure components",
                f"Validated system performance under load",
                f"Generated actionable optimization recommendations",
                f"Established performance baseline for monitoring"
            ]
        }
    
    def _generate_next_steps(self, completed_modules: List[str], 
                           failed_modules: List[str]) -> List[str]:
        """Generate recommended next steps."""
        next_steps = []
        
        if failed_modules:
            next_steps.append(f"PRIORITY: Investigate and resolve failed optimization modules: {', '.join(failed_modules)}")
        
        if "load_testing" in completed_modules:
            next_steps.append("Deploy performance monitoring dashboards to track optimization results")
        
        if "api_optimization" in completed_modules:
            next_steps.append("Implement the most effective API optimization techniques in production")
        
        if "database_optimization" in completed_modules:
            next_steps.append("Schedule regular database performance reviews and index maintenance")
        
        if "redis_optimization" in completed_modules:
            next_steps.append("Monitor Redis memory usage and stream performance in production")
        
        # Always recommend ongoing monitoring
        next_steps.extend([
            "Establish performance SLA monitoring and alerting",
            "Schedule monthly performance optimization reviews",
            "Implement continuous performance testing in CI/CD pipeline",
            "Document performance optimization procedures for team knowledge transfer"
        ])
        
        return next_steps
    
    def save_comprehensive_report(self, report: Dict[str, Any], filename: str = None):
        """Save comprehensive optimization report."""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"comprehensive_performance_optimization_report_{timestamp}.json"
        
        # Ensure performance directory exists
        performance_dir = Path("performance")
        performance_dir.mkdir(exist_ok=True)
        
        filepath = performance_dir / filename
        
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        logger.info(f"📄 Comprehensive optimization report saved to: {filepath}")
        
        # Also create a summary report for quick review
        summary_filename = filepath.stem + "_executive_summary.json"
        summary_filepath = performance_dir / f"{summary_filename}.json"
        
        summary_report = {
            "executive_summary": report["executive_summary"],
            "optimization_suite_summary": report["optimization_suite_summary"],
            "performance_summary": report["performance_summary"],
            "consolidated_recommendations": report["consolidated_recommendations"][:10],  # Top 10
            "next_steps": report["next_steps"]
        }
        
        with open(summary_filepath, 'w') as f:
            json.dump(summary_report, f, indent=2, default=str)
        
        logger.info(f"📋 Executive summary saved to: {summary_filepath}")
    
    def print_results_summary(self, report: Dict[str, Any]):
        """Print comprehensive results summary."""
        print("\n" + "="*80)
        print("📊 COMPREHENSIVE PERFORMANCE OPTIMIZATION RESULTS")
        print("="*80)
        
        # Executive Summary
        exec_summary = report["executive_summary"]
        print(f"\n🎯 EXECUTIVE SUMMARY:")
        print(f"   Status: {exec_summary['optimization_status']}")
        print(f"   Reliability: {exec_summary['reliability_status']}")
        print(f"   Production Ready: {exec_summary['business_impact']['production_readiness']}")
        
        # Suite Summary
        suite_summary = report["optimization_suite_summary"]
        print(f"\n📈 OPTIMIZATION SUITE RESULTS:")
        print(f"   Duration: {suite_summary['total_duration_seconds']:.1f} seconds")
        print(f"   Modules Completed: {suite_summary['modules_completed']}/{suite_summary['modules_executed']}")
        print(f"   Success Rate: {suite_summary['overall_success_rate']:.1f}%")
        
        # Performance Summary
        print(f"\n⚡ PERFORMANCE ACHIEVEMENTS:")
        for achievement in exec_summary["key_achievements"]:
            print(f"   ✅ {achievement}")
        
        # Module Results
        print(f"\n🔧 MODULE RESULTS:")
        for module_name, result in report["module_results"].items():
            status_icon = "✅" if result["status"] == "completed" else "❌"
            print(f"   {status_icon} {module_name.replace('_', ' ').title()}: {result['status'].upper()}")
        
        # Top Recommendations
        print(f"\n🔍 TOP RECOMMENDATIONS:")
        for i, rec in enumerate(report["consolidated_recommendations"][:5], 1):
            print(f"   {i}. {rec}")
        
        # Next Steps
        print(f"\n🚀 IMMEDIATE NEXT STEPS:")
        for i, step in enumerate(report["next_steps"][:3], 1):
            print(f"   {i}. {step}")
        
        print("\n" + "="*80)

async def main():
    """Main function to run comprehensive performance optimization."""
    
    # Check if simple_gateway is running
    logger.info("🔍 Checking if AstraTrade enhanced gateway is running...")
    
    try:
        import aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:8000/health") as response:
                if response.status == 200:
                    logger.info("✅ Enhanced gateway is running and ready for optimization")
                else:
                    logger.warning("⚠️ Enhanced gateway responded but may have issues")
    except Exception as e:
        logger.error(f"❌ Cannot connect to enhanced gateway: {e}")
        logger.info("💡 Please start the enhanced gateway with: python3 simple_gateway.py")
        return
    
    # Run comprehensive optimization
    optimizer = ComprehensivePerformanceOptimizer()
    
    try:
        report = await optimizer.run_comprehensive_optimization()
        
        # Save comprehensive report
        optimizer.save_comprehensive_report(report)
        
        # Print results summary
        optimizer.print_results_summary(report)
        
        # Return success/failure based on results
        failed_modules = [name for name, result in report["module_results"].items() 
                         if result.get("status") == "failed"]
        
        if not failed_modules:
            logger.info("🎉 All optimization modules completed successfully!")
            return True
        else:
            logger.warning(f"⚠️ Some optimization modules failed: {', '.join(failed_modules)}")
            return False
    
    except Exception as e:
        logger.error(f"❌ Comprehensive optimization failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)