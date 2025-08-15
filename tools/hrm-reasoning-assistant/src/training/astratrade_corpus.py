"""
AstraTrade Corpus Builder

Creates training data from the AstraTrade codebase for HRM reasoning training.
Extracts patterns, problem-solution pairs, and architectural decisions.
"""

import os
import ast
import json
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class CodePattern:
    """Represents a code pattern extracted from AstraTrade codebase"""
    pattern_type: str
    pattern_name: str
    file_path: str
    code_snippet: str
    context: Dict[str, Any]
    complexity: int
    reasoning_steps: List[str]


@dataclass
class ProblemSolution:
    """Represents a problem-solution pair for training"""
    problem_description: str
    problem_context: Dict[str, Any]
    solution_steps: List[str]
    code_changes: List[Dict[str, Any]]
    reasoning_process: List[str]
    domain: str  # trading, gamification, financial, etc.


class AstraTradeCorpusBuilder:
    """
    Builds training corpus from AstraTrade codebase for HRM reasoning enhancement
    """
    
    def __init__(self, astratrade_root: str):
        self.astratrade_root = Path(astratrade_root)
        self.patterns = []
        self.problem_solutions = []
        
    def build_corpus(self) -> Dict[str, Any]:
        """
        Build complete training corpus from AstraTrade codebase
        """
        logger.info("Building AstraTrade corpus for HRM training...")
        
        # Extract code patterns
        self._extract_domain_patterns()
        self._extract_architectural_patterns()
        self._extract_integration_patterns()
        
        # Generate problem-solution pairs
        self._generate_refactoring_problems()
        self._generate_integration_problems()
        self._generate_performance_problems()
        
        corpus = {
            'patterns': [self._pattern_to_dict(p) for p in self.patterns],
            'problem_solutions': [self._problem_solution_to_dict(ps) for ps in self.problem_solutions],
            'metadata': {
                'total_patterns': len(self.patterns),
                'total_problems': len(self.problem_solutions),
                'domains': self._get_domain_distribution(),
                'pattern_types': self._get_pattern_distribution()
            }
        }
        
        logger.info(f"Corpus built: {len(self.patterns)} patterns, {len(self.problem_solutions)} problem-solutions")
        return corpus
    
    def _extract_domain_patterns(self):
        """Extract domain-specific patterns from each domain"""
        domains = ['trading', 'gamification', 'financial', 'social', 'nft', 'user']
        
        for domain in domains:
            domain_path = self.astratrade_root / 'apps' / 'backend' / 'domains' / domain
            if domain_path.exists():
                self._extract_domain_service_patterns(domain_path, domain)
                self._extract_entity_patterns(domain_path, domain)
                self._extract_value_object_patterns(domain_path, domain)
    
    def _extract_domain_service_patterns(self, domain_path: Path, domain: str):
        """Extract domain service patterns"""
        services_file = domain_path / 'services.py'
        if services_file.exists():
            with open(services_file, 'r') as f:
                code = f.read()
            
            try:
                tree = ast.parse(code)
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef) and 'Service' in node.name:
                        # Extract service pattern
                        pattern = CodePattern(
                            pattern_type="domain_service",
                            pattern_name=f"{domain}_service",
                            file_path=str(services_file),
                            code_snippet=self._extract_class_code(code, node),
                            context={
                                'domain': domain,
                                'methods': [m.name for m in node.body if isinstance(m, ast.FunctionDef)],
                                'dependencies': self._extract_dependencies(node)
                            },
                            complexity=self._calculate_complexity(node),
                            reasoning_steps=self._generate_service_reasoning(node, domain)
                        )
                        self.patterns.append(pattern)
                        
            except Exception as e:
                logger.warning(f"Failed to parse {services_file}: {e}")
    
    def _extract_entity_patterns(self, domain_path: Path, domain: str):
        """Extract entity patterns"""
        entities_file = domain_path / 'entities.py'
        if entities_file.exists():
            with open(entities_file, 'r') as f:
                code = f.read()
            
            try:
                tree = ast.parse(code)
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        pattern = CodePattern(
                            pattern_type="domain_entity",
                            pattern_name=f"{domain}_{node.name.lower()}",
                            file_path=str(entities_file),
                            code_snippet=self._extract_class_code(code, node),
                            context={
                                'domain': domain,
                                'entity_name': node.name,
                                'attributes': self._extract_attributes(node),
                                'methods': [m.name for m in node.body if isinstance(m, ast.FunctionDef)]
                            },
                            complexity=self._calculate_complexity(node),
                            reasoning_steps=self._generate_entity_reasoning(node, domain)
                        )
                        self.patterns.append(pattern)
                        
            except Exception as e:
                logger.warning(f"Failed to parse {entities_file}: {e}")
    
    def _extract_value_object_patterns(self, domain_path: Path, domain: str):
        """Extract value object patterns"""
        vo_file = domain_path / 'value_objects.py'
        if vo_file.exists():
            with open(vo_file, 'r') as f:
                code = f.read()
            
            try:
                tree = ast.parse(code)
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        pattern = CodePattern(
                            pattern_type="value_object",
                            pattern_name=f"{domain}_{node.name.lower()}",
                            file_path=str(vo_file),
                            code_snippet=self._extract_class_code(code, node),
                            context={
                                'domain': domain,
                                'vo_name': node.name,
                                'is_dataclass': self._has_dataclass_decorator(node),
                                'attributes': self._extract_attributes(node)
                            },
                            complexity=self._calculate_complexity(node),
                            reasoning_steps=self._generate_vo_reasoning(node, domain)
                        )
                        self.patterns.append(pattern)
                        
            except Exception as e:
                logger.warning(f"Failed to parse {vo_file}: {e}")
    
    def _extract_architectural_patterns(self):
        """Extract architectural patterns from the codebase"""
        # Microservices pattern
        services_path = self.astratrade_root / 'apps' / 'backend' / 'services'
        if services_path.exists():
            for service_dir in services_path.iterdir():
                if service_dir.is_dir() and (service_dir / 'main.py').exists():
                    self._extract_microservice_pattern(service_dir)
        
        # Event-driven pattern
        events_path = self.astratrade_root / 'apps' / 'backend' / 'infrastructure' / 'events'
        if events_path.exists():
            self._extract_event_pattern(events_path)
        
        # API Gateway pattern
        gateway_file = self.astratrade_root / 'apps' / 'backend' / 'api_gateway.py'
        if gateway_file.exists():
            self._extract_gateway_pattern(gateway_file)
    
    def _extract_microservice_pattern(self, service_dir: Path):
        """Extract microservice architecture pattern"""
        main_file = service_dir / 'main.py'
        with open(main_file, 'r') as f:
            code = f.read()
        
        pattern = CodePattern(
            pattern_type="microservice",
            pattern_name=f"{service_dir.name}_microservice",
            file_path=str(main_file),
            code_snippet=code,
            context={
                'service_name': service_dir.name,
                'has_dockerfile': (service_dir / 'Dockerfile').exists(),
                'has_requirements': (service_dir / 'requirements.txt').exists(),
                'endpoints': self._extract_api_endpoints(code)
            },
            complexity=len(code.split('\n')),
            reasoning_steps=[
                "Identify service boundaries",
                "Define API endpoints",
                "Implement business logic",
                "Add monitoring and health checks",
                "Configure deployment"
            ]
        )
        self.patterns.append(pattern)
    
    def _extract_event_pattern(self, events_path: Path):
        """Extract event-driven architecture pattern"""
        event_files = list(events_path.glob('*.py'))
        for event_file in event_files:
            with open(event_file, 'r') as f:
                code = f.read()
            
            pattern = CodePattern(
                pattern_type="event_driven",
                pattern_name=f"event_{event_file.stem}",
                file_path=str(event_file),
                code_snippet=code,
                context={
                    'event_type': event_file.stem,
                    'has_handlers': 'handler' in code.lower(),
                    'has_schemas': 'schema' in code.lower(),
                    'uses_redis': 'redis' in code.lower()
                },
                complexity=len(code.split('\n')),
                reasoning_steps=[
                    "Define event schema",
                    "Implement event handlers",
                    "Set up event bus",
                    "Add error handling",
                    "Ensure delivery guarantees"
                ]
            )
            self.patterns.append(pattern)
    
    def _extract_integration_patterns(self):
        """Extract integration patterns"""
        # External API integrations
        integrations = [
            'extended_exchange_client.py',
            'astratrade_exchange_v2_service.dart',
            'starknet_service.dart'
        ]
        
        for integration in integrations:
            integration_files = list(self.astratrade_root.rglob(integration))
            for file_path in integration_files:
                self._extract_integration_pattern(file_path)
    
    def _extract_integration_pattern(self, file_path: Path):
        """Extract integration pattern from file"""
        try:
            with open(file_path, 'r') as f:
                code = f.read()
            
            pattern = CodePattern(
                pattern_type="external_integration",
                pattern_name=f"integration_{file_path.stem}",
                file_path=str(file_path),
                code_snippet=code[:1000],  # First 1000 chars
                context={
                    'integration_type': file_path.stem,
                    'language': file_path.suffix,
                    'has_auth': 'auth' in code.lower(),
                    'has_retry': 'retry' in code.lower(),
                    'has_error_handling': 'exception' in code.lower() or 'error' in code.lower()
                },
                complexity=len(code.split('\n')),
                reasoning_steps=[
                    "Define integration interface",
                    "Implement authentication",
                    "Add error handling and retries",
                    "Handle rate limiting",
                    "Add monitoring and logging"
                ]
            )
            self.patterns.append(pattern)
            
        except Exception as e:
            logger.warning(f"Failed to extract integration pattern from {file_path}: {e}")
    
    def _extract_gateway_pattern(self, gateway_file: Path):
        """Extract API gateway pattern"""
        try:
            with open(gateway_file, 'r') as f:
                code = f.read()
            
            pattern = CodePattern(
                pattern_type="api_gateway",
                pattern_name="api_gateway",
                file_path=str(gateway_file),
                code_snippet=code[:1000],  # First 1000 chars
                context={
                    'gateway_type': 'central_api_gateway',
                    'has_routing': 'route' in code.lower(),
                    'has_auth': 'auth' in code.lower(),
                    'has_middleware': 'middleware' in code.lower(),
                    'endpoints': self._extract_api_endpoints(code)
                },
                complexity=len(code.split('\n')),
                reasoning_steps=[
                    "Define gateway architecture",
                    "Implement request routing",
                    "Add authentication middleware",
                    "Set up rate limiting",
                    "Add monitoring and logging"
                ]
            )
            self.patterns.append(pattern)
            
        except Exception as e:
            logger.warning(f"Failed to extract gateway pattern from {gateway_file}: {e}")
    
    def _generate_refactoring_problems(self):
        """Generate refactoring problem-solution pairs"""
        # Example: Service consolidation problem
        self.problem_solutions.append(ProblemSolution(
            problem_description="Multiple services have overlapping functionality and need consolidation",
            problem_context={
                'services': ['trading_service.py', 'clan_trading_service.py'],
                'overlap': 'trading logic',
                'complexity': 'high'
            },
            solution_steps=[
                "Identify common functionality",
                "Create unified domain service",
                "Maintain interface contracts",
                "Migrate existing callers",
                "Remove duplicate code"
            ],
            code_changes=[
                {'action': 'consolidate', 'files': ['services.py']},
                {'action': 'update', 'files': ['api endpoints']},
                {'action': 'remove', 'files': ['old services']}
            ],
            reasoning_process=[
                "Analyze service dependencies",
                "Map functionality overlap",
                "Design consolidated interface",
                "Plan migration strategy",
                "Execute consolidation",
                "Verify functionality"
            ],
            domain="trading"
        ))
    
    def _generate_integration_problems(self):
        """Generate integration problem-solution pairs"""
        self.problem_solutions.append(ProblemSolution(
            problem_description="Need to integrate new gamification features with existing trading logic",
            problem_context={
                'domains': ['trading', 'gamification'],
                'integration_type': 'event-driven',
                'complexity': 'medium'
            },
            solution_steps=[
                "Define domain events",
                "Implement event handlers",
                "Set up event bus",
                "Add cross-domain communication",
                "Test integration"
            ],
            code_changes=[
                {'action': 'add', 'files': ['domain events']},
                {'action': 'update', 'files': ['event handlers']},
                {'action': 'configure', 'files': ['event bus']}
            ],
            reasoning_process=[
                "Identify integration points",
                "Choose communication pattern",
                "Design event schema",
                "Implement handlers",
                "Test end-to-end flow"
            ],
            domain="integration"
        ))
    
    def _generate_performance_problems(self):
        """Generate performance optimization problem-solution pairs"""
        self.problem_solutions.append(ProblemSolution(
            problem_description="System performance degrades under high trading load",
            problem_context={
                'bottleneck': 'database queries',
                'load_type': 'trading operations',
                'complexity': 'high'
            },
            solution_steps=[
                "Profile performance bottlenecks",
                "Optimize database queries",
                "Add caching layer",
                "Implement connection pooling",
                "Load test improvements"
            ],
            code_changes=[
                {'action': 'optimize', 'files': ['repository queries']},
                {'action': 'add', 'files': ['caching layer']},
                {'action': 'configure', 'files': ['connection pool']}
            ],
            reasoning_process=[
                "Identify performance bottlenecks",
                "Analyze query patterns",
                "Design optimization strategy",
                "Implement improvements",
                "Measure performance gains"
            ],
            domain="performance"
        ))
    
    # Helper methods
    
    def _extract_class_code(self, full_code: str, node: ast.ClassDef) -> str:
        """Extract class code from full file"""
        lines = full_code.split('\n')
        start_line = node.lineno - 1
        end_line = node.end_lineno if hasattr(node, 'end_lineno') else start_line + 20
        return '\n'.join(lines[start_line:end_line])
    
    def _extract_dependencies(self, node: ast.ClassDef) -> List[str]:
        """Extract class dependencies"""
        dependencies = []
        if hasattr(node, '__init__'):
            for child in ast.walk(node):
                if isinstance(child, ast.arg):
                    dependencies.append(child.arg)
        return dependencies
    
    def _calculate_complexity(self, node: ast.AST) -> int:
        """Calculate cyclomatic complexity"""
        complexity = 1
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
        return complexity
    
    def _extract_attributes(self, node: ast.ClassDef) -> List[str]:
        """Extract class attributes"""
        attributes = []
        for child in node.body:
            if isinstance(child, ast.AnnAssign) and hasattr(child.target, 'id'):
                attributes.append(child.target.id)
        return attributes
    
    def _has_dataclass_decorator(self, node: ast.ClassDef) -> bool:
        """Check if class has @dataclass decorator"""
        return any(
            isinstance(d, ast.Name) and d.id == 'dataclass'
            for d in node.decorator_list
        )
    
    def _extract_api_endpoints(self, code: str) -> List[str]:
        """Extract API endpoints from code"""
        endpoints = []
        for line in code.split('\n'):
            if '@app.' in line or '@router.' in line:
                endpoints.append(line.strip())
        return endpoints
    
    def _generate_service_reasoning(self, node: ast.ClassDef, domain: str) -> List[str]:
        """Generate reasoning steps for service patterns"""
        return [
            f"Identify {domain} domain boundaries",
            "Define service interface",
            "Implement business logic",
            "Add error handling",
            "Integrate with repositories",
            "Add domain events"
        ]
    
    def _generate_entity_reasoning(self, node: ast.ClassDef, domain: str) -> List[str]:
        """Generate reasoning steps for entity patterns"""
        return [
            f"Define {domain} entity identity",
            "Model entity attributes",
            "Add business methods",
            "Ensure invariants",
            "Handle state changes"
        ]
    
    def _generate_vo_reasoning(self, node: ast.ClassDef, domain: str) -> List[str]:
        """Generate reasoning steps for value object patterns"""
        return [
            f"Define {domain} value concept",
            "Ensure immutability",
            "Add validation rules",
            "Implement equality",
            "Provide conversions"
        ]
    
    def _get_domain_distribution(self) -> Dict[str, int]:
        """Get distribution of patterns by domain"""
        distribution = {}
        for pattern in self.patterns:
            domain = pattern.context.get('domain', 'unknown')
            distribution[domain] = distribution.get(domain, 0) + 1
        return distribution
    
    def _get_pattern_distribution(self) -> Dict[str, int]:
        """Get distribution of pattern types"""
        distribution = {}
        for pattern in self.patterns:
            pattern_type = pattern.pattern_type
            distribution[pattern_type] = distribution.get(pattern_type, 0) + 1
        return distribution
    
    def _pattern_to_dict(self, pattern: CodePattern) -> Dict[str, Any]:
        """Convert pattern to dictionary"""
        return {
            'pattern_type': pattern.pattern_type,
            'pattern_name': pattern.pattern_name,
            'file_path': pattern.file_path,
            'code_snippet': pattern.code_snippet,
            'context': pattern.context,
            'complexity': pattern.complexity,
            'reasoning_steps': pattern.reasoning_steps
        }
    
    def _problem_solution_to_dict(self, ps: ProblemSolution) -> Dict[str, Any]:
        """Convert problem-solution to dictionary"""
        return {
            'problem_description': ps.problem_description,
            'problem_context': ps.problem_context,
            'solution_steps': ps.solution_steps,
            'code_changes': ps.code_changes,
            'reasoning_process': ps.reasoning_process,
            'domain': ps.domain
        }
    
    def save_corpus(self, output_path: str):
        """Save corpus to file"""
        corpus = self.build_corpus()
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(corpus, f, indent=2, ensure_ascii=False)
        logger.info(f"Corpus saved to {output_path}")


def main():
    """CLI for building AstraTrade corpus"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Build AstraTrade training corpus")
    parser.add_argument("astratrade_root", help="Path to AstraTrade root directory")
    parser.add_argument("--output", "-o", default="astratrade_corpus.json", help="Output file")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.basicConfig(level=logging.INFO)
    
    builder = AstraTradeCorpusBuilder(args.astratrade_root)
    builder.save_corpus(args.output)
    
    print(f"AstraTrade corpus built and saved to {args.output}")


if __name__ == "__main__":
    main()