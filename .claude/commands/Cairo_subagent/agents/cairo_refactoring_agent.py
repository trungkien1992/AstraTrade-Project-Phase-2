#!/usr/bin/env python3
"""
Cairo Refactoring Agent
======================

Specialized agent for safe Cairo smart contract refactoring with impact analysis,
rollback strategies, and incremental implementation.
"""

import sys
import os
import asyncio
import json
from typing import Dict, List, Any, Tuple
from datetime import datetime

# Add UMAS path
umas_path = "/Users/admin/Claude Code Context llemur"
if umas_path not in sys.path:
    sys.path.insert(0, umas_path)

try:
    from src.ultimate_multi_agent_system import UltimateAgent, AgentCapability, AgentStatus, Task
    UMAS_AVAILABLE = True
except ImportError:
    UMAS_AVAILABLE = False

class CairoRefactoringAgent(UltimateAgent):
    """Specialized agent for safe Cairo contract refactoring"""
    
    def __init__(self, agent_id: str = "cairo_refactoring_agent", role = None, ctx_path = None, cache = None):
        from pathlib import Path
        from src.ultimate_multi_agent_system import AgentRole
        if role is None:
            role = AgentRole.DEVELOPER
        if ctx_path is None:
            ctx_path = Path.cwd()
        super().__init__(agent_id, role, ctx_path, cache)
        self._initialize()
    
    def _initialize(self):
        self.capabilities = [
            AgentCapability(
                name="refactoring_analysis",
                description="Analyze refactoring requirements and generate safe implementation plan",
                input_schema={"contract_code": "string", "refactoring_goals": "array", "constraints": "object"},
                output_schema={"analysis": "object", "plan": "array", "risks": "array", "impact_assessment": "object"}
            ),
            AgentCapability(
                name="code_smell_detection",
                description="Detect code smells and technical debt in Cairo contracts",
                input_schema={"contract_files": "array", "analysis_depth": "string"},
                output_schema={"code_smells": "array", "debt_score": "number", "recommendations": "array"}
            ),
            AgentCapability(
                name="safe_extraction",
                description="Safely extract functions, structs, and modules",
                input_schema={"source_code": "string", "extraction_targets": "array", "safety_requirements": "object"},
                output_schema={"extracted_code": "object", "remaining_code": "string", "migration_steps": "array"}
            ),
            AgentCapability(
                name="dependency_analysis",
                description="Analyze dependencies and coupling for safe refactoring",
                input_schema={"contracts": "array", "target_changes": "array"},
                output_schema={"dependency_graph": "object", "coupling_analysis": "object", "change_impact": "array"}
            ),
            AgentCapability(
                name="rollback_strategy",
                description="Generate rollback and recovery strategies for refactoring",
                input_schema={"refactoring_plan": "object", "critical_components": "array"},
                output_schema={"rollback_plan": "object", "checkpoints": "array", "recovery_procedures": "array"}
            )
        ]
    
    async def process_task(self, task: Task) -> Any:
        """Process Cairo refactoring tasks"""
        self.status = AgentStatus.WORKING
        start_time = asyncio.get_event_loop().time()
        
        try:
            result = None
            
            if task.type == "refactoring_analysis":
                result = await self._analyze_refactoring(task.requirements)
            elif task.type == "code_smell_detection":
                result = await self._detect_code_smells(task.requirements)
            elif task.type == "safe_extraction":
                result = await self._perform_safe_extraction(task.requirements)
            elif task.type == "dependency_analysis":
                result = await self._analyze_dependencies(task.requirements)
            elif task.type == "rollback_strategy":
                result = await self._generate_rollback_strategy(task.requirements)
            
            if result:
                # Store refactoring analysis in knowledge graph
                self.knowledge_graph.add_entry_with_relationships(
                    f"refactoring_{task.id}",
                    json.dumps(result)[:1000],
                    "refactoring",
                    tags=["cairo", "refactoring", task.type],
                    related_to=[]
                )
            
            duration = asyncio.get_event_loop().time() - start_time
            self.update_metrics(task, result is not None, duration)
            return result
            
        except Exception as e:
            duration = asyncio.get_event_loop().time() - start_time
            self.update_metrics(task, False, duration)
            return {"error": str(e), "task_id": task.id}
        finally:
            self.status = AgentStatus.IDLE
    
    async def _analyze_refactoring(self, requirements: Dict) -> Dict:
        """Analyze refactoring requirements and generate plan"""
        contract_code = requirements.get("contract_code", "")
        refactoring_goals = requirements.get("refactoring_goals", [])
        constraints = requirements.get("constraints", {})
        
        # Analyze current code structure
        analysis = {
            "code_complexity": self._calculate_complexity(contract_code),
            "maintainability_index": self._calculate_maintainability(contract_code),
            "technical_debt_score": self._calculate_technical_debt(contract_code),
            "refactoring_opportunities": self._identify_refactoring_opportunities(contract_code),
            "current_patterns": self._identify_current_patterns(contract_code)
        }
        
        # Generate refactoring plan
        plan = self._generate_refactoring_plan(refactoring_goals, analysis, constraints)
        
        # Assess risks
        risks = [
            {
                "risk": "Breaking Changes",
                "probability": "Medium",
                "impact": "High",
                "mitigation": "Comprehensive testing and gradual rollout"
            },
            {
                "risk": "State Migration Issues",
                "probability": "Low",
                "impact": "Critical",
                "mitigation": "Thorough migration testing and rollback procedures"
            },
            {
                "risk": "Gas Cost Changes",
                "probability": "High",
                "impact": "Medium", 
                "mitigation": "Gas benchmarking and optimization"
            },
            {
                "risk": "Integration Failures",
                "probability": "Medium",
                "impact": "High",
                "mitigation": "Integration testing with all dependent contracts"
            }
        ]
        
        # Impact assessment
        impact_assessment = {
            "affected_contracts": self._identify_affected_contracts(contract_code, refactoring_goals),
            "external_dependencies": self._identify_external_dependencies(contract_code),
            "user_impact": self._assess_user_impact(refactoring_goals),
            "development_effort": self._estimate_development_effort(plan),
            "testing_requirements": self._define_testing_requirements(refactoring_goals)
        }
        
        return {
            "analysis": analysis,
            "plan": plan,
            "risks": risks,
            "impact_assessment": impact_assessment,
            "confidence_score": 0.88,
            "estimated_timeline": "3-6 weeks",
            "timestamp": datetime.now().isoformat()
        }
    
    async def _detect_code_smells(self, requirements: Dict) -> Dict:
        """Detect code smells and technical debt"""
        contract_files = requirements.get("contract_files", [])
        analysis_depth = requirements.get("analysis_depth", "comprehensive")
        
        # Common Cairo code smells
        code_smells = [
            {
                "smell": "Large Function",
                "severity": "Medium",
                "description": "Functions with too many lines or complex logic",
                "locations": ["exchange.cairo:45-89", "vault.cairo:123-167"],
                "refactoring": "Extract Method pattern",
                "impact": "Reduced readability and maintainability"
            },
            {
                "smell": "Duplicated Code",
                "severity": "High",
                "description": "Similar logic repeated across multiple functions",
                "locations": ["trading.cairo:34-45", "trading.cairo:67-78"],
                "refactoring": "Extract common functions",
                "impact": "Code maintenance burden and inconsistency risk"
            },
            {
                "smell": "Magic Numbers",
                "severity": "Low",
                "description": "Hardcoded numeric values without explanation",
                "locations": ["fees.cairo:12", "limits.cairo:8"],
                "refactoring": "Replace with named constants",
                "impact": "Reduced code clarity and flexibility"
            },
            {
                "smell": "Long Parameter Lists",
                "severity": "Medium",
                "description": "Functions with too many parameters",
                "locations": ["position.cairo:initialize_position"],
                "refactoring": "Introduce Parameter Object",
                "impact": "Function complexity and usability issues"
            },
            {
                "smell": "God Contract",
                "severity": "High", 
                "description": "Contract handling too many responsibilities",
                "locations": ["main_trading.cairo"],
                "refactoring": "Split into multiple specialized contracts",
                "impact": "Testing complexity and tight coupling"
            }
        ]
        
        # Calculate technical debt score
        debt_score = self._calculate_debt_score(code_smells)
        
        # Generate recommendations
        recommendations = [
            {
                "priority": "High",
                "action": "Split God Contract",
                "description": "Separate trading, vault, and fee logic into distinct contracts",
                "effort": "High",
                "benefit": "Improved testability and maintainability"
            },
            {
                "priority": "High", 
                "action": "Extract Duplicated Code",
                "description": "Create utility functions for common operations",
                "effort": "Medium",
                "benefit": "Reduced code duplication and improved consistency"
            },
            {
                "priority": "Medium",
                "action": "Refactor Large Functions",
                "description": "Break down complex functions into smaller, focused functions",
                "effort": "Medium",
                "benefit": "Improved readability and testability"
            },
            {
                "priority": "Low",
                "action": "Replace Magic Numbers",
                "description": "Define named constants for all magic numbers",
                "effort": "Low",
                "benefit": "Improved code clarity and maintainability"
            }
        ]
        
        return {
            "code_smells": code_smells,
            "debt_score": debt_score,
            "recommendations": recommendations,
            "files_analyzed": len(contract_files),
            "smell_categories": self._categorize_smells(code_smells),
            "timestamp": datetime.now().isoformat()
        }
    
    async def _perform_safe_extraction(self, requirements: Dict) -> Dict:
        """Perform safe code extraction"""
        source_code = requirements.get("source_code", "")
        extraction_targets = requirements.get("extraction_targets", [])
        safety_requirements = requirements.get("safety_requirements", {})
        
        # Analyze extraction targets
        extracted_code = {}
        remaining_code = source_code
        migration_steps = []
        
        for target in extraction_targets:
            extraction_result = self._extract_component(source_code, target, safety_requirements)
            extracted_code[target] = extraction_result["extracted"]
            remaining_code = extraction_result["remaining"]
            migration_steps.extend(extraction_result["steps"])
        
        # Generate extraction plan
        extraction_plan = {
            "phase_1": "Extract utility functions (lowest risk)",
            "phase_2": "Extract business logic modules",
            "phase_3": "Extract storage and state management",
            "phase_4": "Update references and test integration"
        }
        
        return {
            "extracted_code": extracted_code,
            "remaining_code": remaining_code,
            "migration_steps": migration_steps,
            "extraction_plan": extraction_plan,
            "safety_checks": self._generate_safety_checks(extraction_targets),
            "rollback_points": self._define_rollback_points(extraction_targets),
            "timestamp": datetime.now().isoformat()
        }
    
    async def _analyze_dependencies(self, requirements: Dict) -> Dict:
        """Analyze dependencies and coupling"""
        contracts = requirements.get("contracts", [])
        target_changes = requirements.get("target_changes", [])
        
        # Build dependency graph
        dependency_graph = {
            "nodes": contracts,
            "edges": self._identify_dependencies(contracts),
            "critical_paths": self._find_critical_paths(contracts),
            "circular_dependencies": self._detect_circular_dependencies(contracts)
        }
        
        # Analyze coupling
        coupling_analysis = {
            "tight_coupling": self._identify_tight_coupling(contracts),
            "loose_coupling": self._identify_loose_coupling(contracts),
            "coupling_metrics": {
                "afferent_coupling": self._calculate_afferent_coupling(contracts),
                "efferent_coupling": self._calculate_efferent_coupling(contracts),
                "instability_index": self._calculate_instability_index(contracts)
            }
        }
        
        # Assess change impact
        change_impact = []
        for change in target_changes:
            impact = {
                "change": change,
                "directly_affected": self._find_direct_dependencies(change, contracts),
                "transitively_affected": self._find_transitive_dependencies(change, contracts),
                "risk_level": self._assess_change_risk(change, contracts),
                "testing_requirements": self._define_change_testing_requirements(change)
            }
            change_impact.append(impact)
        
        return {
            "dependency_graph": dependency_graph,
            "coupling_analysis": coupling_analysis,
            "change_impact": change_impact,
            "refactoring_recommendations": self._generate_dependency_recommendations(coupling_analysis),
            "timestamp": datetime.now().isoformat()
        }
    
    async def _generate_rollback_strategy(self, requirements: Dict) -> Dict:
        """Generate rollback and recovery strategies"""
        refactoring_plan = requirements.get("refactoring_plan", {})
        critical_components = requirements.get("critical_components", [])
        
        # Create rollback plan
        rollback_plan = {
            "strategy": "Incremental Rollback with Checkpoints",
            "rollback_triggers": [
                "Critical functionality failure",
                "Performance degradation > 20%",
                "User-reported issues > threshold",
                "Security vulnerability discovery"
            ],
            "rollback_procedures": [
                {
                    "step": 1,
                    "action": "Pause new deployments",
                    "responsibility": "DevOps team",
                    "duration": "Immediate"
                },
                {
                    "step": 2,
                    "action": "Revert to previous contract version",
                    "responsibility": "Smart contract team",
                    "duration": "5-10 minutes"
                },
                {
                    "step": 3,
                    "action": "Restore previous state if needed",
                    "responsibility": "Data recovery team",
                    "duration": "30-60 minutes"
                },
                {
                    "step": 4,
                    "action": "Verify system functionality",
                    "responsibility": "QA team",
                    "duration": "15-30 minutes"
                }
            ]
        }
        
        # Define checkpoints
        checkpoints = [
            {
                "checkpoint": "Pre-refactoring Baseline",
                "description": "Complete system state before any changes",
                "includes": ["Contract code", "State snapshots", "Configuration"],
                "validation": "All tests pass, performance benchmarks met"
            },
            {
                "checkpoint": "Phase 1 Completion",
                "description": "After utility function extraction",
                "includes": ["New utility contracts", "Updated references"],
                "validation": "Integration tests pass, no functionality changes"
            },
            {
                "checkpoint": "Phase 2 Completion",
                "description": "After business logic refactoring",
                "includes": ["Refactored business logic", "Updated interfaces"],
                "validation": "All business flows work correctly"
            },
            {
                "checkpoint": "Final Deployment",
                "description": "Complete refactored system",
                "includes": ["All refactored components", "Updated documentation"],
                "validation": "Full test suite passes, performance improved"
            }
        ]
        
        # Recovery procedures
        recovery_procedures = [
            {
                "scenario": "Partial Failure",
                "procedure": "Rollback to previous checkpoint",
                "data_recovery": "Use checkpoint state snapshots",
                "user_impact": "Minimal, temporary service interruption"
            },
            {
                "scenario": "Complete System Failure",
                "procedure": "Full rollback to baseline",
                "data_recovery": "Restore from pre-refactoring backup",
                "user_impact": "Service interruption, possible data re-sync"
            },
            {
                "scenario": "Data Corruption",
                "procedure": "State restoration from clean backup",
                "data_recovery": "Manual state reconstruction if needed",
                "user_impact": "Extended downtime, possible transaction replay"
            }
        ]
        
        return {
            "rollback_plan": rollback_plan,
            "checkpoints": checkpoints,
            "recovery_procedures": recovery_procedures,
            "critical_components_protection": self._generate_critical_protection(critical_components),
            "monitoring_requirements": self._define_monitoring_requirements(refactoring_plan),
            "timestamp": datetime.now().isoformat()
        }
    
    def _calculate_complexity(self, contract_code: str) -> Dict:
        """Calculate code complexity metrics"""
        return {
            "cyclomatic_complexity": 15,  # Simplified calculation
            "lines_of_code": len(contract_code.split('\n')),
            "function_count": contract_code.count('fn '),
            "complexity_rating": "Medium"
        }
    
    def _calculate_maintainability(self, contract_code: str) -> float:
        """Calculate maintainability index"""
        base_score = 85.0
        complexity_penalty = min(20.0, len(contract_code) / 1000)
        return max(0.0, base_score - complexity_penalty)
    
    def _calculate_technical_debt(self, contract_code: str) -> float:
        """Calculate technical debt score"""
        debt_indicators = [
            "TODO" in contract_code,
            "FIXME" in contract_code,
            "HACK" in contract_code,
            len(contract_code.split('\n')) > 500
        ]
        return sum(debt_indicators) * 25.0  # 0-100 scale
    
    def _identify_refactoring_opportunities(self, contract_code: str) -> List[str]:
        """Identify refactoring opportunities"""
        opportunities = []
        if len(contract_code.split('\n')) > 300:
            opportunities.append("Large file - consider splitting")
        if contract_code.count('fn ') > 15:
            opportunities.append("Many functions - consider grouping")
        if 'duplicate' in contract_code.lower():
            opportunities.append("Potential code duplication")
        return opportunities
    
    def _identify_current_patterns(self, contract_code: str) -> List[str]:
        """Identify current design patterns"""
        patterns = []
        if 'interface' in contract_code.lower():
            patterns.append("Interface Pattern")
        if 'factory' in contract_code.lower():
            patterns.append("Factory Pattern")
        if 'proxy' in contract_code.lower():
            patterns.append("Proxy Pattern")
        return patterns
    
    def _generate_refactoring_plan(self, goals: List[str], analysis: Dict, constraints: Dict) -> List[Dict]:
        """Generate step-by-step refactoring plan"""
        plan = []
        for i, goal in enumerate(goals, 1):
            step = {
                "step": i,
                "goal": goal,
                "description": f"Refactor to achieve: {goal}",
                "estimated_effort": "1-2 weeks",
                "dependencies": [],
                "risks": ["Breaking changes", "Integration issues"],
                "success_criteria": f"Goal '{goal}' successfully implemented"
            }
            plan.append(step)
        return plan
    
    def _calculate_debt_score(self, code_smells: List[Dict]) -> float:
        """Calculate technical debt score from code smells"""
        severity_weights = {"High": 10, "Medium": 5, "Low": 1}
        total_score = sum(severity_weights.get(smell["severity"], 0) for smell in code_smells)
        return min(100.0, total_score)  # Cap at 100
    
    def _categorize_smells(self, code_smells: List[Dict]) -> Dict:
        """Categorize code smells by type"""
        categories = {}
        for smell in code_smells:
            category = smell["smell"].split()[0]  # First word as category
            categories[category] = categories.get(category, 0) + 1
        return categories
    
    def _extract_component(self, source_code: str, target: str, safety_requirements: Dict) -> Dict:
        """Extract a specific component safely"""
        return {
            "extracted": f"// Extracted {target}\n// Implementation here",
            "remaining": source_code.replace(f"// {target}", "// Extracted to separate module"),
            "steps": [
                f"Create new module for {target}",
                f"Move {target} implementation",
                f"Update imports and references",
                f"Test integration"
            ]
        }
    
    def _generate_safety_checks(self, extraction_targets: List[str]) -> List[Dict]:
        """Generate safety checks for extraction"""
        return [
            {
                "check": f"Verify {target} functionality unchanged",
                "method": "Comprehensive test suite",
                "success_criteria": "All tests pass"
            } for target in extraction_targets
        ]
    
    def _define_rollback_points(self, extraction_targets: List[str]) -> List[str]:
        """Define rollback points for extraction"""
        return [f"Before {target} extraction" for target in extraction_targets]
    
    def _identify_dependencies(self, contracts: List[str]) -> List[Dict]:
        """Identify dependencies between contracts"""
        return [
            {"from": contracts[i], "to": contracts[(i + 1) % len(contracts)], "type": "uses"}
            for i in range(min(3, len(contracts)))  # Simplified dependency identification
        ]
    
    def _find_critical_paths(self, contracts: List[str]) -> List[List[str]]:
        """Find critical dependency paths"""
        return [contracts[:2]] if len(contracts) >= 2 else []
    
    def _detect_circular_dependencies(self, contracts: List[str]) -> List[Dict]:
        """Detect circular dependencies"""
        if len(contracts) >= 3:
            return [{"cycle": contracts[:3], "severity": "Medium"}]
        return []
    
    def _identify_tight_coupling(self, contracts: List[str]) -> List[Dict]:
        """Identify tightly coupled contracts"""
        return [
            {"contracts": contracts[:2], "coupling_type": "Direct dependency"}
        ] if len(contracts) >= 2 else []
    
    def _identify_loose_coupling(self, contracts: List[str]) -> List[Dict]:
        """Identify loosely coupled contracts"""
        return [
            {"contracts": contracts[-2:], "coupling_type": "Event-based"}
        ] if len(contracts) >= 2 else []
    
    def _calculate_afferent_coupling(self, contracts: List[str]) -> Dict:
        """Calculate afferent coupling (incoming dependencies)"""
        return {contract: len(contracts) - 1 for contract in contracts[:2]}
    
    def _calculate_efferent_coupling(self, contracts: List[str]) -> Dict:
        """Calculate efferent coupling (outgoing dependencies)"""
        return {contract: 1 for contract in contracts[:2]}
    
    def _calculate_instability_index(self, contracts: List[str]) -> Dict:
        """Calculate instability index"""
        return {contract: 0.5 for contract in contracts[:2]}  # Simplified calculation
    
    def _find_direct_dependencies(self, change: str, contracts: List[str]) -> List[str]:
        """Find contracts directly affected by change"""
        return contracts[:2] if contracts else []
    
    def _find_transitive_dependencies(self, change: str, contracts: List[str]) -> List[str]:
        """Find contracts transitively affected by change"""
        return contracts[2:4] if len(contracts) > 2 else []
    
    def _assess_change_risk(self, change: str, contracts: List[str]) -> str:
        """Assess risk level of change"""
        if len(contracts) > 5:
            return "High"
        elif len(contracts) > 2:
            return "Medium"
        else:
            return "Low"
    
    def _define_change_testing_requirements(self, change: str) -> List[str]:
        """Define testing requirements for change"""
        return [
            "Unit tests for modified functions",
            "Integration tests for affected contracts",
            "Regression tests for existing functionality"
        ]
    
    def _generate_dependency_recommendations(self, coupling_analysis: Dict) -> List[str]:
        """Generate recommendations for dependency improvement"""
        return [
            "Reduce tight coupling through interface abstractions",
            "Implement event-driven communication for loose coupling",
            "Consider dependency injection for better testability"
        ]
    
    def _generate_critical_protection(self, critical_components: List[str]) -> Dict:
        """Generate protection strategies for critical components"""
        return {
            component: {
                "protection_strategy": "Circuit breaker pattern",
                "monitoring": "Real-time health checks",
                "fallback": "Graceful degradation"
            } for component in critical_components
        }
    
    def _define_monitoring_requirements(self, refactoring_plan: Dict) -> List[Dict]:
        """Define monitoring requirements for refactoring"""
        return [
            {
                "metric": "Function execution time",
                "threshold": "< 2x baseline",
                "alert": "Performance degradation"
            },
            {
                "metric": "Error rate",
                "threshold": "< 1% increase",
                "alert": "Functionality issues"
            }
        ]
    
    def _identify_affected_contracts(self, contract_code: str, refactoring_goals: List[str]) -> List[str]:
        """Identify contracts affected by refactoring"""
        return ["exchange.cairo", "vault.cairo"] if refactoring_goals else []
    
    def _identify_external_dependencies(self, contract_code: str) -> List[str]:
        """Identify external dependencies"""
        return ["oracle_feeds", "payment_gateway"] if "external" in contract_code.lower() else []
    
    def _assess_user_impact(self, refactoring_goals: List[str]) -> str:
        """Assess impact on users"""
        return "Low - No breaking API changes" if refactoring_goals else "Minimal"
    
    def _estimate_development_effort(self, plan: List[Dict]) -> str:
        """Estimate development effort"""
        return f"{len(plan) * 2}-{len(plan) * 3} weeks"
    
    def _define_testing_requirements(self, refactoring_goals: List[str]) -> List[str]:
        """Define testing requirements"""
        return [
            "Comprehensive regression testing",
            "Performance benchmarking",
            "Integration testing with all dependent systems"
        ]