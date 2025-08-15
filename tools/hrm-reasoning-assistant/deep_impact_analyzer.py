#!/usr/bin/env python3
"""
Deep Impact HRM Analyzer

Extended contextual reasoning that explains:
1. WHY something is concerning (root cause analysis)
2. WHAT the specific impacts are (business, technical, team)
3. HOW urgent the issue is (risk assessment)
4. WHEN to address it (prioritization)
5. WHAT alternatives exist (solution space)

This represents advanced HRM reasoning that goes beyond detection to impact analysis.
"""

import ast
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta

class ImpactSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ImpactCategory(Enum):
    MAINTAINABILITY = "maintainability"
    PERFORMANCE = "performance"
    TESTING = "testing"
    COLLABORATION = "collaboration"
    TECHNICAL_DEBT = "technical_debt"
    BUSINESS_RISK = "business_risk"

@dataclass
class ImpactAnalysis:
    category: ImpactCategory
    severity: ImpactSeverity
    description: str
    evidence: List[str]
    time_to_impact: str  # "immediate", "weeks", "months"
    cost_estimate: str
    mitigation_strategies: List[str]

@dataclass
class DeepAnalysisResult:
    class_name: str
    line_count: int
    concern_level: str
    confidence: float
    root_causes: List[str]
    impact_analyses: List[ImpactAnalysis]
    risk_assessment: Dict[str, Any]
    prioritization_score: int
    recommended_actions: List[Dict[str, Any]]
    alternatives: List[Dict[str, str]]

