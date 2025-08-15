#!/usr/bin/env python3
"""
Cairo UMAS Workflow Templates
============================

Predefined workflow templates for common Cairo smart contract operations
using the Ultimate Multi-Agent System (UMAS).
"""

import sys
import os
import asyncio
import json
from typing import Dict, List, Any, Optional
from datetime import datetime

# Add UMAS path
umas_path = "/Users/admin/Claude Code Context llemur"
if umas_path not in sys.path:
    sys.path.insert(0, umas_path)

try:
    from src.ultimate_multi_agent_system import Task, TaskPriority
    UMAS_AVAILABLE = True
except ImportError:
    UMAS_AVAILABLE = False

class CairoWorkflowTemplates:
    """Cairo-specific workflow templates for UMAS"""
    
    def __init__(self):
        self.templates = {
            "cairo_security_audit": self.cairo_security_audit_workflow,
            "cairo_development_cycle": self.cairo_development_cycle_workflow,
            "cairo_safe_refactoring": self.cairo_safe_refactoring_workflow,
            "cairo_comprehensive_review": self.cairo_comprehensive_review_workflow,
            "cairo_expert_coordination": self.cairo_expert_coordination_workflow
        }
    
    async def cairo_security_audit_workflow(self, system, parameters: Dict) -> Dict:
        """
        Comprehensive Cairo security audit workflow
        
        Phases:
        1. Contract Discovery & Risk Profiling
        2. Parallel Security Analysis
        3. Vulnerability Assessment
        4. Remediation Planning
        5. Validation & Reporting
        """
        contracts = parameters.get("contracts", [])
        audit_type = parameters.get("audit_type", "full")
        severity_filter = parameters.get("severity_filter", "all")
        
        workflow_results = {
            "workflow": "cairo_security_audit",
            "phases": {},
            "summary": {},
            "recommendations": [],
            "timeline": datetime.now().isoformat()
        }
        
        try:
            # Phase 1: Contract Discovery & Risk Profiling
            discovery_task = Task(
                id=f"discovery_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                type="contract_discovery",
                description="Discover and profile Cairo contracts for security assessment",
                requirements={
                    "contracts": contracts,
                    "analysis_depth": "comprehensive",
                    "risk_factors": ["access_control", "reentrancy", "arithmetic", "oracle_dependency"]
                },
                priority=TaskPriority.HIGH
            )
            
            discovery_result = await system.coordinator.execute_task(discovery_task)
            workflow_results["phases"]["discovery"] = discovery_result
            
            # Phase 2: Parallel Security Analysis
            security_tasks = []
            
            # Access Control Analysis
            access_control_task = Task(
                id=f"access_control_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                type="access_control_analysis",
                description="Analyze access control patterns and vulnerabilities",
                requirements={
                    "contracts": contracts,
                    "focus_areas": ["role_management", "function_modifiers", "ownership_patterns"]
                },
                priority=TaskPriority.HIGH
            )
            security_tasks.append(access_control_task)
            
            # Reentrancy Analysis
            reentrancy_task = Task(
                id=f"reentrancy_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                type="reentrancy_detection",
                description="Detect potential reentrancy vulnerabilities",
                requirements={
                    "contracts": contracts,
                    "entry_points": discovery_result.get("entry_points", []) if discovery_result else [],
                    "external_calls": discovery_result.get("external_calls", []) if discovery_result else []
                },
                priority=TaskPriority.HIGH
            )
            security_tasks.append(reentrancy_task)
            
            # Arithmetic Safety Analysis
            arithmetic_task = Task(
                id=f"arithmetic_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                type="arithmetic_safety_check",
                description="Check arithmetic operations for overflow/underflow vulnerabilities",
                requirements={
                    "contracts": contracts,
                    "mathematical_operations": discovery_result.get("math_operations", []) if discovery_result else []
                },
                priority=TaskPriority.MEDIUM
            )
            security_tasks.append(arithmetic_task)
            
            # Execute security analysis tasks in parallel
            security_results = []
            for task in security_tasks:
                result = await system.coordinator.execute_task(task)
                security_results.append(result)
            
            workflow_results["phases"]["security_analysis"] = security_results
            
            # Phase 3: Vulnerability Assessment & Aggregation
            vulnerabilities = []
            risk_score = 0
            
            for result in security_results:
                if result and isinstance(result, dict):
                    if "vulnerabilities" in result:
                        vulnerabilities.extend(result["vulnerabilities"])
                    if "risk_score" in result:
                        risk_score += result["risk_score"]
                    if "access_issues" in result:
                        vulnerabilities.extend([
                            {
                                "type": "access_control",
                                "severity": issue.get("severity", "medium"),
                                "description": issue.get("issue", ""),
                                "location": issue.get("function", ""),
                                "remediation": issue.get("recommendation", "")
                            } for issue in result["access_issues"]
                        ])
            
            # Filter by severity if specified
            if severity_filter != "all":
                vulnerabilities = [v for v in vulnerabilities if v.get("severity") == severity_filter]
            
            workflow_results["phases"]["vulnerability_assessment"] = {
                "total_vulnerabilities": len(vulnerabilities),
                "risk_score": min(100, risk_score),
                "severity_breakdown": self._analyze_severity_breakdown(vulnerabilities),
                "vulnerabilities": vulnerabilities
            }
            
            # Phase 4: Remediation Planning
            remediation_task = Task(
                id=f"remediation_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                type="remediation_planning",
                description="Generate prioritized remediation plan",
                requirements={
                    "vulnerabilities": vulnerabilities,
                    "risk_score": risk_score,
                    "business_constraints": parameters.get("business_constraints", {})
                },
                priority=TaskPriority.MEDIUM
            )
            
            remediation_result = await system.coordinator.execute_task(remediation_task)
            workflow_results["phases"]["remediation_planning"] = remediation_result
            
            # Generate final recommendations
            recommendations = [
                f"Address {len([v for v in vulnerabilities if v.get('severity') == 'high'])} high-severity vulnerabilities immediately",
                f"Implement comprehensive access control review process",
                f"Add reentrancy protection to all external-facing functions",
                f"Conduct regular security audits (recommended: quarterly)"
            ]
            
            if risk_score > 70:
                recommendations.insert(0, "CRITICAL: Risk score exceeds acceptable threshold - immediate action required")
            
            workflow_results["recommendations"] = recommendations
            
            # Workflow summary
            workflow_results["summary"] = {
                "contracts_audited": len(contracts),
                "total_vulnerabilities": len(vulnerabilities),
                "critical_issues": len([v for v in vulnerabilities if v.get("severity") == "high"]),
                "risk_score": risk_score,
                "audit_type": audit_type,
                "completion_time": datetime.now().isoformat(),
                "next_audit_recommended": "3 months"
            }
            
            return workflow_results
            
        except Exception as e:
            workflow_results["error"] = str(e)
            workflow_results["status"] = "failed"
            return workflow_results
    
    async def cairo_development_cycle_workflow(self, system, parameters: Dict) -> Dict:
        """
        Complete Cairo development lifecycle workflow
        
        Phases:
        1. Requirements Analysis
        2. Architecture Design
        3. Code Generation
        4. Testing Strategy
        5. Performance Optimization
        6. Documentation Generation
        """
        specification = parameters.get("specification", "")
        requirements = parameters.get("requirements", {})
        constraints = parameters.get("constraints", {})
        
        workflow_results = {
            "workflow": "cairo_development_cycle",
            "phases": {},
            "artifacts": {},
            "timeline": datetime.now().isoformat()
        }
        
        try:
            # Phase 1: Requirements Analysis
            analysis_task = Task(
                id=f"requirements_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                type="requirements_analysis",
                description="Analyze and clarify development requirements",
                requirements={
                    "specification": specification,
                    "business_requirements": requirements,
                    "technical_constraints": constraints
                },
                priority=TaskPriority.HIGH
            )
            
            analysis_result = await system.coordinator.execute_task(analysis_task)
            workflow_results["phases"]["requirements_analysis"] = analysis_result
            
            # Phase 2: Architecture Design
            architecture_task = Task(
                id=f"architecture_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                type="architecture_review",
                description="Design Cairo contract architecture",
                requirements={
                    "requirements": analysis_result.get("clarified_requirements", {}) if analysis_result else {},
                    "focus_areas": ["modularity", "upgradeability", "gas_efficiency"],
                    "constraints": constraints
                },
                priority=TaskPriority.HIGH
            )
            
            architecture_result = await system.coordinator.execute_task(architecture_task)
            workflow_results["phases"]["architecture_design"] = architecture_result
            
            # Phase 3: Code Generation
            code_generation_task = Task(
                id=f"codegen_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                type="cairo_code_generation",
                description="Generate Cairo contract code",
                requirements={
                    "specification": specification,
                    "architecture": architecture_result.get("recommended_architecture", {}) if architecture_result else {},
                    "patterns": architecture_result.get("recommended_patterns", []) if architecture_result else [],
                    "constraints": constraints
                },
                priority=TaskPriority.HIGH
            )
            
            code_result = await system.coordinator.execute_task(code_generation_task)
            workflow_results["phases"]["code_generation"] = code_result
            
            # Phase 4: Testing Strategy
            testing_task = Task(
                id=f"testing_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                type="test_generation",
                description="Generate comprehensive testing strategy",
                requirements={
                    "contract_code": code_result.get("code", "") if code_result else "",
                    "functions": code_result.get("functions", []) if code_result else [],
                    "test_types": ["unit", "integration", "property", "security"]
                },
                priority=TaskPriority.MEDIUM
            )
            
            testing_result = await system.coordinator.execute_task(testing_task)
            workflow_results["phases"]["testing_strategy"] = testing_result
            
            # Phase 5: Performance Optimization
            optimization_task = Task(
                id=f"optimization_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                type="performance_testing",
                description="Optimize contract performance and gas usage",
                requirements={
                    "contract_code": code_result.get("code", "") if code_result else "",
                    "functions": code_result.get("functions", []) if code_result else [],
                    "gas_targets": constraints.get("gas_targets", {}),
                    "optimization_goals": ["gas_efficiency", "execution_speed", "storage_optimization"]
                },
                priority=TaskPriority.MEDIUM
            )
            
            optimization_result = await system.coordinator.execute_task(optimization_task)
            workflow_results["phases"]["performance_optimization"] = optimization_result
            
            # Generate artifacts
            workflow_results["artifacts"] = {
                "contract_code": code_result.get("code", "") if code_result else "",
                "test_suite": testing_result.get("test_suite", {}) if testing_result else {},
                "architecture_documentation": architecture_result.get("documentation", "") if architecture_result else "",
                "performance_benchmarks": optimization_result.get("gas_benchmarks", {}) if optimization_result else {},
                "deployment_guide": self._generate_deployment_guide(code_result, constraints)
            }
            
            return workflow_results
            
        except Exception as e:
            workflow_results["error"] = str(e)
            workflow_results["status"] = "failed"
            return workflow_results
    
    async def cairo_safe_refactoring_workflow(self, system, parameters: Dict) -> Dict:
        """
        Safe Cairo contract refactoring with impact analysis and rollback strategy
        """
        contract_code = parameters.get("contract_code", "")
        refactoring_goals = parameters.get("refactoring_goals", [])
        safety_constraints = parameters.get("safety_constraints", {})
        
        workflow_results = {
            "workflow": "cairo_safe_refactoring",
            "phases": {},
            "safety_measures": {},
            "timeline": datetime.now().isoformat()
        }
        
        try:
            # Phase 1: Pre-refactoring Analysis
            analysis_task = Task(
                id=f"pre_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                type="refactoring_analysis",
                description="Analyze refactoring requirements and risks",
                requirements={
                    "contract_code": contract_code,
                    "refactoring_goals": refactoring_goals,
                    "constraints": safety_constraints
                },
                priority=TaskPriority.HIGH
            )
            
            analysis_result = await system.coordinator.execute_task(analysis_task)
            workflow_results["phases"]["pre_analysis"] = analysis_result
            
            # Phase 2: Dependency Analysis
            dependency_task = Task(
                id=f"dependency_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                type="dependency_analysis",
                description="Analyze contract dependencies and coupling",
                requirements={
                    "contracts": [contract_code],
                    "target_changes": refactoring_goals
                },
                priority=TaskPriority.HIGH
            )
            
            dependency_result = await system.coordinator.execute_task(dependency_task)
            workflow_results["phases"]["dependency_analysis"] = dependency_result
            
            # Phase 3: Impact Assessment
            impact_assessment = {
                "breaking_changes_risk": self._assess_breaking_changes_risk(analysis_result, dependency_result),
                "affected_contracts": dependency_result.get("change_impact", []) if dependency_result else [],
                "testing_requirements": analysis_result.get("impact_assessment", {}).get("testing_requirements", []) if analysis_result else [],
                "rollback_complexity": "Medium"
            }
            workflow_results["phases"]["impact_assessment"] = impact_assessment
            
            # Phase 4: Rollback Strategy Generation
            rollback_task = Task(
                id=f"rollback_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                type="rollback_strategy",
                description="Generate rollback and recovery strategies",
                requirements={
                    "refactoring_plan": analysis_result.get("plan", {}) if analysis_result else {},
                    "critical_components": safety_constraints.get("critical_components", [])
                },
                priority=TaskPriority.HIGH
            )
            
            rollback_result = await system.coordinator.execute_task(rollback_task)
            workflow_results["phases"]["rollback_strategy"] = rollback_result
            
            # Phase 5: Safe Implementation Planning
            implementation_plan = self._generate_safe_implementation_plan(
                analysis_result,
                dependency_result, 
                rollback_result,
                safety_constraints
            )
            workflow_results["phases"]["implementation_plan"] = implementation_plan
            
            # Safety measures summary
            workflow_results["safety_measures"] = {
                "checkpoints_defined": len(rollback_result.get("checkpoints", [])) if rollback_result else 0,
                "rollback_procedures": rollback_result.get("rollback_plan", {}) if rollback_result else {},
                "risk_mitigation": analysis_result.get("risks", []) if analysis_result else [],
                "validation_requirements": implementation_plan.get("validation_steps", [])
            }
            
            return workflow_results
            
        except Exception as e:
            workflow_results["error"] = str(e)
            workflow_results["status"] = "failed"
            return workflow_results
    
    async def cairo_comprehensive_review_workflow(self, system, parameters: Dict) -> Dict:
        """
        Comprehensive Cairo contract review workflow combining multiple expert perspectives
        """
        contract_path = parameters.get("contract_path", "")
        review_focus = parameters.get("review_focus", ["architecture", "security", "performance", "quality"])
        
        workflow_results = {
            "workflow": "cairo_comprehensive_review",
            "expert_analyses": {},
            "consensus": {},
            "timeline": datetime.now().isoformat()
        }
        
        try:
            # Parallel expert reviews
            review_tasks = []
            
            # Architecture Review
            if "architecture" in review_focus:
                arch_task = Task(
                    id=f"arch_review_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    type="architecture_review",
                    description="Architecture and design pattern review",
                    requirements={
                        "contracts": [contract_path],
                        "focus_areas": ["design_patterns", "modularity", "coupling"],
                        "requirements": {}
                    },
                    priority=TaskPriority.HIGH
                )
                review_tasks.append(("architecture", arch_task))
            
            # Security Review
            if "security" in review_focus:
                security_task = Task(
                    id=f"security_review_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    type="cairo_security_audit",
                    description="Security vulnerability assessment",
                    requirements={
                        "contracts": [contract_path],
                        "audit_type": "comprehensive",
                        "severity_filter": "all"
                    },
                    priority=TaskPriority.HIGH
                )
                review_tasks.append(("security", security_task))
            
            # Performance Review
            if "performance" in review_focus:
                perf_task = Task(
                    id=f"perf_review_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    type="performance_testing",
                    description="Performance and gas optimization review",
                    requirements={
                        "contract_code": contract_path,
                        "functions": [],  # Will be populated from contract analysis
                        "gas_targets": {},
                        "optimization_goals": ["gas_efficiency", "storage_optimization"]
                    },
                    priority=TaskPriority.MEDIUM
                )
                review_tasks.append(("performance", perf_task))
            
            # Quality Review (Code Smells, Technical Debt)
            if "quality" in review_focus:
                quality_task = Task(
                    id=f"quality_review_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    type="code_smell_detection",
                    description="Code quality and technical debt analysis",
                    requirements={
                        "contract_files": [contract_path],
                        "analysis_depth": "comprehensive"
                    },
                    priority=TaskPriority.MEDIUM
                )
                review_tasks.append(("quality", quality_task))
            
            # Execute all reviews in parallel
            expert_results = {}
            for expert_type, task in review_tasks:
                result = await system.coordinator.execute_task(task)
                expert_results[expert_type] = result
            
            workflow_results["expert_analyses"] = expert_results
            
            # Generate consensus and recommendations
            consensus = self._generate_expert_consensus(expert_results)
            workflow_results["consensus"] = consensus
            
            return workflow_results
            
        except Exception as e:
            workflow_results["error"] = str(e)
            workflow_results["status"] = "failed"
            return workflow_results
    
    async def cairo_expert_coordination_workflow(self, system, parameters: Dict) -> Dict:
        """
        Multi-expert coordination workflow for complex Cairo queries
        """
        query = parameters.get("query", "")
        coordination_mode = parameters.get("mode", "collaborative")  # collaborative, consensus, validate
        
        workflow_results = {
            "workflow": "cairo_expert_coordination",
            "query_analysis": {},
            "expert_routing": {},
            "collaborative_analysis": {},
            "timeline": datetime.now().isoformat()
        }
        
        try:
            # Phase 1: Query Analysis and Expert Routing
            query_analysis = self._analyze_query_complexity(query)
            expert_routing = self._determine_expert_routing(query, query_analysis, coordination_mode)
            
            workflow_results["query_analysis"] = query_analysis
            workflow_results["expert_routing"] = expert_routing
            
            # Phase 2: Expert Consultation based on routing decision
            if expert_routing["strategy"] == "single_expert":
                # Route to single most qualified expert
                primary_expert = expert_routing["primary_expert"]
                task = Task(
                    id=f"expert_{primary_expert}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    type=self._get_expert_task_type(primary_expert),
                    description=f"{primary_expert} analysis for: {query}",
                    requirements=self._prepare_expert_requirements(query, primary_expert),
                    priority=TaskPriority.HIGH
                )
                
                result = await system.coordinator.execute_task(task)
                workflow_results["collaborative_analysis"] = {
                    "single_expert_result": result,
                    "confidence": expert_routing["confidence"]
                }
                
            elif expert_routing["strategy"] == "multi_expert":
                # Coordinate multiple experts
                expert_tasks = []
                for expert in expert_routing["experts"]:
                    task = Task(
                        id=f"expert_{expert}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                        type=self._get_expert_task_type(expert),
                        description=f"{expert} analysis for: {query}",
                        requirements=self._prepare_expert_requirements(query, expert),
                        priority=TaskPriority.HIGH
                    )
                    expert_tasks.append((expert, task))
                
                # Execute expert consultations in parallel
                expert_results = {}
                for expert, task in expert_tasks:
                    result = await system.coordinator.execute_task(task)
                    expert_results[expert] = result
                
                # Synthesize results
                synthesis = self._synthesize_expert_results(expert_results, coordination_mode)
                workflow_results["collaborative_analysis"] = {
                    "expert_results": expert_results,
                    "synthesis": synthesis,
                    "consensus_level": synthesis.get("consensus_level", "partial")
                }
            
            return workflow_results
            
        except Exception as e:
            workflow_results["error"] = str(e)
            workflow_results["status"] = "failed"
            return workflow_results
    
    # Helper methods
    
    def _analyze_severity_breakdown(self, vulnerabilities: List[Dict]) -> Dict:
        """Analyze vulnerability severity breakdown"""
        breakdown = {"high": 0, "medium": 0, "low": 0}
        for vuln in vulnerabilities:
            severity = vuln.get("severity", "low").lower()
            breakdown[severity] = breakdown.get(severity, 0) + 1
        return breakdown
    
    def _generate_deployment_guide(self, code_result: Dict, constraints: Dict) -> str:
        """Generate deployment guide"""
        if not code_result:
            return "Deployment guide not available - code generation failed"
        
        return """
# Cairo Contract Deployment Guide

## Prerequisites
- Starknet CLI installed and configured
- Account with sufficient funds for deployment
- Contract compiled and verified

## Deployment Steps
1. Compile contract: `starknet-compile contract.cairo --output contract.json`
2. Deploy contract: `starknet deploy --contract contract.json`
3. Verify deployment: Check contract address and initial state
4. Test basic functionality: Execute test transactions

## Post-deployment Checklist
- [ ] Contract functionality verified
- [ ] Access controls working correctly
- [ ] Events being emitted properly
- [ ] Integration with frontend/backend systems tested
"""
    
    def _assess_breaking_changes_risk(self, analysis_result: Dict, dependency_result: Dict) -> str:
        """Assess risk of breaking changes"""
        if not analysis_result or not dependency_result:
            return "Low"
        
        affected_contracts = dependency_result.get("change_impact", [])
        if len(affected_contracts) > 5:
            return "High"
        elif len(affected_contracts) > 2:
            return "Medium"
        else:
            return "Low"
    
    def _generate_safe_implementation_plan(self, analysis_result: Dict, dependency_result: Dict, 
                                         rollback_result: Dict, safety_constraints: Dict) -> Dict:
        """Generate safe implementation plan"""
        return {
            "phases": [
                {
                    "phase": 1,
                    "name": "Preparation and Testing",
                    "tasks": ["Create feature branch", "Implement changes", "Run unit tests"],
                    "validation_steps": ["All tests pass", "Code review completed"]
                },
                {
                    "phase": 2, 
                    "name": "Integration Testing",
                    "tasks": ["Deploy to testnet", "Run integration tests", "Performance testing"],
                    "validation_steps": ["Integration tests pass", "Performance benchmarks met"]
                },
                {
                    "phase": 3,
                    "name": "Production Deployment", 
                    "tasks": ["Deploy to mainnet", "Monitor system health", "Gradual rollout"],
                    "validation_steps": ["Deployment successful", "No critical errors", "User feedback positive"]
                }
            ],
            "safety_gates": [
                "All tests must pass before progression",
                "Performance must meet or exceed current benchmarks", 
                "No critical security issues",
                "Rollback procedures tested and ready"
            ]
        }
    
    def _generate_expert_consensus(self, expert_results: Dict) -> Dict:
        """Generate consensus from multiple expert analyses"""
        consensus = {
            "agreement_level": "high",  # high, medium, low
            "key_findings": [],
            "conflicting_opinions": [],
            "final_recommendations": []
        }
        
        # Analyze agreement between experts
        all_recommendations = []
        for expert, result in expert_results.items():
            if result and isinstance(result, dict):
                recommendations = result.get("recommendations", [])
                all_recommendations.extend([(expert, rec) for rec in recommendations])
        
        # Find common recommendations
        recommendation_counts = {}
        for expert, recommendation in all_recommendations:
            if isinstance(recommendation, str):
                recommendation_counts[recommendation] = recommendation_counts.get(recommendation, 0) + 1
        
        # Recommendations mentioned by multiple experts
        consensus["key_findings"] = [
            rec for rec, count in recommendation_counts.items() if count > 1
        ]
        
        # Generate final recommendations
        consensus["final_recommendations"] = [
            "Implement security best practices identified by multiple experts",
            "Address performance concerns raised in analysis",
            "Follow architectural recommendations for better maintainability"
        ]
        
        return consensus
    
    def _analyze_query_complexity(self, query: str) -> Dict:
        """Analyze query complexity and classification"""
        complexity_score = min(100, len(query.split()) * 2)  # Simplified scoring
        
        # Classify query intent
        intent_keywords = {
            "security": ["security", "vulnerability", "attack", "exploit", "audit"],
            "development": ["implement", "code", "function", "contract", "develop"],
            "architecture": ["design", "architecture", "pattern", "structure", "system"],
            "performance": ["optimize", "gas", "performance", "efficiency", "speed"],
            "refactoring": ["refactor", "improve", "restructure", "cleanup", "technical debt"]
        }
        
        intents = []
        query_lower = query.lower()
        for intent, keywords in intent_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                intents.append(intent)
        
        return {
            "complexity_score": complexity_score,
            "complexity_level": "high" if complexity_score > 70 else "medium" if complexity_score > 30 else "low",
            "identified_intents": intents,
            "multi_domain": len(intents) > 1,
            "query_clarity": "high" if len(query.split()) > 5 else "medium"
        }
    
    def _determine_expert_routing(self, query: str, analysis: Dict, mode: str) -> Dict:
        """Determine expert routing strategy"""
        complexity_level = analysis.get("complexity_level", "low")
        intents = analysis.get("identified_intents", [])
        
        if complexity_level == "low" and len(intents) == 1:
            # Single expert, high confidence
            primary_expert = intents[0] if intents else "development"
            return {
                "strategy": "single_expert",
                "primary_expert": primary_expert,
                "confidence": 0.9,
                "reasoning": f"Simple query with clear {primary_expert} focus"
            }
        elif mode == "collaborative" or len(intents) > 1:
            # Multi-expert collaboration
            experts = intents if intents else ["development", "security"]
            return {
                "strategy": "multi_expert",
                "experts": experts[:3],  # Limit to 3 experts max
                "coordination_approach": "parallel_analysis",
                "reasoning": f"Complex query requiring {len(experts)} expert perspectives"
            }
        else:
            # Conservative approach - single expert with validation
            primary_expert = intents[0] if intents else "development"
            return {
                "strategy": "single_expert",
                "primary_expert": primary_expert,
                "confidence": 0.7,
                "reasoning": f"Moderate complexity {primary_expert} query"
            }
    
    def _get_expert_task_type(self, expert: str) -> str:
        """Map expert type to task type"""
        task_mapping = {
            "security": "cairo_security_audit",
            "development": "cairo_code_generation", 
            "architecture": "architecture_review",
            "performance": "performance_testing",
            "refactoring": "refactoring_analysis"
        }
        return task_mapping.get(expert, "cairo_code_generation")
    
    def _prepare_expert_requirements(self, query: str, expert: str) -> Dict:
        """Prepare requirements for specific expert"""
        base_requirements = {
            "query": query,
            "analysis_depth": "comprehensive",
            "context": "AstraTrade Cairo smart contracts"
        }
        
        expert_specific = {
            "security": {
                "contracts": [],  # Will be populated from query analysis
                "audit_type": "targeted",
                "severity_filter": "all"
            },
            "development": {
                "specification": query,
                "patterns": ["access_control", "upgradeability", "gas_optimization"],
                "constraints": {}
            },
            "architecture": {
                "contracts": [],
                "focus_areas": ["design_patterns", "modularity", "scalability"],
                "requirements": {}
            },
            "performance": {
                "functions": [],
                "gas_targets": {},
                "optimization_goals": ["gas_efficiency", "execution_speed"]
            },
            "refactoring": {
                "contract_code": "",
                "refactoring_goals": [query],
                "constraints": {}
            }
        }
        
        base_requirements.update(expert_specific.get(expert, {}))
        return base_requirements
    
    def _synthesize_expert_results(self, expert_results: Dict, coordination_mode: str) -> Dict:
        """Synthesize results from multiple experts"""
        synthesis = {
            "consensus_level": "high",
            "agreed_recommendations": [],
            "conflicting_viewpoints": [],
            "final_recommendation": "",
            "confidence_score": 0.0
        }
        
        # Extract all recommendations
        all_recommendations = []
        confidence_scores = []
        
        for expert, result in expert_results.items():
            if result and isinstance(result, dict):
                recommendations = result.get("recommendations", [])
                confidence = result.get("confidence_score", 0.7)
                
                all_recommendations.extend(recommendations)
                confidence_scores.append(confidence)
        
        # Calculate average confidence
        if confidence_scores:
            synthesis["confidence_score"] = sum(confidence_scores) / len(confidence_scores)
        
        # Find common themes in recommendations
        recommendation_frequency = {}
        for rec in all_recommendations:
            if isinstance(rec, str):
                # Simple keyword-based grouping
                key_words = rec.lower().split()[:3]  # First 3 words as key
                key = " ".join(key_words)
                recommendation_frequency[key] = recommendation_frequency.get(key, 0) + 1
        
        # Recommendations mentioned by multiple experts
        synthesis["agreed_recommendations"] = [
            key for key, freq in recommendation_frequency.items() if freq > 1
        ]
        
        # Determine consensus level
        if len(synthesis["agreed_recommendations"]) >= len(expert_results):
            synthesis["consensus_level"] = "high"
        elif len(synthesis["agreed_recommendations"]) >= len(expert_results) // 2:
            synthesis["consensus_level"] = "medium"
        else:
            synthesis["consensus_level"] = "low"
        
        # Generate final recommendation
        if coordination_mode == "consensus" and synthesis["consensus_level"] == "low":
            synthesis["final_recommendation"] = "Experts disagree - request clarification or additional analysis"
        else:
            synthesis["final_recommendation"] = f"Proceed with implementation focusing on: {', '.join(synthesis['agreed_recommendations'][:3])}"
        
        return synthesis

