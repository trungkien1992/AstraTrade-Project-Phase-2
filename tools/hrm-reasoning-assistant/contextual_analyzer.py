#!/usr/bin/env python3
"""
Contextual HRM Analyzer

Enhanced HRM tool that reasons about WHEN rules should apply vs when they should be relaxed.
This demonstrates true hierarchical reasoning that considers context, trade-offs, and business logic.
"""

import ast
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class ClassSizeJustification(Enum):
    ACCEPTABLE = "acceptable"
    CONCERNING = "concerning" 
    UNACCEPTABLE = "unacceptable"

@dataclass
class ContextualAnalysis:
    finding: str
    justification: ClassSizeJustification
    reasoning_steps: List[str]
    evidence: Dict[str, Any]
    confidence: float
    recommendation: str

class ContextualHRMAnalyzer:
    """HRM analyzer that reasons about context, not just rules"""
    
    def __init__(self):
        self.domain_patterns = {
            'domain_service': ['service', 'domain'],
            'aggregate_root': ['aggregate', 'root'],
            'consolidation': ['consolidat', 'combin', 'unif'],
            'facade': ['facade', 'wrapper', 'interface'],
            'orchestrator': ['orchestrat', 'coordinat', 'manage']
        }
    
    def analyze_large_class_context(self, file_path: str, class_name: str, line_count: int) -> ContextualAnalysis:
        """
        Perform hierarchical reasoning about whether a large class is justified
        
        This is the core HRM reasoning: high-level architectural analysis combined
        with low-level implementation details to make contextual judgments.
        """
        
        print(f"🧠 **HRM Contextual Reasoning: {class_name} ({line_count} lines)**")
        print("=" * 70)
        
        # Read the file for deep analysis
        with open(file_path, 'r') as f:
            code = f.read()
        
        tree = ast.parse(code)
        class_node = self._find_class_node(tree, class_name)
        
        if not class_node:
            return self._create_analysis("Class not found", ClassSizeJustification.CONCERNING, 0.0)
        
        # Multi-level HRM reasoning
        architectural_analysis = self._analyze_architectural_context(code, class_node, file_path)
        consolidation_analysis = self._analyze_consolidation_context(code, class_node)
        responsibility_analysis = self._analyze_responsibility_coherence(class_node, code)
        complexity_analysis = self._analyze_internal_complexity(class_node, code)
        maintainability_analysis = self._analyze_maintainability_factors(class_node, code)
        
        # Hierarchical synthesis - this is where HRM shines
        final_reasoning = self._synthesize_contextual_judgment(
            line_count,
            architectural_analysis,
            consolidation_analysis, 
            responsibility_analysis,
            complexity_analysis,
            maintainability_analysis
        )
        
        self._print_reasoning_process(final_reasoning)
        return final_reasoning
    
    def _analyze_architectural_context(self, code: str, class_node: ast.ClassDef, file_path: str) -> Dict[str, Any]:
        """High-level architectural reasoning"""
        
        architectural_patterns = []
        justifications = []
        
        # Domain Service Pattern Analysis
        if any(pattern in class_node.name.lower() for pattern in self.domain_patterns['domain_service']):
            architectural_patterns.append("Domain Service")
            justifications.append("Domain services can be large when they consolidate business logic")
        
        # Facade Pattern Analysis
        if any(pattern in code.lower() for pattern in self.domain_patterns['facade']):
            architectural_patterns.append("Facade Pattern")
            justifications.append("Facade classes legitimately aggregate multiple subsystem interfaces")
        
        # Consolidation Pattern Analysis
        consolidation_comments = self._extract_consolidation_comments(code)
        if consolidation_comments:
            architectural_patterns.append("Consolidation Pattern")
            justifications.append("Consolidation services intentionally combine multiple smaller services")
        
        # File path context
        path_context = self._analyze_path_context(file_path)
        
        return {
            'patterns': architectural_patterns,
            'justifications': justifications,
            'consolidation_comments': consolidation_comments,
            'path_context': path_context,
            'architecture_score': len(architectural_patterns) * 2  # Higher score = more architectural justification
        }
    
    def _analyze_consolidation_context(self, code: str, class_node: ast.ClassDef) -> Dict[str, Any]:
        """Analyze if large size is due to legitimate consolidation"""
        
        # Look for consolidation evidence in comments and docstrings
        consolidation_evidence = []
        reduction_metrics = {}
        
        # Check docstring for consolidation info
        docstring = ast.get_docstring(class_node)
        if docstring:
            # Look for line count reductions
            line_reduction_pattern = r'(\d+,?\d*)\s*lines?\s*→\s*(\d+,?\d*)\s*lines?.*?(\d+)%\s*reduction'
            matches = re.findall(line_reduction_pattern, docstring, re.IGNORECASE)
            
            if matches:
                for match in matches:
                    before_lines = int(match[0].replace(',', ''))
                    after_lines = int(match[1].replace(',', ''))
                    reduction_pct = int(match[2])
                    
                    reduction_metrics = {
                        'before_lines': before_lines,
                        'after_lines': after_lines,
                        'reduction_percentage': reduction_pct
                    }
                    consolidation_evidence.append(f"Documented {reduction_pct}% code reduction")
            
            # Look for service consolidation mentions
            if any(keyword in docstring.lower() for keyword in ['consolidat', 'combin', 'unif', 'merge']):
                consolidation_evidence.append("Explicit consolidation mentioned in documentation")
        
        # Look for multiple repository dependencies (sign of consolidation)
        dependencies = self._count_repository_dependencies(class_node)
        if dependencies > 3:
            consolidation_evidence.append(f"Multiple repository dependencies ({dependencies}) suggest consolidation")
        
        return {
            'evidence': consolidation_evidence,
            'reduction_metrics': reduction_metrics,
            'repository_count': dependencies,
            'consolidation_score': len(consolidation_evidence) * 3
        }
    
    def _analyze_responsibility_coherence(self, class_node: ast.ClassDef, code: str) -> Dict[str, Any]:
        """Analyze if the class has coherent, related responsibilities"""
        
        method_groups = self._group_methods_by_purpose(class_node)
        
        # Calculate coherence metrics
        coherence_indicators = []
        
        # Check for clear method grouping
        if len(method_groups) <= 5:  # Good grouping
            coherence_indicators.append("Methods group into clear functional areas")
        
        # Check for consistent naming patterns
        method_names = [method.name for method in class_node.body if isinstance(method, ast.FunctionDef)]
        naming_patterns = self._analyze_naming_patterns(method_names)
        
        if naming_patterns['consistent_patterns']:
            coherence_indicators.append("Consistent method naming patterns indicate coherent functionality")
        
        # Check for domain-specific coherence
        domain_coherence = self._check_domain_coherence(code)
        coherence_indicators.extend(domain_coherence)
        
        return {
            'method_groups': method_groups,
            'coherence_indicators': coherence_indicators,
            'naming_patterns': naming_patterns,
            'coherence_score': len(coherence_indicators) * 2
        }
    
    def _analyze_internal_complexity(self, class_node: ast.ClassDef, code: str) -> Dict[str, Any]:
        """Analyze the internal complexity vs just size"""
        
        complexity_factors = {
            'cyclomatic_complexity': 0,
            'nested_depth': 0,
            'method_complexity': [],
            'branching_factor': 0
        }
        
        total_complexity = 0
        complex_methods = []
        
        for node in ast.walk(class_node):
            if isinstance(node, ast.FunctionDef):
                method_complexity = self._calculate_method_complexity(node)
                complexity_factors['method_complexity'].append({
                    'name': node.name,
                    'complexity': method_complexity
                })
                
                if method_complexity > 10:  # High complexity threshold
                    complex_methods.append(f"{node.name} (complexity: {method_complexity})")
                
                total_complexity += method_complexity
        
        # Calculate average complexity per method
        method_count = len([n for n in class_node.body if isinstance(n, ast.FunctionDef)])
        avg_complexity = total_complexity / method_count if method_count > 0 else 0
        
        return {
            'total_complexity': total_complexity,
            'average_method_complexity': avg_complexity,
            'complex_methods': complex_methods,
            'complexity_assessment': self._assess_complexity_level(avg_complexity)
        }
    
    def _analyze_maintainability_factors(self, class_node: ast.ClassDef, code: str) -> Dict[str, Any]:
        """Analyze factors that affect maintainability despite size"""
        
        maintainability_factors = []
        
        # Check for good documentation
        documented_methods = sum(1 for node in class_node.body 
                               if isinstance(node, ast.FunctionDef) and ast.get_docstring(node))
        total_methods = sum(1 for node in class_node.body if isinstance(node, ast.FunctionDef))
        
        doc_ratio = documented_methods / total_methods if total_methods > 0 else 0
        if doc_ratio > 0.8:
            maintainability_factors.append("High documentation coverage aids maintainability")
        
        # Check for clear method organization
        if self._has_clear_method_organization(class_node):
            maintainability_factors.append("Methods are well-organized and logically grouped")
        
        # Check for type hints
        type_hint_coverage = self._calculate_type_hint_coverage(class_node)
        if type_hint_coverage > 0.9:
            maintainability_factors.append("Comprehensive type hints improve code clarity")
        
        # Check for error handling
        if self._has_comprehensive_error_handling(class_node):
            maintainability_factors.append("Good error handling practices observed")
        
        return {
            'factors': maintainability_factors,
            'documentation_ratio': doc_ratio,
            'type_hint_coverage': type_hint_coverage,
            'maintainability_score': len(maintainability_factors) * 2
        }
    
    def _synthesize_contextual_judgment(self, line_count: int, architectural: Dict, consolidation: Dict, 
                                      responsibility: Dict, complexity: Dict, maintainability: Dict) -> ContextualAnalysis:
        """
        Core HRM hierarchical reasoning: synthesize all analyses into final judgment
        """
        
        reasoning_steps = []
        evidence = {
            'architectural': architectural,
            'consolidation': consolidation,
            'responsibility': responsibility,
            'complexity': complexity,
            'maintainability': maintainability
        }
        
        # Step 1: Assess base size concern
        reasoning_steps.append(f"1. Base assessment: {line_count} lines exceeds typical 200-line threshold")
        
        # Step 2: Architectural justification
        arch_score = architectural['architecture_score']
        reasoning_steps.append(f"2. Architectural analysis: Found {len(architectural['patterns'])} architectural patterns")
        
        for justification in architectural['justifications']:
            reasoning_steps.append(f"   → {justification}")
        
        # Step 3: Consolidation justification
        consol_score = consolidation['consolidation_score']
        if consolidation['reduction_metrics']:
            metrics = consolidation['reduction_metrics']
            reasoning_steps.append(f"3. Consolidation analysis: {metrics['reduction_percentage']}% code reduction achieved")
            reasoning_steps.append(f"   → Reduced {metrics['before_lines']} lines to {metrics['after_lines']} lines")
        else:
            reasoning_steps.append("3. Consolidation analysis: No explicit consolidation metrics found")
        
        # Step 4: Responsibility coherence
        coherence_score = responsibility['coherence_score']
        reasoning_steps.append(f"4. Responsibility analysis: {len(responsibility['coherence_indicators'])} coherence indicators")
        
        # Step 5: Complexity assessment
        avg_complexity = complexity['average_method_complexity']
        reasoning_steps.append(f"5. Complexity analysis: Average method complexity {avg_complexity:.1f}")
        
        if complexity['complex_methods']:
            reasoning_steps.append(f"   ⚠️ Complex methods: {', '.join(complexity['complex_methods'])}")
        
        # Step 6: Maintainability factors
        maint_score = maintainability['maintainability_score']
        reasoning_steps.append(f"6. Maintainability analysis: {len(maintainability['factors'])} positive factors")
        
        # Step 7: Hierarchical synthesis
        total_justification_score = arch_score + consol_score + coherence_score + maint_score
        
        reasoning_steps.append(f"7. Synthesis: Total justification score = {total_justification_score}")
        
        # Decision logic
        if total_justification_score >= 15 and avg_complexity < 8:
            justification = ClassSizeJustification.ACCEPTABLE
            recommendation = f"Large class size is JUSTIFIED by architectural patterns and consolidation benefits"
            confidence = min(0.9, 0.6 + (total_justification_score / 30))
        elif total_justification_score >= 8 and avg_complexity < 12:
            justification = ClassSizeJustification.CONCERNING
            recommendation = f"Class size has some justification but monitor complexity growth"
            confidence = 0.7
        else:
            justification = ClassSizeJustification.UNACCEPTABLE
            recommendation = f"Class size appears unjustified - consider refactoring into smaller components"
            confidence = 0.8
        
        reasoning_steps.append(f"8. Decision: {justification.value.upper()} (confidence: {confidence:.1%})")
        
        return ContextualAnalysis(
            finding=f"Large class analysis for {line_count}-line class",
            justification=justification,
            reasoning_steps=reasoning_steps,
            evidence=evidence,
            confidence=confidence,
            recommendation=recommendation
        )
    
    # Helper methods
    
    def _find_class_node(self, tree: ast.AST, class_name: str) -> Optional[ast.ClassDef]:
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == class_name:
                return node
        return None
    
    def _extract_consolidation_comments(self, code: str) -> List[str]:
        """Extract comments that mention consolidation"""
        consolidation_keywords = ['consolidat', 'combin', 'unif', 'merge', 'reduction']
        comments = []
        
        for line in code.split('\n'):
            if any(keyword in line.lower() for keyword in consolidation_keywords):
                if '#' in line or '"""' in line or "'''" in line:
                    comments.append(line.strip())
        
        return comments
    
    def _analyze_path_context(self, file_path: str) -> Dict[str, str]:
        """Analyze file path for architectural context"""
        path = Path(file_path)
        
        context = {
            'domain': 'unknown',
            'layer': 'unknown',
            'type': 'unknown'
        }
        
        parts = path.parts
        if 'domains' in parts:
            domain_index = parts.index('domains')
            if domain_index + 1 < len(parts):
                context['domain'] = parts[domain_index + 1]
        
        if 'services' in path.name:
            context['layer'] = 'service'
            context['type'] = 'domain_service'
        elif 'entities' in path.name:
            context['layer'] = 'domain'
            context['type'] = 'entity'
        
        return context
    
    def _count_repository_dependencies(self, class_node: ast.ClassDef) -> int:
        """Count repository dependencies in constructor"""
        repo_count = 0
        
        for node in ast.walk(class_node):
            if isinstance(node, ast.FunctionDef) and node.name == '__init__':
                for arg in node.args.args:
                    if 'repo' in arg.arg.lower() or arg.arg.endswith('Repository'):
                        repo_count += 1
        
        return repo_count
    
    def _group_methods_by_purpose(self, class_node: ast.ClassDef) -> Dict[str, List[str]]:
        """Group methods by their apparent purpose"""
        groups = {
            'lifecycle': [],
            'business_logic': [],
            'queries': [],
            'calculations': [],
            'validation': [],
            'integration': [],
            'other': []
        }
        
        for node in class_node.body:
            if isinstance(node, ast.FunctionDef):
                method_name = node.name.lower()
                
                if method_name in ['__init__', 'create', 'build']:
                    groups['lifecycle'].append(node.name)
                elif any(word in method_name for word in ['get', 'find', 'search', 'list']):
                    groups['queries'].append(node.name)
                elif any(word in method_name for word in ['calculate', 'compute', 'determine']):
                    groups['calculations'].append(node.name)
                elif any(word in method_name for word in ['validate', 'check', 'verify']):
                    groups['validation'].append(node.name)
                elif any(word in method_name for word in ['execute', 'process', 'handle', 'perform']):
                    groups['business_logic'].append(node.name)
                else:
                    groups['other'].append(node.name)
        
        return {k: v for k, v in groups.items() if v}  # Remove empty groups
    
    def _analyze_naming_patterns(self, method_names: List[str]) -> Dict[str, Any]:
        """Analyze method naming patterns for consistency"""
        patterns = {
            'async_methods': sum(1 for name in method_names if name.startswith('async_')),
            'get_methods': sum(1 for name in method_names if name.startswith('get_')),
            'calculate_methods': sum(1 for name in method_names if name.startswith('calculate_')),
            'validate_methods': sum(1 for name in method_names if name.startswith('validate_')),
        }
        
        consistent_patterns = sum(1 for count in patterns.values() if count > 1)
        
        return {
            'patterns': patterns,
            'consistent_patterns': consistent_patterns > 0
        }
    
    def _check_domain_coherence(self, code: str) -> List[str]:
        """Check for domain-specific coherence indicators"""
        coherence = []
        
        # Trading domain coherence
        trading_terms = ['trade', 'order', 'position', 'portfolio', 'asset']
        if sum(1 for term in trading_terms if term in code.lower()) >= 3:
            coherence.append("Strong trading domain coherence")
        
        # Gamification domain coherence
        gaming_terms = ['xp', 'level', 'achievement', 'reward', 'leaderboard']
        if sum(1 for term in gaming_terms if term in code.lower()) >= 3:
            coherence.append("Strong gamification domain coherence")
        
        return coherence
    
    def _calculate_method_complexity(self, method_node: ast.FunctionDef) -> int:
        """Calculate cyclomatic complexity of a method"""
        complexity = 1  # Base complexity
        
        for node in ast.walk(method_node):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.ExceptHandler, ast.With)):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1
        
        return complexity
    
    def _assess_complexity_level(self, avg_complexity: float) -> str:
        """Assess complexity level"""
        if avg_complexity < 5:
            return "Low"
        elif avg_complexity < 10:
            return "Moderate"
        else:
            return "High"
    
    def _has_clear_method_organization(self, class_node: ast.ClassDef) -> bool:
        """Check if methods are well-organized"""
        # Simple heuristic: check if related methods are grouped together
        method_names = [node.name for node in class_node.body if isinstance(node, ast.FunctionDef)]
        
        # Check for grouping patterns
        patterns = ['get_', 'set_', 'calculate_', 'validate_', 'create_', 'update_', 'delete_']
        
        for pattern in patterns:
            pattern_methods = [name for name in method_names if name.startswith(pattern)]
            if len(pattern_methods) >= 2:
                return True
        
        return False
    
    def _calculate_type_hint_coverage(self, class_node: ast.ClassDef) -> float:
        """Calculate type hint coverage for class methods"""
        total_methods = 0
        typed_methods = 0
        
        for node in class_node.body:
            if isinstance(node, ast.FunctionDef):
                total_methods += 1
                if node.returns or any(arg.annotation for arg in node.args.args):
                    typed_methods += 1
        
        return typed_methods / total_methods if total_methods > 0 else 0
    
    def _has_comprehensive_error_handling(self, class_node: ast.ClassDef) -> bool:
        """Check for comprehensive error handling"""
        try_blocks = sum(1 for node in ast.walk(class_node) if isinstance(node, ast.Try))
        raise_statements = sum(1 for node in ast.walk(class_node) if isinstance(node, ast.Raise))
        
        return try_blocks >= 2 or raise_statements >= 3
    
    def _create_analysis(self, finding: str, justification: ClassSizeJustification, confidence: float) -> ContextualAnalysis:
        """Create a basic analysis result"""
        return ContextualAnalysis(
            finding=finding,
            justification=justification,
            reasoning_steps=[finding],
            evidence={},
            confidence=confidence,
            recommendation="Analysis incomplete"
        )
    
    def _print_reasoning_process(self, analysis: ContextualAnalysis) -> None:
        """Print the hierarchical reasoning process"""
        
        print(f"\n🎯 **HRM Contextual Judgment**: {analysis.justification.value.upper()}")
        print(f"🎯 **Confidence**: {analysis.confidence:.1%}")
        print(f"\n🧠 **Hierarchical Reasoning Process**:")
        
        for step in analysis.reasoning_steps:
            print(f"   {step}")
        
        print(f"\n💡 **Final Recommendation**:")
        print(f"   {analysis.recommendation}")
        
        # Print evidence summary
        print(f"\n📊 **Evidence Summary**:")
        arch = analysis.evidence.get('architectural', {})
        if arch.get('patterns'):
            print(f"   • **Architectural Patterns**: {', '.join(arch['patterns'])}")
        
        consol = analysis.evidence.get('consolidation', {})
        if consol.get('reduction_metrics'):
            metrics = consol['reduction_metrics']
            print(f"   • **Code Reduction**: {metrics['reduction_percentage']}% ({metrics['before_lines']} → {metrics['after_lines']} lines)")
        
        resp = analysis.evidence.get('responsibility', {})
        if resp.get('method_groups'):
            print(f"   • **Method Organization**: {len(resp['method_groups'])} functional groups")
        
        complex_analysis = analysis.evidence.get('complexity', {})
        if complex_analysis:
            print(f"   • **Average Method Complexity**: {complex_analysis['average_method_complexity']:.1f}")

def main():
    import sys
    
    if len(sys.argv) != 4:
        print("Usage: python contextual_analyzer.py <file_path> <class_name> <line_count>")
        print("Example: python contextual_analyzer.py services.py GamificationDomainService 461")
        sys.exit(1)
    
    file_path = sys.argv[1]
    class_name = sys.argv[2]
    line_count = int(sys.argv[3])
    
    analyzer = ContextualHRMAnalyzer()
    analysis = analyzer.analyze_large_class_context(file_path, class_name, line_count)
    
    print(f"\n🎉 **Contextual Analysis Complete!**")
    print(f"   **Class**: {class_name} ({line_count} lines)")
    print(f"   **Verdict**: {analysis.justification.value.upper()}")
    print(f"   **Confidence**: {analysis.confidence:.1%}")

if __name__ == "__main__":
    main()