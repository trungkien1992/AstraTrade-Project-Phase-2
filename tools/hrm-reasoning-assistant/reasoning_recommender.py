#!/usr/bin/env python3
"""
HRM Reasoning Recommender

Advanced HRM tool that doesn't just suggest recommendations, but REASONS through:
1. WHY each recommendation makes sense for this specific context
2. WHICH recommendation is best given the constraints
3. HOW to sequence multiple recommendations
4. WHAT the trade-offs are between different approaches
5. WHEN to apply each recommendation based on business priorities

This represents the pinnacle of HRM reasoning - contextual recommendation synthesis.
"""

import ast
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta

class RecommendationReasoning(Enum):
    BUSINESS_PRIORITY = "business_priority"
    TECHNICAL_FEASIBILITY = "technical_feasibility"
    RISK_MITIGATION = "risk_mitigation"
    COST_OPTIMIZATION = "cost_optimization"
    TEAM_CAPACITY = "team_capacity"
    ARCHITECTURAL_ALIGNMENT = "architectural_alignment"

@dataclass
class ReasonedRecommendation:
    recommendation: str
    reasoning_type: RecommendationReasoning
    confidence: float
    effort_estimate: str
    business_value: str
    risk_level: str
    prerequisites: List[str]
    success_metrics: List[str]
    reasoning_steps: List[str]
    trade_offs: Dict[str, str]
    implementation_guidance: str
    why_this_context: str  # Why this recommendation for THIS specific situation

@dataclass
class RecommendationPlan:
    primary_recommendation: ReasonedRecommendation
    alternative_recommendations: List[ReasonedRecommendation]
    sequencing_strategy: str
    total_timeline: str
    resource_requirements: Dict[str, Any]
    success_probability: float
    contextual_reasoning: List[str]