class DeepImpactAnalyzer:
    """Extended HRM analyzer with deep impact reasoning"""
    
    def __init__(self):
        self.entity_size_thresholds = {
            'small': 50,
            'medium': 150,
            'large': 300,
            'excessive': 500
        }
        
        self.domain_context = {
            'nft': {
                'expected_complexity': 'high',
                'business_criticality': 'high',
                'change_frequency': 'medium',
                'team_familiarity': 'medium'
            },
            'trading': {
                'expected_complexity': 'very_high',
                'business_criticality': 'critical',
                'change_frequency': 'high',
                'team_familiarity': 'high'
            },
            'gamification': {
                'expected_complexity': 'medium',
                'business_criticality': 'medium',
                'change_frequency': 'high',
                'team_familiarity': 'high'
            }
        }
    
    def analyze_deep_impact(self, file_path: str, class_name: str, line_count: int) -> DeepAnalysisResult:
        """
        Perform deep impact analysis with extended contextual reasoning
        """
        
        print(f"🔬 **Deep HRM Impact Analysis: {class_name} ({line_count} lines)**")
        print("=" * 80)
        
        # Read and parse the file
        with open(file_path, 'r') as f:
            code = f.read()
        
        tree = ast.parse(code)
        class_node = self._find_class_node(tree, class_name)
        
        if not class_node:
            return self._create_error_result(class_name, line_count, "Class not found")
        
        # Multi-dimensional analysis
        entity_analysis = self._analyze_entity_specific_concerns(class_node, code, file_path)
        business_context = self._analyze_business_context(file_path, class_node, code)
        technical_debt_analysis = self._analyze_technical_debt_implications(class_node, code, line_count)
        collaboration_impact = self._analyze_collaboration_impact(class_node, code, line_count)
        testing_implications = self._analyze_testing_implications(class_node, code)
        performance_concerns = self._analyze_performance_implications(class_node, code)
        evolution_risks = self._analyze_evolution_risks(class_node, code, line_count)
        
        # Synthesize root causes
        root_causes = self._identify_root_causes(
            entity_analysis, business_context, technical_debt_analysis, 
            collaboration_impact, testing_implications
        )
        
        # Generate impact analyses
        impact_analyses = self._generate_impact_analyses(
            entity_analysis, business_context, technical_debt_analysis,
            collaboration_impact, testing_implications, performance_concerns,
            evolution_risks, line_count
        )
        
        # Risk assessment
        risk_assessment = self._perform_risk_assessment(
            impact_analyses, business_context, line_count
        )
        
        # Prioritization scoring
        prioritization_score = self._calculate_prioritization_score(
            impact_analyses, risk_assessment, business_context
        )
        
        # Generate recommended actions
        recommended_actions = self._generate_recommended_actions(
            impact_analyses, risk_assessment, prioritization_score
        )
        
        # Identify alternatives
        alternatives = self._identify_refactoring_alternatives(
            class_node, code, entity_analysis, line_count
        )
        
        result = DeepAnalysisResult(
            class_name=class_name,
            line_count=line_count,
            concern_level=self._determine_concern_level(prioritization_score),
            confidence=0.85,  # High confidence in impact analysis
            root_causes=root_causes,
            impact_analyses=impact_analyses,
            risk_assessment=risk_assessment,
            prioritization_score=prioritization_score,
            recommended_actions=recommended_actions,
            alternatives=alternatives
        )
        
        self._print_deep_analysis(result)
        return result
    
    def _analyze_entity_specific_concerns(self, class_node: ast.ClassDef, code: str, file_path: str) -> Dict[str, Any]:
        """Analyze concerns specific to entity classes"""
        
        concerns = []
        evidence = []
        
        # Entity should have focused responsibility
        method_count = len([n for n in class_node.body if isinstance(n, ast.FunctionDef)])
        if method_count > 20:
            concerns.append("Entity has too many methods - violates Single Responsibility Principle")
            evidence.append(f"Found {method_count} methods in entity class")
        
        # Entity should not have complex business logic
        complex_methods = self._find_complex_business_logic(class_node)
        if complex_methods:
            concerns.append("Entity contains complex business logic that should be in domain services")
            evidence.extend([f"Complex method: {method}" for method in complex_methods])
        
        # Entity should not manage external dependencies
        external_deps = self._find_external_dependencies(class_node, code)
        if external_deps:
            concerns.append("Entity has external dependencies - should be dependency-free")
            evidence.extend([f"External dependency: {dep}" for dep in external_deps])
        
        # NFT-specific concerns
        if 'nft' in file_path.lower():
            nft_concerns = self._analyze_nft_specific_concerns(class_node, code)
            concerns.extend(nft_concerns['concerns'])
            evidence.extend(nft_concerns['evidence'])
        
        return {
            'concerns': concerns,
            'evidence': evidence,
            'method_count': method_count,
            'complexity_score': self._calculate_entity_complexity(class_node)
        }
    
    def _analyze_business_context(self, file_path: str, class_node: ast.ClassDef, code: str) -> Dict[str, Any]:
        """Analyze business context and criticality"""
        
        domain = self._extract_domain_from_path(file_path)
        domain_info = self.domain_context.get(domain, {})
        
        # Business criticality factors
        business_factors = {
            'domain': domain,
            'criticality': domain_info.get('business_criticality', 'medium'),
            'change_frequency': domain_info.get('change_frequency', 'medium'),
            'team_familiarity': domain_info.get('team_familiarity', 'medium')
        }
        
        # NFT-specific business concerns
        if domain == 'nft':
            business_factors.update({
                'revenue_impact': 'high',  # NFTs are monetization feature
                'user_facing': True,       # Directly visible to users
                'blockchain_integration': True,  # Complex integration requirements
                'compliance_requirements': True  # Legal/regulatory concerns
            })
        
        # Extract business concepts from code
        business_concepts = self._extract_business_concepts(code)
        
        return {
            'domain_info': business_factors,
            'business_concepts': business_concepts,
            'estimated_change_frequency': self._estimate_change_frequency(class_node, code),
            'user_impact_level': self._assess_user_impact_level(class_node, code)
        }
    
    def _analyze_technical_debt_implications(self, class_node: ast.ClassDef, code: str, line_count: int) -> Dict[str, Any]:
        """Analyze technical debt implications of large entity"""
        
        debt_indicators = []
        debt_severity = "low"
        
        # Size-based debt
        if line_count > 300:
            debt_indicators.append("Excessive size indicates accumulated technical debt")
            debt_severity = "medium"
        
        if line_count > 500:
            debt_indicators.append("Critical size - major refactoring debt")
            debt_severity = "high"
        
        # Code quality debt
        duplication = self._detect_code_duplication(class_node, code)
        if duplication['score'] > 0.3:
            debt_indicators.append("High code duplication within class")
            debt_severity = "high"
        
        # Design debt
        design_violations = self._detect_design_violations(class_node, code)
        debt_indicators.extend(design_violations)
        
        # Maintenance cost estimation
        maintenance_cost = self._estimate_maintenance_cost(line_count, debt_indicators)
        
        return {
            'debt_indicators': debt_indicators,
            'debt_severity': debt_severity,
            'duplication_score': duplication['score'],
            'design_violations': design_violations,
            'estimated_maintenance_cost': maintenance_cost,
            'refactoring_effort_days': self._estimate_refactoring_effort(line_count, debt_indicators)
        }
    
    def _analyze_collaboration_impact(self, class_node: ast.ClassDef, code: str, line_count: int) -> Dict[str, Any]:
        """Analyze impact on team collaboration"""
        
        collaboration_issues = []
        
        # Large classes cause merge conflicts
        if line_count > 250:
            collaboration_issues.append("Large file increases likelihood of merge conflicts")
        
        # Complex classes are hard to understand for new team members
        complexity_score = self._calculate_cognitive_complexity(class_node)
        if complexity_score > 50:
            collaboration_issues.append("High cognitive complexity impedes knowledge transfer")
        
        # Multiple responsibilities lead to ownership confusion
        responsibilities = self._identify_responsibilities(class_node, code)
        if len(responsibilities) > 3:
            collaboration_issues.append("Multiple responsibilities create unclear ownership")
        
        # Hard to review
        if line_count > 300:
            collaboration_issues.append("Difficult to review in code reviews - reduces quality")
        
        return {
            'collaboration_issues': collaboration_issues,
            'cognitive_complexity': complexity_score,
            'responsibilities': responsibilities,
            'review_difficulty': "high" if line_count > 300 else "medium",
            'onboarding_impact': "significant" if complexity_score > 50 else "moderate"
        }
    
    def _analyze_testing_implications(self, class_node: ast.ClassDef, code: str) -> Dict[str, Any]:
        """Analyze testing implications"""
        
        testing_challenges = []
        
        # Large classes are hard to test comprehensively
        method_count = len([n for n in class_node.body if isinstance(n, ast.FunctionDef)])
        if method_count > 15:
            testing_challenges.append("Many methods require extensive test coverage")
        
        # Complex state makes test setup difficult
        state_complexity = self._analyze_state_complexity(class_node)
        if state_complexity['score'] > 0.7:
            testing_challenges.append("Complex state makes test setup and teardown difficult")
        
        # External dependencies complicate testing
        external_deps = self._find_external_dependencies(class_node, code)
        if external_deps:
            testing_challenges.append("External dependencies require extensive mocking")
        
        # Estimate test maintenance burden
        test_maintenance_burden = self._estimate_test_maintenance_burden(
            method_count, state_complexity['score'], len(external_deps)
        )
        
        return {
            'testing_challenges': testing_challenges,
            'state_complexity': state_complexity,
            'test_maintenance_burden': test_maintenance_burden,
            'estimated_test_lines': method_count * 15,  # Rough estimate
            'mock_complexity': len(external_deps)
        }
    
    def _analyze_performance_implications(self, class_node: ast.ClassDef, code: str) -> Dict[str, Any]:
        """Analyze potential performance implications"""
        
        performance_concerns = []
        
        # Large objects consume more memory
        if len([n for n in class_node.body if isinstance(n, ast.AnnAssign)]) > 20:
            performance_concerns.append("Many attributes increase memory footprint")
        
        # Complex initialization
        init_method = self._find_init_method(class_node)
        if init_method and self._calculate_method_complexity(init_method) > 10:
            performance_concerns.append("Complex initialization may impact object creation performance")
        
        # Look for potential N+1 patterns or expensive operations
        expensive_operations = self._find_potentially_expensive_operations(class_node, code)
        if expensive_operations:
            performance_concerns.extend(expensive_operations)
        
        return {
            'performance_concerns': performance_concerns,
            'memory_impact': "medium" if len(performance_concerns) > 2 else "low",
            'creation_cost': "high" if any("initialization" in concern for concern in performance_concerns) else "low"
        }
    
    def _analyze_evolution_risks(self, class_node: ast.ClassDef, code: str, line_count: int) -> Dict[str, Any]:
        """Analyze risks related to future evolution"""
        
        evolution_risks = []
        
        # Large classes resist change
        if line_count > 300:
            evolution_risks.append("Large size makes future changes risky and expensive")
        
        # Tight coupling prevents evolution
        coupling_score = self._calculate_coupling_score(class_node, code)
        if coupling_score > 0.7:
            evolution_risks.append("High coupling makes independent evolution difficult")
        
        # Business domain evolution
        if 'nft' in code.lower():
            evolution_risks.append("NFT domain is rapidly evolving - needs flexible design")
        
        # Technology evolution
        blockchain_deps = self._find_blockchain_dependencies(code)
        if blockchain_deps:
            evolution_risks.append("Blockchain technology evolution may require significant changes")
        
        return {
            'evolution_risks': evolution_risks,
            'coupling_score': coupling_score,
            'change_resistance': "high" if line_count > 300 else "medium",
            'adaptation_cost': self._estimate_adaptation_cost(line_count, coupling_score)
        }
    
    def _generate_impact_analyses(self, entity_analysis, business_context, technical_debt, 
                                collaboration, testing, performance, evolution, line_count) -> List[ImpactAnalysis]:
        """Generate detailed impact analyses for each concern area"""
        
        impacts = []
        
        # Maintainability Impact
        maintainability_evidence = []
        maintainability_evidence.extend(technical_debt['debt_indicators'])
        maintainability_evidence.extend([f"Complex state with {collaboration['cognitive_complexity']} complexity score"])
        
        maintainability_severity = ImpactSeverity.HIGH if line_count > 400 else ImpactSeverity.MEDIUM
        
        impacts.append(ImpactAnalysis(
            category=ImpactCategory.MAINTAINABILITY,
            severity=maintainability_severity,
            description=f"Large entity class ({line_count} lines) significantly increases maintenance burden and modification risk",
            evidence=maintainability_evidence,
            time_to_impact="immediate",
            cost_estimate=f"${technical_debt['estimated_maintenance_cost']/1000:.0f}K annual maintenance overhead",
            mitigation_strategies=[
                "Break into smaller, focused classes",
                "Extract business logic to domain services",
                "Implement facade pattern for complex operations",
                "Add comprehensive documentation"
            ]
        ))
        
        # Collaboration Impact
        if collaboration['collaboration_issues']:
            impacts.append(ImpactAnalysis(
                category=ImpactCategory.COLLABORATION,
                severity=ImpactSeverity.MEDIUM,
                description="Large class impedes team collaboration and knowledge sharing",
                evidence=collaboration['collaboration_issues'],
                time_to_impact="weeks",
                cost_estimate="20-30% increased development time for features touching this class",
                mitigation_strategies=[
                    "Establish clear ownership boundaries",
                    "Create detailed documentation",
                    "Implement pair programming for changes",
                    "Regular architecture reviews"
                ]
            ))
        
        # Testing Impact
        if testing['testing_challenges']:
            impacts.append(ImpactAnalysis(
                category=ImpactCategory.TESTING,
                severity=ImpactSeverity.MEDIUM,
                description="Testing complexity reduces code quality and deployment confidence",
                evidence=testing['testing_challenges'],
                time_to_impact="immediate",
                cost_estimate=f"{testing['estimated_test_lines']} additional test lines required",
                mitigation_strategies=[
                    "Extract testable components",
                    "Implement builder pattern for test setup",
                    "Add integration test coverage",
                    "Mock external dependencies"
                ]
            ))
        
        # Technical Debt Impact
        if technical_debt['debt_severity'] in ['medium', 'high']:
            impacts.append(ImpactAnalysis(
                category=ImpactCategory.TECHNICAL_DEBT,
                severity=ImpactSeverity.HIGH if technical_debt['debt_severity'] == 'high' else ImpactSeverity.MEDIUM,
                description="Accumulating technical debt will compound maintenance costs over time",
                evidence=technical_debt['debt_indicators'],
                time_to_impact="months",
                cost_estimate=f"{technical_debt['refactoring_effort_days']} person-days to address",
                mitigation_strategies=[
                    "Schedule dedicated refactoring sprint",
                    "Implement incremental refactoring",
                    "Add architectural constraints",
                    "Regular debt assessment"
                ]
            ))
        
        # Business Risk Impact (for NFT domain)
        if business_context['domain_info'].get('criticality') == 'high':
            impacts.append(ImpactAnalysis(
                category=ImpactCategory.BUSINESS_RISK,
                severity=ImpactSeverity.HIGH,
                description="Complex NFT entity increases risk of bugs in revenue-critical functionality",
                evidence=[
                    "NFT domain directly impacts revenue",
                    "User-facing functionality with high visibility",
                    "Complex blockchain integration requirements"
                ],
                time_to_impact="immediate",
                cost_estimate="High - potential revenue loss from NFT marketplace issues",
                mitigation_strategies=[
                    "Prioritize comprehensive testing",
                    "Implement staging environment validation",
                    "Add monitoring and alerting",
                    "Create rollback procedures"
                ]
            ))
        
        return impacts
    
    def _perform_risk_assessment(self, impact_analyses: List[ImpactAnalysis], 
                               business_context: Dict, line_count: int) -> Dict[str, Any]:
        """Perform comprehensive risk assessment"""
        
        # Calculate risk scores
        high_severity_impacts = len([i for i in impact_analyses if i.severity == ImpactSeverity.HIGH])
        medium_severity_impacts = len([i for i in impact_analyses if i.severity == ImpactSeverity.MEDIUM])
        
        # Risk factors
        size_risk = min(line_count / 500.0, 1.0)  # Normalize to 0-1
        business_criticality = 1.0 if business_context['domain_info'].get('criticality') == 'high' else 0.5
        change_frequency = 1.0 if business_context['domain_info'].get('change_frequency') == 'high' else 0.7
        
        # Overall risk score (0-100)
        risk_score = int((
            (high_severity_impacts * 30) +
            (medium_severity_impacts * 15) +
            (size_risk * 20) +
            (business_criticality * 15) +
            (change_frequency * 10)
        ))
        
        risk_level = "CRITICAL" if risk_score > 80 else "HIGH" if risk_score > 60 else "MEDIUM" if risk_score > 40 else "LOW"
        
        return {
            'risk_score': risk_score,
            'risk_level': risk_level,
            'high_severity_impacts': high_severity_impacts,
            'medium_severity_impacts': medium_severity_impacts,
            'primary_risk_factors': [
                "Large size increases change risk",
                "High business criticality amplifies impact",
                "Frequent changes increase failure probability"
            ][:high_severity_impacts + 1]
        }
    
    def _calculate_prioritization_score(self, impact_analyses: List[ImpactAnalysis], 
                                      risk_assessment: Dict, business_context: Dict) -> int:
        """Calculate prioritization score (0-100)"""
        
        # Base score from risk assessment
        base_score = risk_assessment['risk_score']
        
        # Adjust for immediate impacts
        immediate_impacts = len([i for i in impact_analyses if i.time_to_impact == "immediate"])
        urgency_bonus = immediate_impacts * 10
        
        # Adjust for business criticality
        business_bonus = 15 if business_context['domain_info'].get('criticality') == 'high' else 0
        
        # Calculate final score
        priority_score = min(base_score + urgency_bonus + business_bonus, 100)
        
        return priority_score
    
    def _generate_recommended_actions(self, impact_analyses: List[ImpactAnalysis], 
                                    risk_assessment: Dict, prioritization_score: int) -> List[Dict[str, Any]]:
        """Generate prioritized recommended actions"""
        
        actions = []
        
        if prioritization_score > 80:
            actions.append({
                'priority': 'URGENT',
                'timeframe': '1-2 sprints',
                'action': 'Immediate refactoring required - schedule dedicated refactoring sprint',
                'rationale': 'High risk score and immediate impacts require urgent attention',
                'success_criteria': 'Reduce class size by 50%, extract domain services'
            })
        elif prioritization_score > 60:
            actions.append({
                'priority': 'HIGH',
                'timeframe': '2-4 sprints',
                'action': 'Plan structured refactoring as part of regular development',
                'rationale': 'Significant impacts warrant prioritized attention',
                'success_criteria': 'Break into 2-3 focused classes, improve test coverage'
            })
        else:
            actions.append({
                'priority': 'MEDIUM',
                'timeframe': '1-2 quarters',
                'action': 'Include in technical debt backlog for future attention',
                'rationale': 'Manageable concerns that can be addressed incrementally',
                'success_criteria': 'Incremental improvements during feature development'
            })
        
        # Add specific technical actions
        for impact in impact_analyses:
            if impact.severity in [ImpactSeverity.HIGH, ImpactSeverity.CRITICAL]:
                actions.append({
                    'priority': 'HIGH',
                    'timeframe': 'Next sprint',
                    'action': f"Address {impact.category.value} concerns",
                    'rationale': impact.description,
                    'success_criteria': f"Implement: {'; '.join(impact.mitigation_strategies[:2])}"
                })
        
        return actions
    
    def _identify_refactoring_alternatives(self, class_node: ast.ClassDef, code: str, 
                                         entity_analysis: Dict, line_count: int) -> List[Dict[str, str]]:
        """Identify specific refactoring alternatives"""
        
        alternatives = []
        
        # Extract Value Objects
        if self._can_extract_value_objects(class_node, code):
            alternatives.append({
                'strategy': 'Extract Value Objects',
                'description': 'Extract complex attributes into separate value object classes',
                'effort': 'Medium (1-2 weeks)',
                'impact': 'Reduces complexity, improves reusability',
                'example': 'Extract NFTMetadata, NFTRoyalty, NFTAttributes as separate classes'
            })
        
        # Extract Domain Services
        if entity_analysis['method_count'] > 15:
            alternatives.append({
                'strategy': 'Extract Domain Services',
                'description': 'Move business logic methods to dedicated domain service classes',
                'effort': 'High (2-3 weeks)',
                'impact': 'Separates concerns, improves testability',
                'example': 'Create NFTMintingService, NFTTransferService, NFTValidationService'
            })
        
        # Composition over Inheritance
        alternatives.append({
            'strategy': 'Composition Pattern',
            'description': 'Break into smaller components using composition',
            'effort': 'High (3-4 weeks)',
            'impact': 'Maximum flexibility, best long-term solution',
            'example': 'NFT contains NFTCore, NFTMetadata, NFTBehavior components'
        })
        
        # Facade Pattern
        if line_count > 400:
            alternatives.append({
                'strategy': 'Facade Pattern',
                'description': 'Create a simplified interface over complex subsystems',
                'effort': 'Low (3-5 days)',
                'impact': 'Immediate usability improvement, hides complexity',
                'example': 'NFTFacade provides simple interface to complex NFT operations'
            })
        
        # State Pattern
        if self._has_state_machine_behavior(class_node, code):
            alternatives.append({
                'strategy': 'State Pattern',
                'description': 'Extract state-specific behavior into separate state classes',
                'effort': 'Medium (1-2 weeks)',
                'impact': 'Cleaner state management, easier to extend',
                'example': 'NFTDraftState, NFTMintedState, NFTTransferredState classes'
            })
        
        return alternatives
    
    # Helper methods (many omitted for brevity - would include full implementations)
    
    def _find_class_node(self, tree: ast.AST, class_name: str) -> Optional[ast.ClassDef]:
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == class_name:
                return node
        return None
    
    def _extract_domain_from_path(self, file_path: str) -> str:
        parts = Path(file_path).parts
        if 'domains' in parts:
            domain_index = parts.index('domains')
            if domain_index + 1 < len(parts):
                return parts[domain_index + 1]
        return 'unknown'
    
    def _calculate_entity_complexity(self, class_node: ast.ClassDef) -> int:
        # Simplified complexity calculation
        complexity = 0
        for node in ast.walk(class_node):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
        return complexity
    
    def _find_complex_business_logic(self, class_node: ast.ClassDef) -> List[str]:
        # Find methods with high complexity
        complex_methods = []
        for node in class_node.body:
            if isinstance(node, ast.FunctionDef):
                complexity = self._calculate_method_complexity(node)
                if complexity > 8:
                    complex_methods.append(f"{node.name} (complexity: {complexity})")
        return complex_methods
    
    def _calculate_method_complexity(self, method_node: ast.FunctionDef) -> int:
        complexity = 1
        for node in ast.walk(method_node):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
        return complexity
    
    def _find_external_dependencies(self, class_node: ast.ClassDef, code: str) -> List[str]:
        # Simplified - look for common external dependency patterns
        deps = []
        if 'requests.' in code:
            deps.append('HTTP client dependency')
        if 'redis' in code.lower():
            deps.append('Redis dependency')
        if 'database' in code.lower() or 'db.' in code:
            deps.append('Database dependency')
        return deps
    
    def _analyze_nft_specific_concerns(self, class_node: ast.ClassDef, code: str) -> Dict[str, Any]:
        concerns = []
        evidence = []
        
        # NFT entities should be immutable
        if not self._is_immutable_design(class_node, code):
            concerns.append("NFT entity should be immutable to prevent accidental modification")
            evidence.append("No @dataclass(frozen=True) or immutability patterns found")
        
        # Should have proper validation
        if not self._has_nft_validation(code):
            concerns.append("Missing NFT-specific validation (metadata, royalties, etc.)")
            evidence.append("No validation methods for NFT business rules found")
        
        return {'concerns': concerns, 'evidence': evidence}
    
    def _is_immutable_design(self, class_node: ast.ClassDef, code: str) -> bool:
        return 'frozen=True' in code or 'Final' in code
    
    def _has_nft_validation(self, code: str) -> bool:
        return any(word in code.lower() for word in ['validate', 'check', 'verify']) and 'nft' in code.lower()
    
    # Additional helper methods would be implemented here...
    
    def _determine_concern_level(self, prioritization_score: int) -> str:
        if prioritization_score > 80:
            return "CRITICAL"
        elif prioritization_score > 60:
            return "HIGH"
        elif prioritization_score > 40:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _create_error_result(self, class_name: str, line_count: int, error: str) -> DeepAnalysisResult:
        return DeepAnalysisResult(
            class_name=class_name,
            line_count=line_count,
            concern_level="UNKNOWN",
            confidence=0.0,
            root_causes=[error],
            impact_analyses=[],
            risk_assessment={},
            prioritization_score=0,
            recommended_actions=[],
            alternatives=[]
        )
    
    def _print_deep_analysis(self, result: DeepAnalysisResult) -> None:
        """Print comprehensive deep analysis results"""
        
        print(f"\n🎯 **DEEP IMPACT ASSESSMENT**")
        print(f"   **Class**: {result.class_name} ({result.line_count} lines)")
        print(f"   **Concern Level**: {result.concern_level}")
        print(f"   **Confidence**: {result.confidence:.1%}")
        print(f"   **Priority Score**: {result.prioritization_score}/100")
        
        print(f"\n🔍 **ROOT CAUSES**:")
        for i, cause in enumerate(result.root_causes, 1):
            print(f"   {i}. {cause}")
        
        print(f"\n⚠️  **IMPACT ANALYSIS** ({len(result.impact_analyses)} areas affected):")
        for impact in result.impact_analyses:
            print(f"\n   📊 **{impact.category.value.upper()}** - {impact.severity.value.upper()} severity")
            print(f"      {impact.description}")
            print(f"      **Time to Impact**: {impact.time_to_impact}")
            print(f"      **Cost**: {impact.cost_estimate}")
            if impact.evidence:
                print(f"      **Evidence**: {'; '.join(impact.evidence[:2])}")
            print(f"      **Top Mitigations**: {'; '.join(impact.mitigation_strategies[:2])}")
        
        print(f"\n🎯 **RISK ASSESSMENT**:")
        risk = result.risk_assessment
        if risk:
            print(f"   **Overall Risk**: {risk.get('risk_level', 'UNKNOWN')} ({risk.get('risk_score', 0)}/100)")
            print(f"   **High Severity Impacts**: {risk.get('high_severity_impacts', 0)}")
            print(f"   **Medium Severity Impacts**: {risk.get('medium_severity_impacts', 0)}")
        
        print(f"\n🚀 **RECOMMENDED ACTIONS** ({len(result.recommended_actions)} actions):")
        for i, action in enumerate(result.recommended_actions[:3], 1):  # Top 3
            print(f"   {i}. **{action.get('priority', 'MEDIUM')}** ({action.get('timeframe', 'TBD')})")
            print(f"      {action.get('action', 'No action specified')}")
            print(f"      *Rationale*: {action.get('rationale', 'No rationale provided')}")
        
        print(f"\n🔧 **REFACTORING ALTERNATIVES** ({len(result.alternatives)} options):")
        for i, alt in enumerate(result.alternatives[:3], 1):  # Top 3
            print(f"   {i}. **{alt.get('strategy', 'Unknown Strategy')}** - {alt.get('effort', 'Unknown effort')}")
            print(f"      {alt.get('description', 'No description')}")
            print(f"      *Impact*: {alt.get('impact', 'Unknown impact')}")

