#!/usr/bin/env python3
"""
Standalone HRM Analysis Tool for AstraTrade Files
Analyzes specific files using HRM reasoning patterns.
"""

import os
import sys
import ast
import json
from pathlib import Path
from decimal import Decimal
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

@dataclass
class AnalysisResult:
    file_path: str
    complexity_score: float
    patterns_detected: List[str]
    issues_found: List[Dict[str, str]]
    improvement_suggestions: List[str]
    confidence: float
    detailed_analysis: Dict[str, Any]

class HRMCodeAnalyzer:
    """HRM-powered code analyzer for AstraTrade patterns"""
    
    def __init__(self):
        self.astratrade_patterns = self._load_patterns()
    
    def _load_patterns(self) -> Dict[str, Any]:
        """Load AstraTrade-specific patterns"""
        return {
            'value_object_patterns': [
                'immutable_dataclass',
                'validation_methods',
                'equality_implementation',
                'conversion_methods',
                'business_rules'
            ],
            'domain_patterns': [
                'domain_driven_design',
                'value_object',
                'entity',
                'aggregate_root',
                'domain_service'
            ],
            'quality_indicators': [
                'type_hints',
                'docstrings',
                'error_handling',
                'validation',
                'immutability'
            ]
        }
    
    def analyze_file(self, file_path: str) -> AnalysisResult:
        """Analyze a specific file using HRM reasoning"""
        print(f"🧠 HRM Analysis: {file_path}")
        print("=" * 60)
        
        if not Path(file_path).exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        with open(file_path, 'r') as f:
            code = f.read()
        
        # Parse AST for structural analysis
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            return AnalysisResult(
                file_path=file_path,
                complexity_score=0.0,
                patterns_detected=[],
                issues_found=[{"type": "syntax_error", "message": str(e)}],
                improvement_suggestions=["Fix syntax errors"],
                confidence=0.0,
                detailed_analysis={"error": str(e)}
            )
        
        # Multi-level HRM analysis
        structural_analysis = self._analyze_structure(tree, code)
        pattern_analysis = self._analyze_patterns(tree, code)
        quality_analysis = self._analyze_quality(tree, code)
        domain_analysis = self._analyze_domain_concepts(tree, code, file_path)
        
        # Hierarchical reasoning synthesis
        complexity_score = self._calculate_complexity(structural_analysis, pattern_analysis)
        patterns_detected = self._identify_patterns(pattern_analysis, domain_analysis)
        issues_found = self._identify_issues(quality_analysis, structural_analysis)
        suggestions = self._generate_suggestions(issues_found, pattern_analysis, domain_analysis)
        confidence = self._calculate_confidence(structural_analysis, pattern_analysis, quality_analysis)
        
        # Generate detailed analysis
        detailed_analysis = {
            "file_metrics": structural_analysis,
            "pattern_recognition": pattern_analysis,
            "quality_assessment": quality_analysis,
            "domain_modeling": domain_analysis,
            "hrm_reasoning": self._generate_reasoning_steps(patterns_detected, issues_found)
        }
        
        result = AnalysisResult(
            file_path=file_path,
            complexity_score=complexity_score,
            patterns_detected=patterns_detected,
            issues_found=issues_found,
            improvement_suggestions=suggestions,
            confidence=confidence,
            detailed_analysis=detailed_analysis
        )
        
        self._print_analysis_results(result)
        return result
    
    def _analyze_structure(self, tree: ast.AST, code: str) -> Dict[str, Any]:
        """Analyze structural properties of the code"""
        lines = code.split('\n')
        non_empty_lines = [line for line in lines if line.strip()]
        
        classes = []
        functions = []
        imports = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                classes.append({
                    'name': node.name,
                    'methods': [n.name for n in node.body if isinstance(n, ast.FunctionDef)],
                    'decorators': [d.id if isinstance(d, ast.Name) else str(d) for d in node.decorator_list],
                    'docstring': ast.get_docstring(node),
                    'line_count': self._get_node_line_count(node, lines)
                })
            elif isinstance(node, ast.FunctionDef):
                if not any(node.name in cls['methods'] for cls in classes):
                    functions.append({
                        'name': node.name,
                        'args': [arg.arg for arg in node.args.args],
                        'decorators': [d.id if isinstance(d, ast.Name) else str(d) for d in node.decorator_list],
                        'docstring': ast.get_docstring(node),
                        'line_count': self._get_node_line_count(node, lines)
                    })
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                imports.append(ast.unparse(node))
        
        return {
            'total_lines': len(lines),
            'non_empty_lines': len(non_empty_lines),
            'classes': classes,
            'functions': functions,
            'imports': imports,
            'has_main_block': '__name__ == "__main__"' in code
        }
    
    def _analyze_patterns(self, tree: ast.AST, code: str) -> Dict[str, Any]:
        """Analyze design patterns and architectural patterns"""
        patterns = {
            'value_object': self._detect_value_object_pattern(tree, code),
            'dataclass': '@dataclass' in code,
            'immutable': self._detect_immutability_pattern(tree, code),
            'validation': self._detect_validation_pattern(tree, code),
            'factory': self._detect_factory_pattern(tree, code),
            'builder': self._detect_builder_pattern(tree, code),
            'domain_model': self._detect_domain_model_pattern(tree, code)
        }
        
        return patterns
    
    def _analyze_quality(self, tree: ast.AST, code: str) -> Dict[str, Any]:
        """Analyze code quality indicators"""
        quality_metrics = {
            'type_hints': self._check_type_hints(tree),
            'docstrings': self._check_docstrings(tree),
            'error_handling': self._check_error_handling(tree),
            'naming_conventions': self._check_naming_conventions(tree),
            'code_organization': self._check_code_organization(tree),
            'test_coverage': self._estimate_test_coverage(code)
        }
        
        return quality_metrics
    
    def _analyze_domain_concepts(self, tree: ast.AST, code: str, file_path: str) -> Dict[str, Any]:
        """Analyze domain-specific concepts for AstraTrade"""
        domain_concepts = {
            'trading_concepts': self._detect_trading_concepts(code),
            'financial_concepts': self._detect_financial_concepts(code),
            'gamification_concepts': self._detect_gamification_concepts(code),
            'blockchain_concepts': self._detect_blockchain_concepts(code),
            'domain_boundaries': self._analyze_domain_boundaries(file_path),
            'business_rules': self._extract_business_rules(tree, code)
        }
        
        return domain_concepts
    
    def _detect_value_object_pattern(self, tree: ast.AST, code: str) -> bool:
        """Detect value object pattern implementation"""
        has_dataclass = '@dataclass' in code
        has_frozen = 'frozen=True' in code
        has_eq_methods = any(
            isinstance(node, ast.FunctionDef) and node.name in ['__eq__', '__hash__']
            for node in ast.walk(tree)
        )
        
        return has_dataclass or has_eq_methods
    
    def _detect_immutability_pattern(self, tree: ast.AST, code: str) -> bool:
        """Detect immutability patterns"""
        return ('frozen=True' in code or 
                'Final' in code or
                any(isinstance(node, ast.AnnAssign) and 
                    getattr(node.annotation, 'id', None) == 'Final'
                    for node in ast.walk(tree)))
    
    def _detect_validation_pattern(self, tree: ast.AST, code: str) -> bool:
        """Detect validation patterns"""
        validation_keywords = ['validate', 'check', 'verify', 'assert', 'raise ValueError']
        return any(keyword in code for keyword in validation_keywords)
    
    def _detect_factory_pattern(self, tree: ast.AST, code: str) -> bool:
        """Detect factory pattern"""
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if (node.name.startswith('create_') or 
                    node.name.startswith('from_') or
                    node.name in ['factory', 'build']):
                    return True
        return False
    
    def _detect_builder_pattern(self, tree: ast.AST, code: str) -> bool:
        """Detect builder pattern"""
        return 'Builder' in code or any(
            isinstance(node, ast.ClassDef) and 'builder' in node.name.lower()
            for node in ast.walk(tree)
        )
    
    def _detect_domain_model_pattern(self, tree: ast.AST, code: str) -> bool:
        """Detect domain modeling patterns"""
        domain_indicators = ['Entity', 'ValueObject', 'AggregateRoot', 'DomainService']
        return any(indicator in code for indicator in domain_indicators)
    
    def _check_type_hints(self, tree: ast.AST) -> Dict[str, Any]:
        """Check type hint usage"""
        total_functions = 0
        typed_functions = 0
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                total_functions += 1
                if (node.returns or 
                    any(arg.annotation for arg in node.args.args)):
                    typed_functions += 1
        
        coverage = (typed_functions / total_functions * 100) if total_functions > 0 else 0
        
        return {
            'coverage_percentage': coverage,
            'total_functions': total_functions,
            'typed_functions': typed_functions
        }
    
    def _check_docstrings(self, tree: ast.AST) -> Dict[str, Any]:
        """Check docstring coverage"""
        total_items = 0
        documented_items = 0
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.ClassDef, ast.FunctionDef)):
                total_items += 1
                if ast.get_docstring(node):
                    documented_items += 1
        
        coverage = (documented_items / total_items * 100) if total_items > 0 else 0
        
        return {
            'coverage_percentage': coverage,
            'total_items': total_items,
            'documented_items': documented_items
        }
    
    def _check_error_handling(self, tree: ast.AST) -> Dict[str, Any]:
        """Check error handling patterns"""
        try_blocks = sum(1 for node in ast.walk(tree) if isinstance(node, ast.Try))
        raise_statements = sum(1 for node in ast.walk(tree) if isinstance(node, ast.Raise))
        
        return {
            'try_blocks': try_blocks,
            'raise_statements': raise_statements,
            'has_error_handling': try_blocks > 0 or raise_statements > 0
        }
    
    def _check_naming_conventions(self, tree: ast.AST) -> Dict[str, Any]:
        """Check naming convention adherence"""
        issues = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                if not node.name[0].isupper():
                    issues.append(f"Class {node.name} should start with uppercase")
            elif isinstance(node, ast.FunctionDef):
                if not node.name.islower() and '_' not in node.name:
                    if not node.name.startswith('__'):  # Allow dunder methods
                        issues.append(f"Function {node.name} should be snake_case")
        
        return {
            'issues': issues,
            'follows_conventions': len(issues) == 0
        }
    
    def _check_code_organization(self, tree: ast.AST) -> Dict[str, Any]:
        """Check code organization"""
        imports_at_top = True
        class_count = sum(1 for node in ast.walk(tree) if isinstance(node, ast.ClassDef))
        
        # Check if imports are at the top
        first_non_import = None
        for node in ast.walk(tree):
            if not isinstance(node, (ast.Import, ast.ImportFrom, ast.Expr)):
                first_non_import = node
                break
        
        return {
            'imports_at_top': imports_at_top,
            'class_count': class_count,
            'well_organized': imports_at_top and class_count <= 5
        }
    
    def _estimate_test_coverage(self, code: str) -> Dict[str, Any]:
        """Estimate test coverage based on code patterns"""
        has_test_methods = 'def test_' in code
        has_assertions = any(keyword in code for keyword in ['assert', 'assertEqual', 'assertTrue'])
        
        return {
            'has_tests': has_test_methods,
            'has_assertions': has_assertions,
            'estimated_coverage': 'high' if has_test_methods and has_assertions else 'low'
        }
    
    def _detect_trading_concepts(self, code: str) -> List[str]:
        """Detect trading-specific concepts"""
        trading_terms = [
            'trade', 'order', 'position', 'portfolio', 'asset', 'price', 'pnl',
            'buy', 'sell', 'long', 'short', 'market', 'limit', 'stop'
        ]
        return [term for term in trading_terms if term.lower() in code.lower()]
    
    def _detect_financial_concepts(self, code: str) -> List[str]:
        """Detect financial concepts"""
        financial_terms = [
            'money', 'currency', 'amount', 'balance', 'payment', 'transaction',
            'decimal', 'usd', 'eur', 'btc', 'eth'
        ]
        return [term for term in financial_terms if term.lower() in code.lower()]
    
    def _detect_gamification_concepts(self, code: str) -> List[str]:
        """Detect gamification concepts"""
        gaming_terms = [
            'xp', 'level', 'achievement', 'badge', 'reward', 'score', 'points',
            'leaderboard', 'clan', 'battle'
        ]
        return [term for term in gaming_terms if term.lower() in code.lower()]
    
    def _detect_blockchain_concepts(self, code: str) -> List[str]:
        """Detect blockchain concepts"""
        blockchain_terms = [
            'starknet', 'cairo', 'contract', 'wallet', 'address', 'hash',
            'signature', 'transaction', 'block', 'nft'
        ]
        return [term for term in blockchain_terms if term.lower() in code.lower()]
    
    def _analyze_domain_boundaries(self, file_path: str) -> Dict[str, str]:
        """Analyze domain boundaries from file path"""
        path_parts = Path(file_path).parts
        domain = 'unknown'
        subdomain = 'unknown'
        
        if 'domains' in path_parts:
            domain_index = path_parts.index('domains')
            if domain_index + 1 < len(path_parts):
                domain = path_parts[domain_index + 1]
            if domain_index + 2 < len(path_parts):
                subdomain = path_parts[domain_index + 2]
        
        return {
            'domain': domain,
            'subdomain': subdomain,
            'bounded_context': f"{domain}_{subdomain}" if subdomain != 'unknown' else domain
        }
    
    def _extract_business_rules(self, tree: ast.AST, code: str) -> List[str]:
        """Extract business rules from code"""
        rules = []
        
        # Look for validation rules
        for node in ast.walk(tree):
            if isinstance(node, ast.If):
                # Extract condition as potential business rule
                try:
                    condition = ast.unparse(node.test)
                    if any(keyword in condition.lower() for keyword in ['validate', 'check', 'must', 'cannot']):
                        rules.append(f"Business rule: {condition}")
                except:
                    pass
        
        return rules
    
    def _calculate_complexity(self, structural: Dict[str, Any], patterns: Dict[str, Any]) -> float:
        """Calculate complexity score using HRM hierarchical reasoning"""
        # Base complexity from structure
        base_complexity = structural['non_empty_lines'] / 10.0
        
        # Pattern complexity adjustments
        pattern_complexity = 0
        if patterns['value_object']:
            pattern_complexity += 5  # Value objects add conceptual complexity
        if patterns['domain_model']:
            pattern_complexity += 10  # Domain models are more complex
        
        # Class complexity
        class_complexity = sum(len(cls['methods']) for cls in structural['classes']) * 2
        
        total_complexity = base_complexity + pattern_complexity + class_complexity
        return min(total_complexity, 100.0)  # Cap at 100
    
    def _identify_patterns(self, pattern_analysis: Dict[str, Any], domain_analysis: Dict[str, Any]) -> List[str]:
        """Identify detected patterns using HRM reasoning"""
        patterns = []
        
        # Structural patterns
        if pattern_analysis['value_object']:
            patterns.append('Value Object Pattern')
        if pattern_analysis['dataclass']:
            patterns.append('Dataclass Pattern')
        if pattern_analysis['immutable']:
            patterns.append('Immutable Object Pattern')
        if pattern_analysis['validation']:
            patterns.append('Validation Pattern')
        if pattern_analysis['factory']:
            patterns.append('Factory Pattern')
        if pattern_analysis['domain_model']:
            patterns.append('Domain Model Pattern')
        
        # Domain-specific patterns
        if domain_analysis['trading_concepts']:
            patterns.append('Trading Domain Pattern')
        if domain_analysis['financial_concepts']:
            patterns.append('Financial Modeling Pattern')
        if domain_analysis['gamification_concepts']:
            patterns.append('Gamification Pattern')
        if domain_analysis['blockchain_concepts']:
            patterns.append('Blockchain Integration Pattern')
        
        return patterns
    
    def _identify_issues(self, quality: Dict[str, Any], structural: Dict[str, Any]) -> List[Dict[str, str]]:
        """Identify potential issues using HRM analysis"""
        issues = []
        
        # Type hint coverage
        if quality['type_hints']['coverage_percentage'] < 80:
            issues.append({
                'type': 'type_hints',
                'message': f"Low type hint coverage ({quality['type_hints']['coverage_percentage']:.1f}%)"
            })
        
        # Documentation coverage
        if quality['docstrings']['coverage_percentage'] < 60:
            issues.append({
                'type': 'documentation',
                'message': f"Low docstring coverage ({quality['docstrings']['coverage_percentage']:.1f}%)"
            })
        
        # Error handling
        if not quality['error_handling']['has_error_handling']:
            issues.append({
                'type': 'error_handling',
                'message': "No error handling detected"
            })
        
        # Naming conventions
        if not quality['naming_conventions']['follows_conventions']:
            issues.append({
                'type': 'naming',
                'message': "Naming convention violations detected"
            })
        
        # Large classes
        for cls in structural['classes']:
            if cls['line_count'] > 200:
                issues.append({
                    'type': 'complexity',
                    'message': f"Class {cls['name']} is large ({cls['line_count']} lines)"
                })
        
        return issues
    
    def _generate_suggestions(self, issues: List[Dict[str, str]], patterns: Dict[str, Any], domain: Dict[str, Any]) -> List[str]:
        """Generate improvement suggestions using HRM reasoning"""
        suggestions = []
        
        # Address specific issues
        for issue in issues:
            if issue['type'] == 'type_hints':
                suggestions.append("Add comprehensive type hints to improve code clarity and IDE support")
            elif issue['type'] == 'documentation':
                suggestions.append("Add docstrings to classes and methods for better maintainability")
            elif issue['type'] == 'error_handling':
                suggestions.append("Implement proper error handling with specific exception types")
            elif issue['type'] == 'naming':
                suggestions.append("Follow Python naming conventions (PEP 8)")
            elif issue['type'] == 'complexity':
                suggestions.append("Consider breaking down large classes into smaller, focused components")
        
        # Pattern-specific suggestions
        if patterns['value_object'] and not patterns['immutable']:
            suggestions.append("Consider making value objects immutable with @dataclass(frozen=True)")
        
        if domain['trading_concepts'] and not patterns['validation']:
            suggestions.append("Add validation methods for trading-specific business rules")
        
        if domain['financial_concepts']:
            suggestions.append("Ensure proper decimal precision for financial calculations")
        
        return suggestions
    
    def _calculate_confidence(self, structural: Dict[str, Any], patterns: Dict[str, Any], quality: Dict[str, Any]) -> float:
        """Calculate analysis confidence using HRM meta-reasoning"""
        factors = []
        
        # Structural confidence
        if structural['non_empty_lines'] > 20:
            factors.append(0.8)
        else:
            factors.append(0.4)
        
        # Pattern detection confidence
        pattern_count = sum(1 for p in patterns.values() if p)
        if pattern_count > 3:
            factors.append(0.9)
        elif pattern_count > 1:
            factors.append(0.7)
        else:
            factors.append(0.5)
        
        # Quality analysis confidence
        if quality['type_hints']['coverage_percentage'] > 50:
            factors.append(0.8)
        else:
            factors.append(0.6)
        
        return sum(factors) / len(factors)
    
    def _generate_reasoning_steps(self, patterns: List[str], issues: List[Dict[str, str]]) -> List[str]:
        """Generate HRM reasoning steps"""
        steps = [
            "1. Analyze code structure and identify key components",
            "2. Detect design patterns and architectural patterns",
            "3. Evaluate code quality metrics and best practices",
            "4. Identify domain-specific concepts and business rules",
            "5. Synthesize findings using hierarchical reasoning",
            f"6. Found {len(patterns)} patterns and {len(issues)} potential issues",
            "7. Generate actionable improvement recommendations"
        ]
        return steps
    
    def _get_node_line_count(self, node: ast.AST, lines: List[str]) -> int:
        """Get line count for an AST node"""
        if hasattr(node, 'end_lineno') and node.end_lineno:
            return node.end_lineno - node.lineno + 1
        return 10  # Estimate
    
    def _print_analysis_results(self, result: AnalysisResult) -> None:
        """Print comprehensive analysis results"""
        print(f"\n📊 **Analysis Results**:")
        print(f"   - **Complexity Score**: {result.complexity_score:.1f}/100")
        print(f"   - **Patterns Detected**: {len(result.patterns_detected)}")
        print(f"   - **Issues Found**: {len(result.issues_found)}")
        print(f"   - **Confidence**: {result.confidence:.1%}")
        
        print(f"\n🔍 **Patterns Detected**:")
        for pattern in result.patterns_detected:
            print(f"   ✅ {pattern}")
        
        if result.issues_found:
            print(f"\n⚠️  **Issues Identified**:")
            for issue in result.issues_found:
                print(f"   • {issue['type'].upper()}: {issue['message']}")
        
        print(f"\n💡 **HRM Improvement Suggestions**:")
        for suggestion in result.improvement_suggestions:
            print(f"   • {suggestion}")
        
        # Domain analysis
        domain_info = result.detailed_analysis.get('domain_modeling', {})
        if domain_info.get('domain') != 'unknown':
            print(f"\n🎯 **Domain Analysis**:")
            print(f"   - **Domain**: {domain_info.get('domain', 'unknown')}")
            print(f"   - **Bounded Context**: {domain_info.get('bounded_context', 'unknown')}")
            
            trading_concepts = domain_info.get('trading_concepts', [])
            if trading_concepts:
                print(f"   - **Trading Concepts**: {', '.join(trading_concepts)}")
            
            financial_concepts = domain_info.get('financial_concepts', [])
            if financial_concepts:
                print(f"   - **Financial Concepts**: {', '.join(financial_concepts)}")
        
        # Quality metrics
        quality_info = result.detailed_analysis.get('quality_assessment', {})
        print(f"\n📈 **Quality Metrics**:")
        print(f"   - **Type Hints**: {quality_info.get('type_hints', {}).get('coverage_percentage', 0):.1f}% coverage")
        print(f"   - **Documentation**: {quality_info.get('docstrings', {}).get('coverage_percentage', 0):.1f}% coverage")
        print(f"   - **Error Handling**: {'✅' if quality_info.get('error_handling', {}).get('has_error_handling', False) else '❌'}")
        
        # HRM reasoning process
        reasoning_steps = result.detailed_analysis.get('hrm_reasoning', [])
        print(f"\n🧠 **HRM Reasoning Process**:")
        for step in reasoning_steps:
            print(f"   {step}")

def main():
    if len(sys.argv) != 2:
        print("Usage: python analyze_file.py <file_path>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    analyzer = HRMCodeAnalyzer()
    
    try:
        result = analyzer.analyze_file(file_path)
        print(f"\n🎉 **Analysis Complete!**")
        print(f"   File: {result.file_path}")
        print(f"   Overall Quality: {'Excellent' if result.confidence > 0.8 else 'Good' if result.confidence > 0.6 else 'Needs Improvement'}")
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()