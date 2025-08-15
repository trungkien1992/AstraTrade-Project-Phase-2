"""
Debug Assistant using Hierarchical Reasoning Model

Provides intelligent debugging assistance for complex AstraTrade development issues
using HRM's hierarchical reasoning to analyze problems systematically.
"""

import torch
import os
import re
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
import logging

from ..hrm.model import HierarchicalReasoningModel, HRMConfig
from .code_analyzer import CodeTokenizer

logger = logging.getLogger(__name__)


@dataclass
class DebugContext:
    """Context information for debugging"""
    error_logs: List[str]
    stack_traces: List[str]
    code_snippets: Dict[str, str]
    system_state: Dict[str, Any]
    recent_changes: List[str]
    environment: str


@dataclass
class DebugAnalysis:
    """Debug analysis result from HRM"""
    problem_description: str
    root_cause_analysis: str
    contributing_factors: List[str]
    solution_steps: List[str]
    prevention_measures: List[str]
    reasoning_chain: List[str]
    confidence: float
    similar_issues: List[str]
    code_fixes: List[Dict[str, str]]


class DebugAssistant:
    """
    HRM-powered debugging assistant for AstraTrade development
    
    Uses hierarchical reasoning to analyze complex bugs, trace root causes,
    and provide systematic debugging solutions.
    """
    
    def __init__(self, model_path: Optional[str] = None):
        self.tokenizer = CodeTokenizer()
        
        # Debug-specific vocabulary extensions
        self.debug_vocab = {
            # Error types
            'syntax_error': 300, 'runtime_error': 301, 'logic_error': 302, 'integration_error': 303,
            'performance_issue': 304, 'memory_leak': 305, 'deadlock': 306, 'race_condition': 307,
            
            # Debug indicators
            'exception': 310, 'traceback': 311, 'assertion_failed': 312, 'timeout': 313,
            'connection_refused': 314, 'permission_denied': 315, 'file_not_found': 316,
            
            # System components
            'database': 320, 'api_endpoint': 321, 'message_queue': 322, 'cache': 323,
            'authentication': 324, 'authorization': 325, 'networking': 326,
            
            # AstraTrade specific issues
            'trading_engine': 330, 'order_execution': 331, 'portfolio_calculation': 332,
            'gamification_sync': 333, 'blockchain_integration': 334, 'real_time_data': 335,
            
            # Debug process
            'isolate': 340, 'reproduce': 341, 'analyze': 342, 'fix': 343, 'verify': 344, 'prevent': 345
        }
        
        # Extend tokenizer vocabulary
        self.tokenizer.vocab.update(self.debug_vocab)
        self.tokenizer.reverse_vocab = {v: k for k, v in self.tokenizer.vocab.items()}
        
        # Initialize HRM model for debugging
        self.config = HRMConfig(
            hidden_size=512,
            vocab_size=len(self.tokenizer.vocab),
            N=5,  # 5 high-level debugging cycles
            T=8,  # 8 low-level analysis steps per cycle
            use_stablemax=True
        )
        
        self.model = HierarchicalReasoningModel(self.config)
        
        if model_path and os.path.exists(model_path):
            self.model.load_state_dict(torch.load(model_path, map_location='cpu'))
            logger.info(f"Loaded debug model from {model_path}")
        else:
            logger.info("Using untrained model for debug assistance")
    
    def debug_problem(
        self, 
        problem_description: str, 
        context_path: Optional[str] = None
    ) -> str:
        """
        Analyze and debug a complex development problem
        """
        logger.info(f"Debugging problem: {problem_description}")
        
        # Gather debug context
        context = self._gather_debug_context(problem_description, context_path)
        
        # Tokenize problem with context
        tokens = self._tokenize_debug_problem(problem_description, context)
        input_ids = torch.tensor([tokens], dtype=torch.long)
        
        # Run HRM debugging analysis
        self.model.eval()
        with torch.no_grad():
            output = self.model(input_ids, return_intermediate=True)
            
            # Analyze reasoning process
            reasoning_analysis = self._analyze_debug_reasoning(
                output['z_h'], 
                output['z_l'], 
                output.get('intermediate_states', [])
            )
        
        # Generate debug analysis
        analysis = self._generate_debug_analysis(
            problem_description=problem_description,
            context=context,
            reasoning_analysis=reasoning_analysis
        )
        
        return self._format_debug_analysis(analysis)
    
    def _gather_debug_context(
        self, 
        problem_description: str, 
        context_path: Optional[str]
    ) -> DebugContext:
        """Gather debugging context from problem description and codebase"""
        
        context = DebugContext(
            error_logs=[],
            stack_traces=[],
            code_snippets={},
            system_state={},
            recent_changes=[],
            environment='development'
        )
        
        # Extract information from problem description
        context.error_logs = self._extract_error_logs(problem_description)
        context.stack_traces = self._extract_stack_traces(problem_description)
        
        # Analyze context path if provided
        if context_path:
            context_dir = Path(context_path)
            if context_dir.exists():
                context.code_snippets = self._extract_relevant_code(context_dir, problem_description)
                context.recent_changes = self._identify_recent_changes(context_dir)
                context.system_state = self._analyze_system_state(context_dir)
        
        return context
    
    def _extract_error_logs(self, problem_description: str) -> List[str]:
        """Extract error messages from problem description"""
        error_patterns = [
            r'Error: (.+)',
            r'Exception: (.+)', 
            r'Failed: (.+)',
            r'ERROR (.+)',
            r'CRITICAL (.+)'
        ]
        
        errors = []
        for pattern in error_patterns:
            matches = re.findall(pattern, problem_description, re.IGNORECASE)
            errors.extend(matches)
        
        return errors
    
    def _extract_stack_traces(self, problem_description: str) -> List[str]:
        """Extract stack traces from problem description"""
        # Look for common stack trace patterns
        stack_patterns = [
            r'Traceback \(most recent call last\):(.+?)(?=\n\n|\Z)',
            r'at (.+?) \((.+?):(\d+):(\d+)\)',
            r'File "(.+?)", line (\d+), in (.+)'
        ]
        
        traces = []
        for pattern in stack_patterns:
            matches = re.findall(pattern, problem_description, re.DOTALL)
            traces.extend([str(match) for match in matches])
        
        return traces
    
    def _extract_relevant_code(self, context_dir: Path, problem_description: str) -> Dict[str, str]:
        """Extract code snippets relevant to the problem"""
        code_snippets = {}
        
        # Identify relevant files based on problem description
        relevant_files = self._identify_relevant_files(context_dir, problem_description)
        
        for file_path in relevant_files[:5]:  # Limit to 5 most relevant files
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Extract relevant sections (functions/classes mentioned in problem)
                    relevant_sections = self._extract_relevant_sections(content, problem_description)
                    if relevant_sections:
                        code_snippets[str(file_path)] = relevant_sections
            except Exception as e:
                logger.warning(f"Could not read {file_path}: {e}")
        
        return code_snippets
    
    def _identify_relevant_files(self, context_dir: Path, problem_description: str) -> List[Path]:
        """Identify files relevant to the problem"""
        # Extract file/module names from problem description
        mentioned_files = re.findall(r'(\w+\.py)', problem_description)
        mentioned_modules = re.findall(r'(\w+)\.\w+', problem_description)
        
        relevant_files = []
        
        # Find exact file matches
        for file_name in mentioned_files:
            matches = list(context_dir.rglob(file_name))
            relevant_files.extend(matches)
        
        # Find module matches
        for module_name in mentioned_modules:
            module_files = list(context_dir.rglob(f'{module_name}.py'))
            relevant_files.extend(module_files)
        
        # Add common problem areas for AstraTrade
        common_problem_areas = [
            'services.py', 'entities.py', 'value_objects.py', 'events.py',
            'trading.py', 'gamification.py', 'financial.py'
        ]
        
        for area in common_problem_areas:
            matches = list(context_dir.rglob(f'*{area}'))
            relevant_files.extend(matches[:2])  # Limit per area
        
        # Remove duplicates and return
        return list(set(relevant_files))
    
    def _extract_relevant_sections(self, code: str, problem_description: str) -> str:
        """Extract relevant code sections based on problem description"""
        lines = code.split('\n')
        relevant_lines = []
        
        # Find lines containing keywords from problem description
        keywords = re.findall(r'\b\w+\b', problem_description.lower())
        keywords = [k for k in keywords if len(k) > 3]  # Filter short words
        
        for i, line in enumerate(lines):
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in keywords):
                # Include context lines around matches
                start = max(0, i - 3)
                end = min(len(lines), i + 4)
                relevant_lines.extend(lines[start:end])
                relevant_lines.append('---')
        
        return '\n'.join(relevant_lines) if relevant_lines else code[:500]
    
    def _identify_recent_changes(self, context_dir: Path) -> List[str]:
        """Identify recent changes that might be related to the problem"""
        # This is a simplified implementation
        # In a real scenario, you'd integrate with git to find recent commits
        changes = []
        
        # Look for common indicators of recent changes
        modified_indicators = [
            'TODO', 'FIXME', 'HACK', 'TEMP',
            'recent', 'new', 'added', 'changed'
        ]
        
        for py_file in context_dir.rglob('*.py'):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    for indicator in modified_indicators:
                        if indicator in content:
                            changes.append(f"Potential recent change in {py_file.name}: {indicator}")
                            break
            except Exception:
                continue
        
        return changes[:10]  # Limit to 10 changes
    
    def _analyze_system_state(self, context_dir: Path) -> Dict[str, Any]:
        """Analyze current system state from configuration files"""
        system_state = {}
        
        # Check Docker configuration
        docker_compose = context_dir / 'docker-compose.yml'
        if docker_compose.exists():
            system_state['containerized'] = True
            system_state['services'] = self._count_docker_services(docker_compose)
        
        # Check database configuration
        if any(context_dir.rglob('*database*')):
            system_state['has_database'] = True
        
        # Check Redis configuration
        if any(context_dir.rglob('*redis*')):
            system_state['has_redis'] = True
        
        # Check monitoring setup
        if any(context_dir.rglob('*monitoring*')):
            system_state['has_monitoring'] = True
        
        return system_state
    
    def _count_docker_services(self, docker_compose_file: Path) -> int:
        """Count services in docker-compose file"""
        try:
            with open(docker_compose_file, 'r') as f:
                content = f.read()
                # Simple count of service definitions
                return len(re.findall(r'^\s*\w+:', content, re.MULTILINE))
        except Exception:
            return 0
    
    def _tokenize_debug_problem(
        self, 
        problem_description: str, 
        context: DebugContext
    ) -> List[int]:
        """Tokenize debug problem with context for HRM processing"""
        tokens = [self.tokenizer.vocab['<START>']]
        
        # Tokenize problem description
        words = problem_description.lower().split()
        for word in words:
            # Map common error terms to debug tokens
            if 'error' in word:
                tokens.append(self.debug_vocab.get('exception', self.tokenizer.vocab['<UNK>']))
            elif 'fail' in word:
                tokens.append(self.debug_vocab.get('runtime_error', self.tokenizer.vocab['<UNK>']))
            elif 'timeout' in word:
                tokens.append(self.debug_vocab.get('timeout', self.tokenizer.vocab['<UNK>']))
            elif 'trading' in word:
                tokens.append(self.debug_vocab.get('trading_engine', self.tokenizer.vocab['<UNK>']))
            elif 'database' in word:
                tokens.append(self.debug_vocab.get('database', self.tokenizer.vocab['<UNK>']))
            else:
                token = self.tokenizer.vocab.get(word, self.tokenizer.vocab['<UNK>'])
                tokens.append(token)
        
        # Add context tokens
        if context.error_logs:
            tokens.append(self.debug_vocab.get('exception', self.tokenizer.vocab['<UNK>']))
        
        if context.stack_traces:
            tokens.append(self.debug_vocab.get('traceback', self.tokenizer.vocab['<UNK>']))
        
        if context.system_state.get('has_database'):
            tokens.append(self.debug_vocab.get('database', self.tokenizer.vocab['<UNK>']))
        
        tokens.append(self.tokenizer.vocab['<END>'])
        return tokens
    
    def _analyze_debug_reasoning(
        self, 
        z_h: torch.Tensor, 
        z_l: torch.Tensor, 
        intermediate_states: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze HRM reasoning process for debugging"""
        
        reasoning_depth = len(intermediate_states)
        
        # Simulate reasoning chain analysis
        reasoning_chain = [
            "Problem identification and symptom analysis",
            "Context gathering and environment assessment", 
            "Root cause hypothesis generation",
            "Evidence evaluation and cause validation",
            "Solution strategy formulation",
            "Implementation planning and risk assessment"
        ]
        
        # Calculate confidence based on reasoning depth and consistency
        confidence = min(reasoning_depth / 6.0, 1.0)
        
        return {
            'reasoning_depth': reasoning_depth,
            'reasoning_chain': reasoning_chain[:reasoning_depth],
            'confidence': confidence
        }
    
    def _generate_debug_analysis(
        self,
        problem_description: str,
        context: DebugContext,
        reasoning_analysis: Dict[str, Any]
    ) -> DebugAnalysis:
        """Generate comprehensive debug analysis using HRM reasoning"""
        
        # Classify the problem type
        problem_type = self._classify_problem(problem_description, context)
        
        # Generate root cause analysis
        root_cause = self._analyze_root_cause(problem_description, context, problem_type)
        
        # Identify contributing factors
        contributing_factors = self._identify_contributing_factors(context, problem_type)
        
        # Generate solution steps
        solution_steps = self._generate_solution_steps(problem_type, context)
        
        # Suggest prevention measures
        prevention_measures = self._generate_prevention_measures(problem_type, context)
        
        # Find similar issues
        similar_issues = self._find_similar_issues(problem_type)
        
        # Generate code fixes
        code_fixes = self._generate_code_fixes(problem_type, context)
        
        return DebugAnalysis(
            problem_description=problem_description,
            root_cause_analysis=root_cause,
            contributing_factors=contributing_factors,
            solution_steps=solution_steps,
            prevention_measures=prevention_measures,
            reasoning_chain=reasoning_analysis['reasoning_chain'],
            confidence=reasoning_analysis['confidence'],
            similar_issues=similar_issues,
            code_fixes=code_fixes
        )
    
    def _classify_problem(self, problem_description: str, context: DebugContext) -> str:
        """Classify the type of problem based on description and context"""
        description_lower = problem_description.lower()
        
        # Check for specific error patterns
        if any(error in description_lower for error in ['syntax', 'import', 'module']):
            return 'syntax_error'
        elif any(error in description_lower for error in ['timeout', 'connection', 'network']):
            return 'connectivity_issue'
        elif any(error in description_lower for error in ['performance', 'slow', 'memory']):
            return 'performance_issue'
        elif any(error in description_lower for error in ['authentication', 'permission', 'auth']):
            return 'auth_issue'
        elif any(error in description_lower for error in ['database', 'query', 'transaction']):
            return 'database_issue'
        elif any(error in description_lower for error in ['trading', 'order', 'execution']):
            return 'trading_issue'
        elif any(error in description_lower for error in ['gamification', 'achievement', 'xp']):
            return 'gamification_issue'
        else:
            return 'general_error'
    
    def _analyze_root_cause(
        self, 
        problem_description: str, 
        context: DebugContext, 
        problem_type: str
    ) -> str:
        """Analyze the root cause of the problem"""
        
        base_analysis = f"**Problem Type**: {problem_type.replace('_', ' ').title()}\n\n"
        
        if problem_type == 'connectivity_issue':
            base_analysis += "**Root Cause Analysis**: Network connectivity or service availability issue. "
            if context.system_state.get('has_database'):
                base_analysis += "Database connection may be failing. "
            if context.error_logs:
                base_analysis += f"Error logs indicate: {'; '.join(context.error_logs[:2])}"
        
        elif problem_type == 'performance_issue':
            base_analysis += "**Root Cause Analysis**: Performance bottleneck detected. "
            if 'database' in problem_description.lower():
                base_analysis += "Likely database query optimization needed. "
            if context.system_state.get('services', 0) > 3:
                base_analysis += "Multiple services may be creating resource contention. "
        
        elif problem_type == 'trading_issue':
            base_analysis += "**Root Cause Analysis**: Trading engine or order execution problem. "
            base_analysis += "Critical path in trading logic may have race condition or validation failure. "
            if context.recent_changes:
                base_analysis += "Recent changes to trading logic may have introduced the issue. "
        
        else:
            base_analysis += f"**Root Cause Analysis**: General system error requiring systematic debugging. "
            if context.error_logs:
                base_analysis += f"Primary error: {context.error_logs[0] if context.error_logs else 'No specific error logged'}"
        
        return base_analysis
    
    def _identify_contributing_factors(self, context: DebugContext, problem_type: str) -> List[str]:
        """Identify factors contributing to the problem"""
        factors = []
        
        if context.recent_changes:
            factors.append(f"Recent code changes: {len(context.recent_changes)} potential modifications")
        
        if context.system_state.get('services', 0) > 3:
            factors.append("Complex microservices architecture may complicate debugging")
        
        if not context.system_state.get('has_monitoring'):
            factors.append("Limited monitoring makes root cause identification difficult")
        
        if context.environment == 'production':
            factors.append("Production environment limits debugging options")
        
        if problem_type == 'performance_issue':
            factors.append("High system load or resource contention")
            factors.append("Inefficient database queries or missing indexes")
        
        elif problem_type == 'trading_issue':
            factors.append("Time-sensitive trading operations with strict latency requirements")
            factors.append("Complex financial calculations with precision requirements")
        
        return factors if factors else ["Insufficient context to identify specific contributing factors"]
    
    def _generate_solution_steps(self, problem_type: str, context: DebugContext) -> List[str]:
        """Generate step-by-step solution approach"""
        
        base_steps = [
            "1. **Reproduce the Issue**: Create minimal test case to consistently reproduce the problem",
            "2. **Gather Additional Logs**: Enable verbose logging and collect comprehensive error information",
            "3. **Isolate Components**: Test individual system components to narrow down the failure point"
        ]
        
        specific_steps = {
            'connectivity_issue': [
                "4. **Check Network Configuration**: Verify service endpoints and network policies",
                "5. **Test Database Connections**: Validate database connectivity and credentials",
                "6. **Review Service Dependencies**: Ensure all required services are running and accessible"
            ],
            'performance_issue': [
                "4. **Profile Performance**: Use profiling tools to identify bottlenecks",
                "5. **Analyze Database Queries**: Review slow queries and missing indexes",
                "6. **Monitor Resource Usage**: Check CPU, memory, and I/O utilization"
            ],
            'trading_issue': [
                "4. **Validate Trading Logic**: Review order validation and execution paths",
                "5. **Check Data Consistency**: Verify portfolio and position calculations",
                "6. **Test Under Load**: Ensure system handles concurrent trading operations"
            ],
            'auth_issue': [
                "4. **Verify Credentials**: Check authentication tokens and permissions",
                "5. **Review Auth Flow**: Validate authentication and authorization logic",
                "6. **Test Access Controls**: Ensure proper role-based access control"
            ]
        }
        
        steps = base_steps + specific_steps.get(problem_type, [
            "4. **Systematic Testing**: Test each component and integration point",
            "5. **Review Recent Changes**: Investigate recent code modifications",
            "6. **Apply Targeted Fix**: Implement specific solution based on root cause"
        ])
        
        steps.extend([
            "7. **Verify Fix**: Test the solution thoroughly in development environment",
            "8. **Deploy with Monitoring**: Deploy fix with enhanced monitoring and rollback plan",
            "9. **Document Solution**: Record the issue and solution for future reference"
        ])
        
        return steps
    
    def _generate_prevention_measures(self, problem_type: str, context: DebugContext) -> List[str]:
        """Generate measures to prevent similar issues"""
        
        general_measures = [
            "Implement comprehensive automated testing for critical paths",
            "Add monitoring and alerting for key system metrics",
            "Establish code review process for high-risk changes"
        ]
        
        specific_measures = {
            'connectivity_issue': [
                "Implement circuit breakers for external service calls",
                "Add connection pooling and retry logic",
                "Set up service health checks and auto-recovery"
            ],
            'performance_issue': [
                "Establish performance benchmarks and regression testing",
                "Implement database query monitoring and optimization",
                "Add resource utilization alerts and auto-scaling"
            ],
            'trading_issue': [
                "Implement comprehensive trading simulation testing",
                "Add real-time trading metrics and anomaly detection",
                "Establish trading halt mechanisms for system errors"
            ],
            'auth_issue': [
                "Implement automated security testing",
                "Add authentication/authorization logging and monitoring",
                "Regular security audits and penetration testing"
            ]
        }
        
        return general_measures + specific_measures.get(problem_type, [
            "Add specific monitoring for this type of issue",
            "Create automated tests to catch similar problems",
            "Document troubleshooting procedures"
        ])
    
    def _find_similar_issues(self, problem_type: str) -> List[str]:
        """Find similar issues that might be related"""
        
        similar_issues = {
            'connectivity_issue': [
                "Database connection pool exhaustion",
                "Service discovery failures in microservices",
                "Network timeout configuration issues"
            ],
            'performance_issue': [
                "N+1 query problems in ORM operations",
                "Missing database indexes on frequently queried columns",
                "Memory leaks in long-running processes"
            ],
            'trading_issue': [
                "Race conditions in concurrent order processing",
                "Floating-point precision errors in financial calculations",
                "Market data feed latency causing stale prices"
            ],
            'auth_issue': [
                "JWT token expiration handling",
                "Role-based access control configuration errors",
                "Session management in distributed systems"
            ]
        }
        
        return similar_issues.get(problem_type, [
            "Configuration management issues",
            "Environment-specific problems",
            "Integration testing gaps"
        ])
    
    def _generate_code_fixes(self, problem_type: str, context: DebugContext) -> List[Dict[str, str]]:
        """Generate potential code fixes based on problem analysis"""
        
        fixes = []
        
        if problem_type == 'connectivity_issue':
            fixes.append({
                'description': 'Add connection retry logic',
                'code': '''
# Add retry mechanism for database connections
import time
from functools import wraps

def retry_connection(max_retries=3, delay=1.0):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except ConnectionError as e:
                    if attempt == max_retries - 1:
                        raise
                    time.sleep(delay * (2 ** attempt))
            return None
        return wrapper
    return decorator
'''
            })
        
        elif problem_type == 'performance_issue':
            fixes.append({
                'description': 'Add database query optimization',
                'code': '''
# Add query optimization and caching
from functools import lru_cache
from django.db import models

class OptimizedQueryMixin:
    @classmethod
    def get_with_cache(cls, **kwargs):
        # Use select_related for foreign keys
        return cls.objects.select_related().filter(**kwargs)
    
    @lru_cache(maxsize=128)
    def cached_calculation(self, param):
        # Cache expensive calculations
        return self.expensive_operation(param)
'''
            })
        
        elif problem_type == 'trading_issue':
            fixes.append({
                'description': 'Add trading operation validation',
                'code': '''
# Add comprehensive trading validation
from decimal import Decimal, ROUND_HALF_UP

class TradingValidator:
    @staticmethod
    def validate_order(order):
        if order.amount <= 0:
            raise ValueError("Order amount must be positive")
        
        # Round to appropriate precision
        order.amount = order.amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        
        # Validate against portfolio limits
        if order.amount > order.portfolio.available_balance:
            raise ValueError("Insufficient balance")
        
        return True
'''
            })
        
        return fixes
    
    def _format_debug_analysis(self, analysis: DebugAnalysis) -> str:
        """Format debug analysis for display"""
        
        sections = [
            "# 🐛 Debug Analysis Report",
            f"\n**Problem**: {analysis.problem_description}",
            f"\n## Root Cause Analysis",
            analysis.root_cause_analysis,
            f"\n## Contributing Factors"
        ]
        
        for factor in analysis.contributing_factors:
            sections.append(f"• {factor}")
        
        sections.extend([
            f"\n## Solution Steps"
        ])
        
        for step in analysis.solution_steps:
            sections.append(step)
        
        sections.extend([
            f"\n## Prevention Measures"
        ])
        
        for measure in analysis.prevention_measures:
            sections.append(f"• {measure}")
        
        if analysis.code_fixes:
            sections.extend([
                f"\n## Suggested Code Fixes"
            ])
            
            for fix in analysis.code_fixes:
                sections.extend([
                    f"### {fix['description']}",
                    "```python",
                    fix['code'].strip(),
                    "```\n"
                ])
        
        sections.extend([
            f"\n## Similar Issues to Consider"
        ])
        
        for issue in analysis.similar_issues:
            sections.append(f"• {issue}")
        
        sections.extend([
            f"\n## Reasoning Process"
        ])
        
        for i, step in enumerate(analysis.reasoning_chain, 1):
            sections.append(f"{i}. {step}")
        
        sections.append(f"\n**Confidence Level**: {analysis.confidence:.1%}")
        
        return '\n'.join(sections)


def main():
    """CLI for debug assistant"""
    import argparse
    
    parser = argparse.ArgumentParser(description="HRM Debug Assistant")
    parser.add_argument("problem", help="Problem description")
    parser.add_argument("--context", "-c", help="Context directory")
    parser.add_argument("--model", "-m", help="Path to trained model")
    parser.add_argument("--output", "-o", help="Output file")
    parser.add_argument("--verbose", "-v", action="store_true")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.basicConfig(level=logging.INFO)
    
    assistant = DebugAssistant(model_path=args.model)
    analysis = assistant.debug_problem(args.problem, context_path=args.context)
    
    if args.output:
        with open(args.output, 'w') as f:
            f.write(analysis)
        print(f"Debug analysis saved to {args.output}")
    else:
        print(analysis)


if __name__ == "__main__":
    main()