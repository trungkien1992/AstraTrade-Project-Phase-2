"""
Code Analyzer using Hierarchical Reasoning Model

Provides deep code analysis capabilities for AstraTrade development,
including pattern recognition, complexity analysis, and improvement suggestions.
"""

import torch
import ast
import os
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
import logging

from ..hrm.model import HierarchicalReasoningModel, HRMConfig
from ..hrm.training import HRMTrainer, TrainingConfig

logger = logging.getLogger(__name__)


@dataclass
class CodeAnalysisResult:
    """Results from HRM-powered code analysis"""
    file_path: str
    complexity_score: float
    patterns_detected: List[str]
    issues_found: List[Dict[str, Any]]
    improvement_suggestions: List[str]
    reasoning_steps: List[str]
    confidence: float


@dataclass
class ASTNode:
    """Simplified AST node representation for HRM processing"""
    node_type: str
    name: str
    children: List['ASTNode']
    metadata: Dict[str, Any]


class CodeTokenizer:
    """Tokenizer for converting Python code to HRM input format"""
    
    def __init__(self):
        # Create vocabulary for code elements
        self.vocab = {
            # Python keywords
            'def': 1, 'class': 2, 'if': 3, 'else': 4, 'elif': 5, 'for': 6, 'while': 7,
            'import': 8, 'from': 9, 'try': 10, 'except': 11, 'finally': 12, 'with': 13,
            'async': 14, 'await': 15, 'return': 16, 'yield': 17, 'break': 18, 'continue': 19,
            
            # Common patterns
            'function_def': 20, 'class_def': 21, 'method_call': 22, 'assignment': 23,
            'conditional': 24, 'loop': 25, 'exception_handling': 26, 'import_stmt': 27,
            
            # AstraTrade specific
            'domain_service': 30, 'repository': 31, 'entity': 32, 'value_object': 33,
            'event': 34, 'api_endpoint': 35, 'trading_logic': 36, 'gamification': 37,
            'financial': 38, 'blockchain': 39,
            
            # Code quality indicators
            'complex_logic': 50, 'nested_structure': 51, 'long_function': 52,
            'duplicate_code': 53, 'poor_naming': 54, 'missing_docstring': 55,
            
            # Special tokens
            '<UNK>': 0, '<PAD>': 100, '<START>': 101, '<END>': 102
        }
        self.reverse_vocab = {v: k for k, v in self.vocab.items()}
    
    def tokenize_file(self, file_path: str) -> List[int]:
        """Convert Python file to token sequence for HRM"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
            
            # Parse AST
            tree = ast.parse(code)
            tokens = []
            
            # Add start token
            tokens.append(self.vocab['<START>'])
            
            # Convert AST to tokens
            tokens.extend(self._ast_to_tokens(tree))
            
            # Add end token
            tokens.append(self.vocab['<END>'])
            
            return tokens
            
        except Exception as e:
            logger.warning(f"Failed to tokenize {file_path}: {e}")
            return [self.vocab['<UNK>']]
    
    def _ast_to_tokens(self, node: ast.AST) -> List[int]:
        """Convert AST node to token sequence"""
        tokens = []
        
        if isinstance(node, ast.FunctionDef):
            tokens.append(self.vocab.get('function_def', self.vocab['<UNK>']))
            # Check for AstraTrade patterns
            if self._is_domain_service_method(node):
                tokens.append(self.vocab.get('domain_service', self.vocab['<UNK>']))
            if self._is_repository_method(node):
                tokens.append(self.vocab.get('repository', self.vocab['<UNK>']))
            if self._is_trading_logic(node):
                tokens.append(self.vocab.get('trading_logic', self.vocab['<UNK>']))
                
        elif isinstance(node, ast.ClassDef):
            tokens.append(self.vocab.get('class_def', self.vocab['<UNK>']))
            if self._is_entity_class(node):
                tokens.append(self.vocab.get('entity', self.vocab['<UNK>']))
            elif self._is_value_object_class(node):
                tokens.append(self.vocab.get('value_object', self.vocab['<UNK>']))
                
        elif isinstance(node, ast.If):
            tokens.append(self.vocab.get('conditional', self.vocab['<UNK>']))
            
        elif isinstance(node, (ast.For, ast.While)):
            tokens.append(self.vocab.get('loop', self.vocab['<UNK>']))
            
        elif isinstance(node, ast.Import):
            tokens.append(self.vocab.get('import_stmt', self.vocab['<UNK>']))
        
        # Recursively process children
        for child in ast.iter_child_nodes(node):
            tokens.extend(self._ast_to_tokens(child))
            
        return tokens
    
    def _is_domain_service_method(self, node: ast.FunctionDef) -> bool:
        """Check if function is a domain service method"""
        return any('service' in arg.arg.lower() for arg in node.args.args if hasattr(arg, 'arg'))
    
    def _is_repository_method(self, node: ast.FunctionDef) -> bool:
        """Check if function is a repository method"""
        return node.name.startswith(('get_', 'save_', 'find_', 'delete_'))
    
    def _is_trading_logic(self, node: ast.FunctionDef) -> bool:
        """Check if function contains trading logic"""
        trading_keywords = ['trade', 'order', 'portfolio', 'position', 'pnl', 'execute']
        return any(keyword in node.name.lower() for keyword in trading_keywords)
    
    def _is_entity_class(self, node: ast.ClassDef) -> bool:
        """Check if class is a domain entity"""
        entity_patterns = ['Entity', 'Aggregate', 'Root']
        return any(pattern in base.id for base in node.bases if hasattr(base, 'id'))
    
    def _is_value_object_class(self, node: ast.ClassDef) -> bool:
        """Check if class is a value object"""
        return '@dataclass' in ast.get_source_segment(open(node.lineno).read(), node) if hasattr(node, 'lineno') else False


class CodeAnalyzer:
    """
    HRM-powered code analyzer for AstraTrade development
    
    Uses hierarchical reasoning to analyze code structure, detect patterns,
    identify issues, and suggest improvements.
    """
    
    def __init__(self, model_path: Optional[str] = None):
        self.tokenizer = CodeTokenizer()
        
        # Initialize HRM model
        self.config = HRMConfig(
            hidden_size=512,
            vocab_size=len(self.tokenizer.vocab),
            N=3,  # 3 high-level reasoning cycles
            T=4,  # 4 low-level steps per cycle
            use_stablemax=True
        )
        
        self.model = HierarchicalReasoningModel(self.config)
        
        if model_path and os.path.exists(model_path):
            self.model.load_state_dict(torch.load(model_path, map_location='cpu'))
            logger.info(f"Loaded pre-trained model from {model_path}")
        else:
            logger.info("Using untrained model - consider training on AstraTrade codebase")
    
    def analyze_file(self, file_path: str) -> CodeAnalysisResult:
        """
        Perform hierarchical reasoning analysis on a single file
        """
        logger.info(f"Analyzing file: {file_path}")
        
        # Tokenize the file
        tokens = self.tokenizer.tokenize_file(file_path)
        input_ids = torch.tensor([tokens], dtype=torch.long)
        
        # Run HRM analysis
        self.model.eval()
        with torch.no_grad():
            # Use HRM with intermediate reasoning steps
            output = self.model(input_ids, return_intermediate=True)
            
            # Extract reasoning information
            logits = output['logits']
            z_h = output['z_h']  # High-level reasoning state
            z_l = output['z_l']  # Low-level reasoning state
            intermediate_states = output.get('intermediate_states', [])
        
        # Analyze the reasoning process
        reasoning_analysis = self._analyze_reasoning_states(z_h, z_l, intermediate_states)
        
        # Generate analysis results
        result = self._generate_analysis_result(
            file_path=file_path,
            tokens=tokens,
            reasoning_analysis=reasoning_analysis,
            logits=logits
        )
        
        return result
    
    def analyze_directory(self, directory_path: str, pattern: str = "*.py") -> List[CodeAnalysisResult]:
        """
        Analyze all Python files in a directory
        """
        directory = Path(directory_path)
        results = []
        
        for file_path in directory.rglob(pattern):
            if file_path.is_file():
                try:
                    result = self.analyze_file(str(file_path))
                    results.append(result)
                except Exception as e:
                    logger.error(f"Failed to analyze {file_path}: {e}")
        
        return results
    
    def _analyze_reasoning_states(
        self, 
        z_h: torch.Tensor, 
        z_l: torch.Tensor, 
        intermediate_states: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze the HRM reasoning process"""
        
        # Compute participation ratios for hierarchical analysis
        pr_h = self._compute_participation_ratio(z_h)
        pr_l = self._compute_participation_ratio(z_l)
        hierarchy_ratio = pr_h / pr_l if pr_l > 0 else 1.0
        
        # Analyze reasoning steps
        reasoning_steps = []
        for i, state in enumerate(intermediate_states):
            step_type = state.get('type', 'unknown')
            step_desc = f"Step {i+1}: {step_type} reasoning"
            reasoning_steps.append(step_desc)
        
        return {
            'hierarchy_ratio': hierarchy_ratio,
            'reasoning_depth': len(intermediate_states),
            'reasoning_steps': reasoning_steps,
            'high_level_complexity': pr_h,
            'low_level_complexity': pr_l
        }
    
    def _compute_participation_ratio(self, hidden_states: torch.Tensor) -> float:
        """Compute participation ratio for dimensional analysis"""
        if hidden_states.numel() == 0:
            return 0.0
        
        # Flatten and compute variance
        flat_states = hidden_states.flatten()
        variance = torch.var(flat_states).item()
        
        # Approximate participation ratio
        return min(variance * 100, 100.0)  # Scale and cap at 100
    
    def _generate_analysis_result(
        self,
        file_path: str,
        tokens: List[int],
        reasoning_analysis: Dict[str, Any],
        logits: torch.Tensor
    ) -> CodeAnalysisResult:
        """Generate comprehensive analysis result"""
        
        # Calculate complexity score based on hierarchy ratio
        complexity_score = reasoning_analysis['hierarchy_ratio'] * 10
        
        # Detect patterns based on tokens
        patterns_detected = self._detect_patterns(tokens)
        
        # Identify potential issues
        issues_found = self._identify_issues(tokens, reasoning_analysis)
        
        # Generate improvement suggestions
        improvement_suggestions = self._generate_suggestions(patterns_detected, issues_found)
        
        # Calculate confidence based on reasoning depth
        confidence = min(reasoning_analysis['reasoning_depth'] / 10.0, 1.0)
        
        return CodeAnalysisResult(
            file_path=file_path,
            complexity_score=complexity_score,
            patterns_detected=patterns_detected,
            issues_found=issues_found,
            improvement_suggestions=improvement_suggestions,
            reasoning_steps=reasoning_analysis['reasoning_steps'],
            confidence=confidence
        )
    
    def _detect_patterns(self, tokens: List[int]) -> List[str]:
        """Detect code patterns from token sequence"""
        patterns = []
        
        # Check for domain patterns
        if self.tokenizer.vocab.get('domain_service', 0) in tokens:
            patterns.append("Domain Service Pattern")
        if self.tokenizer.vocab.get('repository', 0) in tokens:
            patterns.append("Repository Pattern")
        if self.tokenizer.vocab.get('entity', 0) in tokens:
            patterns.append("Domain Entity")
        if self.tokenizer.vocab.get('trading_logic', 0) in tokens:
            patterns.append("Trading Logic")
        
        # Check for architectural patterns
        function_count = tokens.count(self.tokenizer.vocab.get('function_def', 0))
        class_count = tokens.count(self.tokenizer.vocab.get('class_def', 0))
        
        if function_count > class_count * 3:
            patterns.append("Functional Programming Style")
        elif class_count > 0:
            patterns.append("Object-Oriented Design")
        
        return patterns
    
    def _identify_issues(self, tokens: List[int], reasoning_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify potential code issues"""
        issues = []
        
        # High complexity warning
        if reasoning_analysis['hierarchy_ratio'] > 5.0:
            issues.append({
                'type': 'complexity',
                'severity': 'high',
                'message': 'High complexity detected - consider refactoring',
                'line': None
            })
        
        # Check for missing patterns
        if self.tokenizer.vocab.get('domain_service', 0) not in tokens and len(tokens) > 50:
            issues.append({
                'type': 'architecture',
                'severity': 'medium', 
                'message': 'Large file without clear domain service pattern',
                'line': None
            })
        
        # Low reasoning depth might indicate simple logic
        if reasoning_analysis['reasoning_depth'] < 3 and len(tokens) > 100:
            issues.append({
                'type': 'structure',
                'severity': 'low',
                'message': 'Code may benefit from more structured approach',
                'line': None
            })
        
        return issues
    
    def _generate_suggestions(self, patterns: List[str], issues: List[Dict[str, Any]]) -> List[str]:
        """Generate improvement suggestions based on analysis"""
        suggestions = []
        
        # Pattern-based suggestions
        if "Domain Service Pattern" not in patterns and len(issues) > 0:
            suggestions.append("Consider implementing domain service pattern for better separation of concerns")
        
        if "Repository Pattern" not in patterns and "Trading Logic" in patterns:
            suggestions.append("Add repository pattern for data access abstraction")
        
        # Issue-based suggestions
        for issue in issues:
            if issue['type'] == 'complexity':
                suggestions.append("Break down complex functions into smaller, focused methods")
            elif issue['type'] == 'architecture':
                suggestions.append("Consider restructuring with domain-driven design principles")
            elif issue['type'] == 'structure':
                suggestions.append("Add more intermediate processing steps for clarity")
        
        return suggestions
    
    def generate_report(self, results: List[CodeAnalysisResult]) -> str:
        """Generate a comprehensive analysis report"""
        report = ["# HRM Code Analysis Report", ""]
        
        # Summary statistics
        total_files = len(results)
        avg_complexity = sum(r.complexity_score for r in results) / total_files if total_files > 0 else 0
        high_complexity_files = [r for r in results if r.complexity_score > 50]
        
        report.extend([
            f"## Summary",
            f"- **Files Analyzed**: {total_files}",
            f"- **Average Complexity**: {avg_complexity:.2f}",
            f"- **High Complexity Files**: {len(high_complexity_files)}",
            ""
        ])
        
        # Pattern analysis
        all_patterns = []
        for result in results:
            all_patterns.extend(result.patterns_detected)
        
        pattern_counts = {}
        for pattern in all_patterns:
            pattern_counts[pattern] = pattern_counts.get(pattern, 0) + 1
        
        report.extend([
            "## Pattern Analysis",
            ""
        ])
        
        for pattern, count in sorted(pattern_counts.items(), key=lambda x: x[1], reverse=True):
            report.append(f"- **{pattern}**: {count} files")
        
        report.append("")
        
        # High-priority issues
        high_priority_issues = []
        for result in results:
            for issue in result.issues_found:
                if issue['severity'] == 'high':
                    high_priority_issues.append((result.file_path, issue))
        
        if high_priority_issues:
            report.extend([
                "## High Priority Issues",
                ""
            ])
            
            for file_path, issue in high_priority_issues:
                report.append(f"- **{file_path}**: {issue['message']}")
            
            report.append("")
        
        # Recommendations
        all_suggestions = []
        for result in results:
            all_suggestions.extend(result.improvement_suggestions)
        
        unique_suggestions = list(set(all_suggestions))
        
        if unique_suggestions:
            report.extend([
                "## Recommendations",
                ""
            ])
            
            for suggestion in unique_suggestions:
                report.append(f"- {suggestion}")
        
        return "\n".join(report)


# CLI interface
def main():
    """Command-line interface for the code analyzer"""
    import argparse
    
    parser = argparse.ArgumentParser(description="HRM-powered code analyzer")
    parser.add_argument("path", help="File or directory to analyze")
    parser.add_argument("--model", help="Path to trained HRM model")
    parser.add_argument("--output", help="Output file for report")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.basicConfig(level=logging.INFO)
    
    analyzer = CodeAnalyzer(model_path=args.model)
    
    if os.path.isfile(args.path):
        result = analyzer.analyze_file(args.path)
        results = [result]
    else:
        results = analyzer.analyze_directory(args.path)
    
    # Generate and display report
    report = analyzer.generate_report(results)
    
    if args.output:
        with open(args.output, 'w') as f:
            f.write(report)
        print(f"Report saved to {args.output}")
    else:
        print(report)


if __name__ == "__main__":
    main()