# Simplified implementations for demonstration
    def _extract_business_concepts(self, code: str) -> List[str]:
        concepts = []
        if 'mint' in code.lower():
            concepts.append('NFT Minting')
        if 'transfer' in code.lower():
            concepts.append('NFT Transfer')
        if 'royalty' in code.lower():
            concepts.append('Royalty Management')
        return concepts
        
    def _estimate_change_frequency(self, class_node: ast.ClassDef, code: str) -> str:
        # Simplified heuristic
        if 'nft' in code.lower():
            return 'high'  # NFT domain is evolving rapidly
        return 'medium'
    
    def _assess_user_impact_level(self, class_node: ast.ClassDef, code: str) -> str:
        if any(term in code.lower() for term in ['user', 'client', 'api', 'frontend']):
            return 'high'
        return 'medium'
    
    def _detect_code_duplication(self, class_node: ast.ClassDef, code: str) -> Dict[str, float]:
        # Simplified duplication detection
        lines = code.split('\n')
        unique_lines = set(line.strip() for line in lines if line.strip())
        duplication_score = max(0, 1 - (len(unique_lines) / len(lines))) if lines else 0
        return {'score': duplication_score}
    
    def _detect_design_violations(self, class_node: ast.ClassDef, code: str) -> List[str]:
        violations = []
        if len([n for n in class_node.body if isinstance(n, ast.FunctionDef)]) > 20:
            violations.append("Single Responsibility Principle violation")
        return violations
    
    def _estimate_maintenance_cost(self, line_count: int, debt_indicators: List[str]) -> int:
        # Rough cost estimate in dollars per year
        base_cost = line_count * 50  # $50 per line per year
        debt_multiplier = 1 + (len(debt_indicators) * 0.2)
        return int(base_cost * debt_multiplier)
    
    def _estimate_refactoring_effort(self, line_count: int, debt_indicators: List[str]) -> int:
        # Estimate person-days
        base_days = line_count / 50  # 50 lines per day refactoring
        complexity_factor = 1 + (len(debt_indicators) * 0.3)
        return int(base_days * complexity_factor)
    
    def _calculate_cognitive_complexity(self, class_node: ast.ClassDef) -> int:
        # Simplified cognitive complexity
        complexity = 0
        for node in ast.walk(class_node):
            if isinstance(node, ast.If):
                complexity += 1
            elif isinstance(node, ast.For):
                complexity += 2
            elif isinstance(node, ast.While):
                complexity += 2
        return complexity
    
    def _identify_responsibilities(self, class_node: ast.ClassDef, code: str) -> List[str]:
        responsibilities = []
        if 'create' in code.lower() or 'build' in code.lower():
            responsibilities.append('Creation')
        if 'validate' in code.lower():
            responsibilities.append('Validation')
        if 'transfer' in code.lower():
            responsibilities.append('Transfer Management')
        if 'metadata' in code.lower():
            responsibilities.append('Metadata Management')
        return responsibilities
    
    def _analyze_state_complexity(self, class_node: ast.ClassDef) -> Dict[str, float]:
        # Count instance variables
        state_vars = len([n for n in class_node.body if isinstance(n, ast.AnnAssign)])
        score = min(state_vars / 10.0, 1.0)  # Normalize to 0-1
        return {'score': score, 'variable_count': state_vars}
    
    def _estimate_test_maintenance_burden(self, method_count: int, state_complexity: float, external_deps: int) -> str:
        burden_score = method_count + (state_complexity * 10) + (external_deps * 5)
        if burden_score > 50:
            return "High"
        elif burden_score > 25:
            return "Medium"
        else:
            return "Low"
    
    def _find_init_method(self, class_node: ast.ClassDef) -> Optional[ast.FunctionDef]:
        for node in class_node.body:
            if isinstance(node, ast.FunctionDef) and node.name == '__init__':
                return node
        return None
    
    def _find_potentially_expensive_operations(self, class_node: ast.ClassDef, code: str) -> List[str]:
        expensive_ops = []
        if 'loop' in code.lower() or 'for ' in code:
            expensive_ops.append("Potential O(n) operations detected")
        if 'blockchain' in code.lower() or 'contract' in code.lower():
            expensive_ops.append("Blockchain operations can be slow and expensive")
        return expensive_ops
    
    def _calculate_coupling_score(self, class_node: ast.ClassDef, code: str) -> float:
        # Count imports and external references
        import_count = code.count('import ') + code.count('from ')
        external_calls = code.count('.') - code.count('self.')
        coupling_score = min((import_count + external_calls) / 50.0, 1.0)
        return coupling_score
    
    def _find_blockchain_dependencies(self, code: str) -> List[str]:
        deps = []
        if 'starknet' in code.lower():
            deps.append('Starknet dependency')
        if 'cairo' in code.lower():
            deps.append('Cairo contract dependency')
        return deps
    
    def _estimate_adaptation_cost(self, line_count: int, coupling_score: float) -> str:
        cost_factor = (line_count / 500.0) + coupling_score
        if cost_factor > 1.5:
            return "Very High"
        elif cost_factor > 1.0:
            return "High"
        elif cost_factor > 0.5:
            return "Medium"
        else:
            return "Low"
    
    def _identify_root_causes(self, entity_analysis, business_context, technical_debt, collaboration, testing) -> List[str]:
        causes = []
        
        if entity_analysis['method_count'] > 20:
            causes.append("Entity class has accumulated too many responsibilities over time")
        
        if technical_debt['debt_severity'] in ['medium', 'high']:
            causes.append("Lack of regular refactoring has allowed technical debt to accumulate")
        
        if len(collaboration['responsibilities']) > 3:
            causes.append("Multiple business concerns mixed within single class")
        
        if business_context['domain_info'].get('change_frequency') == 'high':
            causes.append("High change frequency in evolving domain without architectural boundaries")
        
        return causes
    
    def _can_extract_value_objects(self, class_node: ast.ClassDef, code: str) -> bool:
        # Check if there are complex attributes that could be value objects
        return 'metadata' in code.lower() or 'attributes' in code.lower() or 'properties' in code.lower()
    
    def _has_state_machine_behavior(self, class_node: ast.ClassDef, code: str) -> bool:
        # Look for state-like behavior
        return any(word in code.lower() for word in ['state', 'status', 'phase', 'stage'])

def main():
    import sys
    
    if len(sys.argv) != 4:
        print("Usage: python deep_impact_analyzer.py <file_path> <class_name> <line_count>")
        print("Example: python deep_impact_analyzer.py entities.py GenesisNFT 330")
        sys.exit(1)
    
    file_path = sys.argv[1]
    class_name = sys.argv[2]
    line_count = int(sys.argv[3])
    
    analyzer = DeepImpactAnalyzer()
    result = analyzer.analyze_deep_impact(file_path, class_name, line_count)
    
    print(f"\n🎉 **DEEP IMPACT ANALYSIS COMPLETE**")
    print(f"   **Priority Score**: {result.prioritization_score}/100")
    print(f"   **Recommended Timeline**: {result.recommended_actions[0]['timeframe'] if result.recommended_actions else 'TBD'}")

if __name__ == "__main__":
    main()