# Global workflow templates instance
cairo_workflows = CairoWorkflowTemplates()

def get_cairo_workflow_templates() -> CairoWorkflowTemplates:
    """Get global Cairo workflow templates instance"""
    return cairo_workflows

# Convenience functions
async def execute_cairo_security_audit(system, contracts: List[str], audit_type: str = "full") -> Dict:
    """Execute Cairo security audit workflow"""
    return await cairo_workflows.cairo_security_audit_workflow(system, {
        "contracts": contracts,
        "audit_type": audit_type,
        "severity_filter": "all"
    })

async def execute_cairo_development_cycle(system, specification: str, requirements: Dict = None) -> Dict:
    """Execute Cairo development cycle workflow"""
    return await cairo_workflows.cairo_development_cycle_workflow(system, {
        "specification": specification,
        "requirements": requirements or {},
        "constraints": {}
    })

async def execute_cairo_safe_refactoring(system, contract_code: str, goals: List[str]) -> Dict:
    """Execute safe Cairo refactoring workflow"""
    return await cairo_workflows.cairo_safe_refactoring_workflow(system, {
        "contract_code": contract_code,
        "refactoring_goals": goals,
        "safety_constraints": {}
    })

async def execute_cairo_expert_coordination(system, query: str, mode: str = "collaborative") -> Dict:
    """Execute Cairo expert coordination workflow"""
    return await cairo_workflows.cairo_expert_coordination_workflow(system, {
        "query": query,
        "mode": mode
    })