class ReasoningRecommender:
    """HRM tool that reasons through recommendations contextually"""
    
    def __init__(self):
        self.context_factors = {
            'business_criticality': ['low', 'medium', 'high', 'critical'],
            'team_size': ['small', 'medium', 'large'],
            'domain_maturity': ['new', 'evolving', 'stable', 'legacy'],
            'change_frequency': ['low', 'medium', 'high', 'very_high'],
            'technical_debt_level': ['low', 'medium', 'high', 'critical'],
            'available_time': ['limited', 'moderate', 'flexible'],
            'risk_tolerance': ['low', 'medium', 'high']
        }
        
        self.recommendation_templates = {
            'extract_value_objects': {
                'base_effort': '1-2 weeks',
                'complexity_factors': ['attribute_count', 'validation_complexity', 'usage_spread'],
                'best_when': ['high_attribute_complexity', 'reusable_concepts', 'clear_boundaries'],
                'avoid_when': ['tight_coupling', 'frequent_changes', 'simple_attributes']
            },
            'extract_domain_services': {
                'base_effort': '2-3 weeks', 
                'complexity_factors': ['method_count', 'business_logic_complexity', 'dependency_web'],
                'best_when': ['clear_business_operations', 'testability_needed', 'single_responsibility_violation'],
                'avoid_when': ['simple_crud', 'tightly_coupled_state', 'performance_critical']
            },
            'composition_pattern': {
                'base_effort': '3-4 weeks',
                'complexity_factors': ['component_boundaries', 'interface_design', 'integration_complexity'],
                'best_when': ['multiple_concerns', 'flexible_design_needed', 'long_term_evolution'],
                'avoid_when': ['simple_use_case', 'tight_deadline', 'small_team']
            },
            'facade_pattern': {
                'base_effort': '3-5 days',
                'complexity_factors': ['interface_complexity', 'underlying_system_complexity'],
                'best_when': ['immediate_relief_needed', 'complex_subsystem', 'stable_interface'],
                'avoid_when': ['frequently_changing_interface', 'simple_underlying_system']
            }
        }
    
    def reason_through_recommendations(self, file_path: str, class_name: str, 
                                     line_count: int, context: Dict[str, Any] = None) -> RecommendationPlan:
        """
        Core HRM reasoning: analyze context and synthesize optimal recommendations
        """
        
        print(f"🧠 **HRM Recommendation Reasoning: {class_name}**")
        print("=" * 70)
        
        # Read and analyze the code
        with open(file_path, 'r') as f:
            code = f.read()
        
        tree = ast.parse(code)
        class_node = self._find_class_node(tree, class_name)
        
        if not class_node:
            return self._create_error_plan(class_name, "Class not found")
        
        # Step 1: Comprehensive context analysis
        context_analysis = self._analyze_comprehensive_context(
            file_path, class_node, code, line_count, context or {}
        )
        
        print(f"\n🔍 **Context Analysis Complete**:")
        print(f"   • Business Criticality: {context_analysis['business_criticality']}")
        print(f"   • Technical Debt Level: {context_analysis['technical_debt_level']}")
        print(f"   • Team Constraints: {context_analysis['team_constraints']}")
        print(f"   • Domain Maturity: {context_analysis['domain_maturity']}")
        
        # Step 2: Generate candidate recommendations with reasoning
        candidate_recommendations = self._generate_candidate_recommendations(
            class_node, code, line_count, context_analysis
        )
        
        print(f"\n🎯 **Generated {len(candidate_recommendations)} Candidate Recommendations**")
        
        # Step 3: Reason through each recommendation contextually
        reasoned_recommendations = []
        for candidate in candidate_recommendations:
            reasoned_rec = self._reason_through_single_recommendation(
                candidate, context_analysis, class_node, code, line_count
            )
            reasoned_recommendations.append(reasoned_rec)
        
        # Step 4: Select optimal recommendation through multi-criteria reasoning
        primary_recommendation = self._select_optimal_recommendation(
            reasoned_recommendations, context_analysis
        )
        
        # Step 5: Create implementation sequence
        sequencing_strategy = self._reason_through_sequencing(
            primary_recommendation, reasoned_recommendations, context_analysis
        )
        
        # Step 6: Synthesize final plan
        plan = RecommendationPlan(
            primary_recommendation=primary_recommendation,
            alternative_recommendations=[r for r in reasoned_recommendations if r != primary_recommendation],
            sequencing_strategy=sequencing_strategy,
            total_timeline=self._calculate_total_timeline(primary_recommendation, context_analysis),
            resource_requirements=self._analyze_resource_requirements(primary_recommendation, context_analysis),
            success_probability=self._estimate_success_probability(primary_recommendation, context_analysis),
            contextual_reasoning=self._generate_meta_reasoning(primary_recommendation, context_analysis)
        )
        
        self._print_reasoned_plan(plan)
        return plan
    
    def _analyze_comprehensive_context(self, file_path: str, class_node: ast.ClassDef, 
                                     code: str, line_count: int, provided_context: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive contextual analysis for recommendation reasoning"""
        
        # Domain context
        domain = self._extract_domain_from_path(file_path)
        domain_info = self._get_domain_characteristics(domain)
        
        # Business context
        business_criticality = self._assess_business_criticality(domain, code, class_node)
        user_impact = self._assess_user_impact(code, domain)
        revenue_impact = self._assess_revenue_impact(domain, code)
        
        # Technical context  
        technical_debt_level = self._assess_technical_debt_level(class_node, code, line_count)
        change_frequency = self._assess_change_frequency(domain, code, class_node)
        complexity_type = self._classify_complexity_type(class_node, code)
        
        # Team context
        team_constraints = self._assess_team_constraints(domain, line_count)
        available_time = self._assess_available_time(business_criticality, technical_debt_level)
        risk_tolerance = self._assess_risk_tolerance(business_criticality, user_impact)
        
        # Code-specific context
        refactoring_safety = self._assess_refactoring_safety(class_node, code)
        architectural_patterns = self._identify_architectural_patterns(code, file_path)
        dependency_complexity = self._analyze_dependency_complexity(class_node, code)
        
        return {
            'domain': domain,
            'domain_info': domain_info,
            'domain_maturity': domain_info.get('evolution_rate', 'medium'),
            'business_criticality': business_criticality,
            'user_impact': user_impact,
            'revenue_impact': revenue_impact,
            'technical_debt_level': technical_debt_level,
            'change_frequency': change_frequency,
            'complexity_type': complexity_type,
            'team_constraints': team_constraints,
            'available_time': available_time,
            'risk_tolerance': risk_tolerance,
            'refactoring_safety': refactoring_safety,
            'architectural_patterns': architectural_patterns,
            'dependency_complexity': dependency_complexity,
            'line_count': line_count,
            'method_count': len([n for n in class_node.body if isinstance(n, ast.FunctionDef)])
        }
    
    def _generate_candidate_recommendations(self, class_node: ast.ClassDef, code: str, 
                                          line_count: int, context: Dict[str, Any]) -> List[str]:
        """Generate candidate recommendations based on analysis"""
        
        candidates = []
        
        # Size-based candidates
        if line_count > 200:
            candidates.append('extract_value_objects')
            candidates.append('extract_domain_services')
            candidates.append('facade_pattern')
        
        if line_count > 400:
            candidates.append('composition_pattern')
        
        # Complexity-based candidates
        if context['method_count'] > 15:
            candidates.append('extract_domain_services')
        
        # Domain-specific candidates
        if context['domain'] == 'nft':
            candidates.append('extract_value_objects')  # NFT metadata, attributes
        
        # Pattern-based candidates
        if 'entity' in code.lower() and context['complexity_type'] == 'business_logic':
            candidates.append('extract_domain_services')
        
        return list(set(candidates))  # Remove duplicates
    
    def _reason_through_single_recommendation(self, recommendation: str, context: Dict[str, Any],
                                            class_node: ast.ClassDef, code: str, line_count: int) -> ReasonedRecommendation:
        """Deep reasoning about a single recommendation in this specific context"""
        
        template = self.recommendation_templates.get(recommendation, {})
        
        # Context-specific reasoning
        reasoning_steps = []
        reasoning_steps.append(f"1. Analyzing {recommendation} for {context['domain']} domain with {line_count} lines")
        
        # Business alignment reasoning
        business_alignment = self._reason_business_alignment(recommendation, context)
        reasoning_steps.append(f"2. Business alignment: {business_alignment}")
        
        # Technical feasibility reasoning
        technical_feasibility = self._reason_technical_feasibility(recommendation, context, class_node, code)
        reasoning_steps.append(f"3. Technical feasibility: {technical_feasibility}")
        
        # Risk assessment reasoning
        risk_assessment = self._reason_risk_assessment(recommendation, context)
        reasoning_steps.append(f"4. Risk assessment: {risk_assessment}")
        
        # Resource requirement reasoning
        resource_reasoning = self._reason_resource_requirements(recommendation, context, template)
        reasoning_steps.append(f"5. Resource analysis: {resource_reasoning}")
        
        # Context-specific "why this recommendation" reasoning
        why_this_context = self._reason_why_this_context(recommendation, context, class_node, code)
        
        # Calculate confidence based on reasoning
        confidence = self._calculate_recommendation_confidence(
            business_alignment, technical_feasibility, risk_assessment, context
        )
        
        # Determine trade-offs
        trade_offs = self._analyze_trade_offs(recommendation, context)
        
        # Generate implementation guidance
        implementation_guidance = self._generate_implementation_guidance(
            recommendation, context, class_node, code
        )
        
        return ReasonedRecommendation(
            recommendation=recommendation,
            reasoning_type=self._determine_reasoning_type(recommendation, context),
            confidence=confidence,
            effort_estimate=self._adjust_effort_estimate(template.get('base_effort', 'Unknown'), context),
            business_value=self._assess_business_value(recommendation, context),
            risk_level=self._assess_recommendation_risk(recommendation, context),
            prerequisites=self._identify_prerequisites(recommendation, context),
            success_metrics=self._define_success_metrics(recommendation, context),
            reasoning_steps=reasoning_steps,
            trade_offs=trade_offs,
            implementation_guidance=implementation_guidance,
            why_this_context=why_this_context
        )
    
    def _reason_business_alignment(self, recommendation: str, context: Dict[str, Any]) -> str:
        """Reason about how well this recommendation aligns with business needs"""
        
        if context['business_criticality'] == 'critical' and context['available_time'] == 'limited':
            if recommendation == 'facade_pattern':
                return "HIGH - Facade provides immediate relief for critical system with minimal disruption"
            elif recommendation == 'composition_pattern':
                return "LOW - Too much effort for critical system under time pressure"
        
        if context['revenue_impact'] == 'high' and recommendation == 'extract_value_objects':
            return "HIGH - Value objects reduce bug risk in revenue-critical code"
        
        if context['user_impact'] == 'high' and context['change_frequency'] == 'high':
            if recommendation == 'extract_domain_services':
                return "HIGH - Separates business logic for safer changes in user-facing code"
        
        return "MEDIUM - Standard business alignment"
    
    def _reason_technical_feasibility(self, recommendation: str, context: Dict[str, Any], 
                                    class_node: ast.ClassDef, code: str) -> str:
        """Reason about technical feasibility in this specific codebase"""
        
        if recommendation == 'extract_value_objects':
            # Check for clear value object candidates
            has_complex_attributes = self._has_complex_attributes(class_node, code)
            has_validation_logic = self._has_validation_logic(class_node, code)
            
            if has_complex_attributes and has_validation_logic:
                return "HIGH - Clear value object candidates with validation logic detected"
            elif has_complex_attributes:
                return "MEDIUM - Complex attributes present but minimal validation"
            else:
                return "LOW - No clear value object extraction opportunities"
        
        if recommendation == 'extract_domain_services':
            # Check for business logic methods
            business_methods = self._identify_business_methods(class_node, code)
            if len(business_methods) > 5:
                return "HIGH - Multiple business methods identified for extraction"
            elif len(business_methods) > 2:
                return "MEDIUM - Some business methods could be extracted"
            else:
                return "LOW - Limited business logic to extract"
        
        if recommendation == 'composition_pattern':
            # Check for clear component boundaries
            component_boundaries = self._identify_component_boundaries(class_node, code)
            if len(component_boundaries) >= 3:
                return "HIGH - Clear component boundaries identified"
            elif len(component_boundaries) == 2:
                return "MEDIUM - Some component separation possible"
            else:
                return "LOW - Unclear component boundaries"
        
        return "MEDIUM - Standard technical feasibility"
    
    def _reason_risk_assessment(self, recommendation: str, context: Dict[str, Any]) -> str:
        """Reason about risks specific to this recommendation and context"""
        
        risk_factors = []
        
        if context['refactoring_safety'] == 'low':
            risk_factors.append("Low refactoring safety due to limited test coverage")
        
        if context['change_frequency'] == 'very_high':
            risk_factors.append("High change frequency increases refactoring coordination complexity")
        
        if context['dependency_complexity'] == 'high':
            risk_factors.append("Complex dependencies increase refactoring risk")
        
        if recommendation == 'composition_pattern' and context['team_constraints'] == 'small_team':
            risk_factors.append("Complex pattern may overwhelm small team")
        
        if recommendation == 'facade_pattern' and context['change_frequency'] == 'very_high':
            risk_factors.append("Facade may become bottleneck with frequent interface changes")
        
        if not risk_factors:
            return "LOW - No significant risk factors identified"
        elif len(risk_factors) == 1:
            return f"MEDIUM - {risk_factors[0]}"
        else:
            return f"HIGH - Multiple risks: {'; '.join(risk_factors[:2])}"
    
    def _reason_resource_requirements(self, recommendation: str, context: Dict[str, Any], 
                                    template: Dict[str, Any]) -> str:
        """Reason about resource requirements in this specific context"""
        
        base_effort = template.get('base_effort', 'Unknown')
        
        # Adjust based on context
        if context['team_constraints'] == 'small_team':
            return f"{base_effort} but will require 30% more time due to small team coordination"
        
        if context['technical_debt_level'] == 'high':
            return f"{base_effort} plus additional time for debt cleanup"
        
        if context['refactoring_safety'] == 'low':
            return f"{base_effort} plus significant time for test creation"
        
        if context['complexity_type'] == 'high_coupling':
            return f"{base_effort} plus extra time for dependency untangling"
        
        return f"{base_effort} - standard effort for this context"
    
    def _reason_why_this_context(self, recommendation: str, context: Dict[str, Any], 
                               class_node: ast.ClassDef, code: str) -> str:
        """Explain why this specific recommendation makes sense for THIS particular situation"""
        
        reasons = []
        
        if recommendation == 'extract_value_objects':
            if context['domain'] == 'nft':
                reasons.append("NFT entities have rich metadata that forms natural value objects")
            if self._has_validation_logic(class_node, code):
                reasons.append("Existing validation logic can be encapsulated in value objects")
            if context['revenue_impact'] == 'high':
                reasons.append("Value objects reduce bug risk in revenue-critical attributes")
        
        elif recommendation == 'extract_domain_services':
            if context['complexity_type'] == 'business_logic':
                reasons.append("Entity contains business logic that belongs in domain services")
            if context['change_frequency'] == 'high':
                reasons.append("Separating business logic enables safer changes")
            if len(self._identify_business_methods(class_node, code)) > 5:
                reasons.append("Multiple business operations identified for extraction")
        
        elif recommendation == 'composition_pattern':
            if context['line_count'] > 400:
                reasons.append("Large size indicates multiple responsibilities that can be composed")
            if context['domain_info'].get('evolution_rate') == 'high':
                reasons.append("Composition enables flexible evolution in rapidly changing domain")
        
        elif recommendation == 'facade_pattern':
            if context['business_criticality'] == 'critical' and context['available_time'] == 'limited':
                reasons.append("Provides immediate relief for critical system under time pressure")
            if context['complexity_type'] == 'interface_complexity':
                reasons.append("Simplifies complex interface for easier usage")
        
        if not reasons:
            return "Standard refactoring approach for large class"
        
        return f"Specifically recommended because: {' • '.join(reasons)}"
    
    def _select_optimal_recommendation(self, recommendations: List[ReasonedRecommendation], 
                                     context: Dict[str, Any]) -> ReasonedRecommendation:
        """Multi-criteria reasoning to select the optimal recommendation"""
        
        print(f"\n🎯 **Multi-Criteria Recommendation Selection**:")
        
        # Define decision criteria with weights based on context
        criteria_weights = self._determine_criteria_weights(context)
        
        print(f"   • Criteria weights: Business Value ({criteria_weights['business_value']:.1f}), "
              f"Feasibility ({criteria_weights['feasibility']:.1f}), Risk ({criteria_weights['risk']:.1f})")
        
        # Score each recommendation
        scored_recommendations = []
        for rec in recommendations:
            score = self._calculate_multi_criteria_score(rec, criteria_weights)
            scored_recommendations.append((rec, score))
            print(f"   • {rec.recommendation}: {score:.2f} score (confidence: {rec.confidence:.1%})")
        
        # Select highest scoring recommendation
        optimal_rec = max(scored_recommendations, key=lambda x: x[1])[0]
        
        print(f"   🏆 **Selected**: {optimal_rec.recommendation}")
        
        return optimal_rec
    
    def _reason_through_sequencing(self, primary: ReasonedRecommendation, 
                                 alternatives: List[ReasonedRecommendation], 
                                 context: Dict[str, Any]) -> str:
        """Reason through optimal sequencing of recommendations"""
        
        if context['available_time'] == 'limited':
            return f"Execute {primary.recommendation} immediately, defer alternatives until next planning cycle"
        
        if context['business_criticality'] == 'critical':
            return f"Phase 1: {primary.recommendation} for immediate impact. Phase 2: Consider alternatives based on results"
        
        # Look for synergistic sequencing
        if primary.recommendation == 'extract_value_objects':
            service_extraction = next((r for r in alternatives if r.recommendation == 'extract_domain_services'), None)
            if service_extraction:
                return f"Optimal sequence: 1) Extract value objects first (foundation), 2) Extract domain services (business logic)"
        
        return f"Focus on {primary.recommendation} with incremental approach based on learning"
    
    def _calculate_total_timeline(self, primary: ReasonedRecommendation, context: Dict[str, Any]) -> str:
        """Calculate realistic total timeline based on context"""
        
        base_timeline = primary.effort_estimate
        
        if context['team_constraints'] == 'small_team':
            return f"{base_timeline} + 30% for small team coordination"
        
        if context['refactoring_safety'] == 'low':
            return f"{base_timeline} + test creation time"
        
        return base_timeline
    
    def _estimate_success_probability(self, primary: ReasonedRecommendation, context: Dict[str, Any]) -> float:
        """Estimate success probability based on contextual factors"""
        
        base_probability = primary.confidence
        
        # Adjust based on context
        if context['refactoring_safety'] == 'high':
            base_probability += 0.1
        elif context['refactoring_safety'] == 'low':
            base_probability -= 0.2
        
        if context['team_constraints'] == 'experienced_team':
            base_probability += 0.1
        elif context['team_constraints'] == 'small_team':
            base_probability -= 0.1
        
        return max(0.0, min(1.0, base_probability))
    
    def _generate_meta_reasoning(self, primary: ReasonedRecommendation, context: Dict[str, Any]) -> List[str]:
        """Generate meta-reasoning about the recommendation selection process"""
        
        meta_reasoning = []
        
        meta_reasoning.append(f"Selected {primary.recommendation} based on {context['business_criticality']} business criticality")
        meta_reasoning.append(f"Context factors: {context['domain']} domain, {context['technical_debt_level']} technical debt")
        meta_reasoning.append(f"Key constraint: {context['available_time']} time availability")
        meta_reasoning.append(f"Success factors: {primary.confidence:.1%} confidence, {primary.risk_level} risk")
        
        return meta_reasoning
    
    # Helper methods (many abbreviated for space)
    
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
    
    def _get_domain_characteristics(self, domain: str) -> Dict[str, Any]:
        domain_chars = {
            'nft': {'evolution_rate': 'high', 'business_impact': 'high', 'complexity': 'high'},
            'trading': {'evolution_rate': 'high', 'business_impact': 'critical', 'complexity': 'very_high'},
            'gamification': {'evolution_rate': 'medium', 'business_impact': 'medium', 'complexity': 'medium'}
        }
        return domain_chars.get(domain, {'evolution_rate': 'medium', 'business_impact': 'medium', 'complexity': 'medium'})
    
    def _assess_business_criticality(self, domain: str, code: str, class_node: ast.ClassDef) -> str:
        if domain == 'trading':
            return 'critical'
        elif domain == 'nft' and ('mint' in code.lower() or 'transfer' in code.lower()):
            return 'high'
        elif 'user' in code.lower() or 'payment' in code.lower():
            return 'high'
        else:
            return 'medium'
    
    def _assess_user_impact(self, code: str, domain: str) -> str:
        if any(word in code.lower() for word in ['user', 'client', 'frontend', 'api']):
            return 'high'
        elif domain in ['nft', 'gamification']:
            return 'medium'
        else:
            return 'low'
    
    def _assess_revenue_impact(self, domain: str, code: str) -> str:
        if domain == 'nft' or 'payment' in code.lower() or 'transaction' in code.lower():
            return 'high'
        elif domain == 'trading':
            return 'critical'
        else:
            return 'low'
    
    def _assess_technical_debt_level(self, class_node: ast.ClassDef, code: str, line_count: int) -> str:
        debt_indicators = 0
        
        if line_count > 400:
            debt_indicators += 2
        elif line_count > 250:
            debt_indicators += 1
        
        # Check for code smells
        if code.count('# TODO') > 3:
            debt_indicators += 1
        
        if code.count('# FIXME') > 0:
            debt_indicators += 1
        
        # Check method complexity
        complex_methods = 0
        for node in class_node.body:
            if isinstance(node, ast.FunctionDef):
                complexity = self._calculate_method_complexity(node)
                if complexity > 10:
                    complex_methods += 1
        
        if complex_methods > 3:
            debt_indicators += 1
        
        if debt_indicators >= 4:
            return 'critical'
        elif debt_indicators >= 2:
            return 'high'
        elif debt_indicators >= 1:
            return 'medium'
        else:
            return 'low'
    
    def _calculate_method_complexity(self, method_node: ast.FunctionDef) -> int:
        complexity = 1
        for node in ast.walk(method_node):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
        return complexity
    
    def _assess_change_frequency(self, domain: str, code: str, class_node: ast.ClassDef) -> str:
        if domain in ['nft', 'gamification']:
            return 'high'  # Evolving domains
        elif domain == 'trading':
            return 'very_high'  # Constantly changing
        else:
            return 'medium'
    
    def _classify_complexity_type(self, class_node: ast.ClassDef, code: str) -> str:
        business_methods = len(self._identify_business_methods(class_node, code))
        if business_methods > 8:
            return 'business_logic'
        elif self._has_complex_attributes(class_node, code):
            return 'data_complexity'
        elif self._analyze_dependency_complexity(class_node, code) == 'high':
            return 'high_coupling'
        else:
            return 'interface_complexity'
    
    def _assess_team_constraints(self, domain: str, line_count: int) -> str:
        # Simplified heuristic
        if line_count > 500:
            return 'experienced_team'  # Assumes complex code needs experienced team
        else:
            return 'small_team'
    
    def _assess_available_time(self, business_criticality: str, technical_debt_level: str) -> str:
        if business_criticality == 'critical' and technical_debt_level in ['high', 'critical']:
            return 'limited'
        elif business_criticality in ['high', 'critical']:
            return 'moderate'
        else:
            return 'flexible'
    
    def _assess_risk_tolerance(self, business_criticality: str, user_impact: str) -> str:
        if business_criticality == 'critical' or user_impact == 'high':
            return 'low'
        elif business_criticality == 'high':
            return 'medium'
        else:
            return 'high'
    
    def _assess_refactoring_safety(self, class_node: ast.ClassDef, code: str) -> str:
        # Check for test indicators
        if 'test' in code.lower() or 'mock' in code.lower():
            return 'high'
        elif 'assert' in code.lower():
            return 'medium'
        else:
            return 'low'
    
    def _identify_architectural_patterns(self, code: str, file_path: str) -> List[str]:
        patterns = []
        if 'service' in file_path.lower():
            patterns.append('domain_service')
        if 'entity' in file_path.lower():
            patterns.append('entity')
        if '@dataclass' in code:
            patterns.append('value_object')
        return patterns
    
    def _analyze_dependency_complexity(self, class_node: ast.ClassDef, code: str) -> str:
        import_count = code.count('import ') + code.count('from ')
        if import_count > 15:
            return 'high'
        elif import_count > 8:
            return 'medium'
        else:
            return 'low'
    
    def _has_complex_attributes(self, class_node: ast.ClassDef, code: str) -> bool:
        # Look for complex attribute patterns
        return any(word in code.lower() for word in ['metadata', 'attributes', 'properties', 'config'])
    
    def _has_validation_logic(self, class_node: ast.ClassDef, code: str) -> bool:
        return any(word in code.lower() for word in ['validate', 'check', 'verify', 'assert'])
    
    def _identify_business_methods(self, class_node: ast.ClassDef, code: str) -> List[str]:
        business_methods = []
        for node in class_node.body:
            if isinstance(node, ast.FunctionDef):
                if any(word in node.name.lower() for word in ['create', 'update', 'process', 'calculate', 'execute']):
                    business_methods.append(node.name)
        return business_methods
    
    def _identify_component_boundaries(self, class_node: ast.ClassDef, code: str) -> List[str]:
        # Simplified component boundary detection
        boundaries = []
        if 'metadata' in code.lower():
            boundaries.append('metadata_component')
        if 'validation' in code.lower():
            boundaries.append('validation_component')
        if 'calculation' in code.lower():
            boundaries.append('calculation_component')
        return boundaries
    
    def _calculate_recommendation_confidence(self, business_alignment: str, technical_feasibility: str, 
                                          risk_assessment: str, context: Dict[str, Any]) -> float:
        score = 0.0
        
        if 'HIGH' in business_alignment:
            score += 0.4
        elif 'MEDIUM' in business_alignment:
            score += 0.2
        
        if 'HIGH' in technical_feasibility:
            score += 0.3
        elif 'MEDIUM' in technical_feasibility:
            score += 0.15
        
        if 'LOW' in risk_assessment:
            score += 0.3
        elif 'MEDIUM' in risk_assessment:
            score += 0.15
        
        return max(0.1, min(1.0, score))
    
    def _determine_reasoning_type(self, recommendation: str, context: Dict[str, Any]) -> RecommendationReasoning:
        if context['business_criticality'] == 'critical':
            return RecommendationReasoning.BUSINESS_PRIORITY
        elif context['risk_tolerance'] == 'low':
            return RecommendationReasoning.RISK_MITIGATION
        elif context['available_time'] == 'limited':
            return RecommendationReasoning.COST_OPTIMIZATION
        else:
            return RecommendationReasoning.TECHNICAL_FEASIBILITY
    
    def _adjust_effort_estimate(self, base_effort: str, context: Dict[str, Any]) -> str:
        if context['team_constraints'] == 'small_team':
            return f"{base_effort} (+30% for small team)"
        elif context['refactoring_safety'] == 'low':
            return f"{base_effort} (+test creation)"
        else:
            return base_effort
    
    def _assess_business_value(self, recommendation: str, context: Dict[str, Any]) -> str:
        if context['business_criticality'] == 'critical':
            return 'High - Critical business functionality'
        elif context['revenue_impact'] == 'high':
            return 'High - Revenue impact'
        elif context['user_impact'] == 'high':
            return 'Medium - User experience impact'
        else:
            return 'Medium - Technical improvement'
    
    def _assess_recommendation_risk(self, recommendation: str, context: Dict[str, Any]) -> str:
        if recommendation == 'facade_pattern':
            return 'Low - Minimal disruption'
        elif context['refactoring_safety'] == 'low':
            return 'High - Limited test coverage'
        elif context['dependency_complexity'] == 'high':
            return 'Medium - Complex dependencies'
        else:
            return 'Low - Standard refactoring risk'
    
    def _identify_prerequisites(self, recommendation: str, context: Dict[str, Any]) -> List[str]:
        prereqs = []
        if context['refactoring_safety'] == 'low':
            prereqs.append('Create comprehensive test suite')
        if recommendation in ['extract_domain_services', 'composition_pattern']:
            prereqs.append('Identify clear component boundaries')
        return prereqs
    
    def _define_success_metrics(self, recommendation: str, context: Dict[str, Any]) -> List[str]:
        metrics = []
        if recommendation == 'extract_value_objects':
            metrics.extend(['Reduced class size by 30%', 'Improved attribute encapsulation', 'Cleaner validation logic'])
        elif recommendation == 'extract_domain_services':
            metrics.extend(['Separated business logic', 'Improved testability', 'Better single responsibility'])
        return metrics
    
    def _analyze_trade_offs(self, recommendation: str, context: Dict[str, Any]) -> Dict[str, str]:
        trade_offs = {}
        
        if recommendation == 'extract_value_objects':
            trade_offs['Benefits'] = 'Better encapsulation, reduced complexity'
            trade_offs['Costs'] = 'More classes to maintain, potential over-engineering'
        elif recommendation == 'facade_pattern':
            trade_offs['Benefits'] = 'Immediate simplification, quick implementation'
            trade_offs['Costs'] = 'Hidden complexity, potential bottleneck'
        
        return trade_offs
    
    def _generate_implementation_guidance(self, recommendation: str, context: Dict[str, Any], 
                                        class_node: ast.ClassDef, code: str) -> str:
        if recommendation == 'extract_value_objects' and context['domain'] == 'nft':
            return "Start with NFTMetadata as clear value object candidate, then extract NFTAttributes and NFTRoyalty"
        elif recommendation == 'extract_domain_services':
            business_methods = self._identify_business_methods(class_node, code)
            return f"Extract {business_methods[0] if business_methods else 'business methods'} into dedicated service class"
        else:
            return f"Standard {recommendation} implementation approach"
    
    def _determine_criteria_weights(self, context: Dict[str, Any]) -> Dict[str, float]:
        if context['business_criticality'] == 'critical':
            return {'business_value': 0.5, 'feasibility': 0.3, 'risk': 0.2}
        elif context['available_time'] == 'limited':
            return {'business_value': 0.3, 'feasibility': 0.5, 'risk': 0.2}
        else:
            return {'business_value': 0.4, 'feasibility': 0.4, 'risk': 0.2}
    
    def _calculate_multi_criteria_score(self, recommendation: ReasonedRecommendation, 
                                      criteria_weights: Dict[str, float]) -> float:
        business_score = {'High': 1.0, 'Medium': 0.6, 'Low': 0.2}.get(recommendation.business_value.split(' - ')[0], 0.5)
        feasibility_score = recommendation.confidence
        risk_score = {'Low': 1.0, 'Medium': 0.6, 'High': 0.2}.get(recommendation.risk_level.split(' - ')[0], 0.5)
        
        total_score = (
            business_score * criteria_weights['business_value'] +
            feasibility_score * criteria_weights['feasibility'] +
            risk_score * criteria_weights['risk']
        )
        
        return total_score
    
    def _analyze_resource_requirements(self, recommendation: ReasonedRecommendation, context: Dict[str, Any]) -> Dict[str, Any]:
        return {
            'time_estimate': recommendation.effort_estimate,
            'skill_level': 'Senior' if 'composition' in recommendation.recommendation else 'Mid-level',
            'team_size': '1-2 developers',
            'external_dependencies': recommendation.prerequisites
        }
    
    def _create_error_plan(self, class_name: str, error: str) -> RecommendationPlan:
        error_rec = ReasonedRecommendation(
            recommendation="manual_analysis_required",
            reasoning_type=RecommendationReasoning.TECHNICAL_FEASIBILITY,
            confidence=0.0,
            effort_estimate="Unknown",
            business_value="Unknown",
            risk_level="Unknown",
            prerequisites=[],
            success_metrics=[],
            reasoning_steps=[error],
            trade_offs={},
            implementation_guidance="Manual analysis required",
            why_this_context=error
        )
        
        return RecommendationPlan(
            primary_recommendation=error_rec,
            alternative_recommendations=[],
            sequencing_strategy="Address error first",
            total_timeline="Unknown",
            resource_requirements={},
            success_probability=0.0,
            contextual_reasoning=[error]
        )
    
    def _print_reasoned_plan(self, plan: RecommendationPlan) -> None:
        """Print the complete reasoned recommendation plan"""
        
        print(f"\n" + "=" * 80)
        print(f"🎯 **REASONED RECOMMENDATION PLAN**")
        print(f"=" * 80)
        
        primary = plan.primary_recommendation
        
        print(f"\n🏆 **PRIMARY RECOMMENDATION**: {primary.recommendation.upper()}")
        print(f"   **Confidence**: {primary.confidence:.1%}")
        print(f"   **Business Value**: {primary.business_value}")
        print(f"   **Risk Level**: {primary.risk_level}")
        print(f"   **Effort**: {primary.effort_estimate}")
        
        print(f"\n🧠 **WHY THIS RECOMMENDATION FOR THIS CONTEXT**:")
        print(f"   {primary.why_this_context}")
        
        print(f"\n🔍 **REASONING PROCESS**:")
        for step in primary.reasoning_steps:
            print(f"   {step}")
        
        print(f"\n⚖️  **TRADE-OFFS ANALYSIS**:")
        for key, value in primary.trade_offs.items():
            print(f"   **{key}**: {value}")
        
        print(f"\n📋 **PREREQUISITES**:")
        if primary.prerequisites:
            for prereq in primary.prerequisites:
                print(f"   • {prereq}")
        else:
            print(f"   • No specific prerequisites")
        
        print(f"\n🎯 **SUCCESS METRICS**:")
        for metric in primary.success_metrics:
            print(f"   • {metric}")
        
        print(f"\n🚀 **IMPLEMENTATION GUIDANCE**:")
        print(f"   {primary.implementation_guidance}")
        
        print(f"\n📅 **SEQUENCING STRATEGY**:")
        print(f"   {plan.sequencing_strategy}")
        
        print(f"\n📊 **RESOURCE REQUIREMENTS**:")
        for key, value in plan.resource_requirements.items():
            print(f"   • **{key.title()}**: {value}")
        
        print(f"\n🎲 **SUCCESS PROBABILITY**: {plan.success_probability:.1%}")
        
        if plan.alternative_recommendations:
            print(f"\n🔄 **ALTERNATIVE RECOMMENDATIONS** ({len(plan.alternative_recommendations)} options):")
            for i, alt in enumerate(plan.alternative_recommendations[:2], 1):
                print(f"   {i}. **{alt.recommendation}** - {alt.confidence:.1%} confidence")
                print(f"      {alt.why_this_context}")
        
        print(f"\n🧠 **META-REASONING SUMMARY**:")
        for reasoning in plan.contextual_reasoning:
            print(f"   • {reasoning}")

def main():
    import sys
    
    if len(sys.argv) != 4:
        print("Usage: python reasoning_recommender.py <file_path> <class_name> <line_count>")
        print("Example: python reasoning_recommender.py entities.py GenesisNFT 330")
        sys.exit(1)
    
    file_path = sys.argv[1]
    class_name = sys.argv[2]
    line_count = int(sys.argv[3])
    
    recommender = ReasoningRecommender()
    plan = recommender.reason_through_recommendations(file_path, class_name, line_count)
    
    print(f"\n🎉 **REASONING COMPLETE**")
    print(f"   **Recommendation**: {plan.primary_recommendation.recommendation}")
    print(f"   **Success Probability**: {plan.success_probability:.1%}")

if __name__ == "__main__":
    main()