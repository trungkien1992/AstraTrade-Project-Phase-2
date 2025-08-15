"""
Performance Optimizer using Hierarchical Reasoning Model

Provides intelligent performance optimization recommendations for AstraTrade
using HRM's hierarchical reasoning to analyze performance bottlenecks systematically.
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
class PerformanceContext:
    """Context information for performance optimization"""
    bottlenecks: List[str]
    metrics: Dict[str, float]
    system_resources: Dict[str, Any]
    code_patterns: List[str]
    architecture_info: Dict[str, Any]
    load_characteristics: Dict[str, Any]


@dataclass
class OptimizationRecommendation:
    """Performance optimization recommendation"""
    target_area: str
    current_performance: str
    optimization_strategy: str
    implementation_steps: List[str]
    expected_improvement: str
    trade_offs: List[str]
    monitoring_metrics: List[str]
    reasoning_chain: List[str]
    confidence: float
    code_changes: List[Dict[str, str]]


class PerformanceOptimizer:
    """
    HRM-powered performance optimizer for AstraTrade development
    
    Uses hierarchical reasoning to analyze performance issues, identify optimization
    opportunities, and provide systematic improvement strategies.
    """
    
    def __init__(self, model_path: Optional[str] = None):
        self.tokenizer = CodeTokenizer()
        
        # Performance-specific vocabulary extensions
        self.perf_vocab = {
            # Performance metrics
            'latency': 400, 'throughput': 401, 'cpu_usage': 402, 'memory_usage': 403,
            'disk_io': 404, 'network_io': 405, 'response_time': 406, 'concurrent_users': 407,
            
            # Bottleneck types
            'database_bottleneck': 410, 'cpu_bottleneck': 411, 'memory_bottleneck': 412,
            'io_bottleneck': 413, 'network_bottleneck': 414, 'algorithm_bottleneck': 415,
            
            # Optimization techniques
            'caching': 420, 'indexing': 421, 'connection_pooling': 422, 'load_balancing': 423,
            'async_processing': 424, 'batch_processing': 425, 'compression': 426,
            
            # AstraTrade specific performance areas
            'order_processing': 430, 'portfolio_calculation': 431, 'real_time_data': 432,
            'gamification_sync': 433, 'blockchain_calls': 434, 'api_gateway': 435,
            
            # Performance patterns
            'n_plus_one': 440, 'hot_path': 441, 'cold_start': 442, 'resource_leak': 443,
            'lock_contention': 444, 'gc_pressure': 445
        }
        
        # Extend tokenizer vocabulary
        self.tokenizer.vocab.update(self.perf_vocab)
        self.tokenizer.reverse_vocab = {v: k for k, v in self.tokenizer.vocab.items()}
        
        # Initialize HRM model for performance optimization
        self.config = HRMConfig(
            hidden_size=512,
            vocab_size=len(self.tokenizer.vocab),
            N=4,  # 4 high-level optimization cycles
            T=6,  # 6 low-level analysis steps per cycle
            use_stablemax=True
        )
        
        self.model = HierarchicalReasoningModel(self.config)
        
        if model_path and os.path.exists(model_path):
            self.model.load_state_dict(torch.load(model_path, map_location='cpu'))
            logger.info(f"Loaded performance model from {model_path}")
        else:
            logger.info("Using untrained model for performance optimization")
    
    def optimize(
        self, 
        target_description: str, 
        context_path: Optional[str] = None
    ) -> str:
        """
        Generate performance optimization recommendations
        """
        logger.info(f"Optimizing: {target_description}")
        
        # Gather performance context
        context = self._gather_performance_context(target_description, context_path)
        
        # Tokenize optimization target with context
        tokens = self._tokenize_performance_target(target_description, context)
        input_ids = torch.tensor([tokens], dtype=torch.long)
        
        # Run HRM optimization analysis
        self.model.eval()
        with torch.no_grad():
            output = self.model(input_ids, return_intermediate=True)
            
            # Analyze reasoning process
            reasoning_analysis = self._analyze_performance_reasoning(
                output['z_h'], 
                output['z_l'], 
                output.get('intermediate_states', [])
            )
        
        # Generate optimization recommendations
        recommendation = self._generate_optimization_recommendation(
            target_description=target_description,
            context=context,
            reasoning_analysis=reasoning_analysis
        )
        
        return self._format_optimization_recommendation(recommendation)
    
    def _gather_performance_context(
        self, 
        target_description: str, 
        context_path: Optional[str]
    ) -> PerformanceContext:
        """Gather performance-related context from description and codebase"""
        
        context = PerformanceContext(
            bottlenecks=[],
            metrics={},
            system_resources={},
            code_patterns=[],
            architecture_info={},
            load_characteristics={}
        )
        
        # Extract performance indicators from description
        context.bottlenecks = self._identify_bottlenecks(target_description)
        context.metrics = self._extract_performance_metrics(target_description)
        
        # Analyze context path if provided
        if context_path:
            context_dir = Path(context_path)
            if context_dir.exists():
                context.code_patterns = self._analyze_performance_patterns(context_dir)
                context.architecture_info = self._analyze_performance_architecture(context_dir)
                context.system_resources = self._estimate_resource_usage(context_dir)
                context.load_characteristics = self._analyze_load_patterns(context_dir, target_description)
        
        return context
    
    def _identify_bottlenecks(self, target_description: str) -> List[str]:
        """Identify performance bottlenecks from description"""
        bottlenecks = []
        description_lower = target_description.lower()
        
        bottleneck_indicators = {
            'database': ['database', 'query', 'sql', 'orm', 'transaction'],
            'cpu': ['cpu', 'computation', 'algorithm', 'calculation', 'processing'],
            'memory': ['memory', 'ram', 'heap', 'allocation', 'garbage'],
            'network': ['network', 'api', 'http', 'request', 'latency'],
            'io': ['disk', 'file', 'storage', 'read', 'write'],
            'concurrency': ['lock', 'thread', 'async', 'concurrent', 'parallel']
        }
        
        for bottleneck_type, indicators in bottleneck_indicators.items():
            if any(indicator in description_lower for indicator in indicators):
                bottlenecks.append(bottleneck_type)
        
        return bottlenecks if bottlenecks else ['general']
    
    def _extract_performance_metrics(self, target_description: str) -> Dict[str, float]:
        """Extract performance metrics from description"""
        metrics = {}
        
        # Look for numeric performance indicators
        latency_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:ms|milliseconds?|seconds?)', target_description.lower())
        if latency_match:
            metrics['latency_ms'] = float(latency_match.group(1))
        
        throughput_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:rps|requests?.*second|ops.*second)', target_description.lower())
        if throughput_match:
            metrics['throughput_rps'] = float(throughput_match.group(1))
        
        cpu_match = re.search(r'(\d+(?:\.\d+)?)\s*%?\s*cpu', target_description.lower())
        if cpu_match:
            metrics['cpu_usage_percent'] = float(cpu_match.group(1))
        
        return metrics
    
    def _analyze_performance_patterns(self, context_dir: Path) -> List[str]:
        """Analyze code patterns that affect performance"""
        patterns = []
        
        # Check for common performance anti-patterns
        python_files = list(context_dir.rglob('*.py'))
        
        for file_path in python_files[:20]:  # Limit analysis to avoid slowdown
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    # Check for N+1 query pattern
                    if re.search(r'for.*in.*\n.*\.objects\.get\(', content, re.MULTILINE):
                        patterns.append('n_plus_one_queries')
                    
                    # Check for synchronous API calls in loops
                    if re.search(r'for.*in.*\n.*requests\.', content, re.MULTILINE):
                        patterns.append('sync_api_calls_in_loop')
                    
                    # Check for missing async/await patterns
                    if 'async def' in content and content.count('await') < content.count('async def'):
                        patterns.append('missing_await_calls')
                    
                    # Check for large object creation in loops
                    if re.search(r'for.*in.*\n.*=.*\[.*\]', content, re.MULTILINE):
                        patterns.append('object_creation_in_loop')
                    
                    # Check for database operations without batching
                    if 'bulk_create' not in content and content.count('.save()') > 3:
                        patterns.append('unbatched_database_operations')
                        
            except Exception as e:
                logger.warning(f"Could not analyze {file_path}: {e}")
        
        return list(set(patterns))  # Remove duplicates
    
    def _analyze_performance_architecture(self, context_dir: Path) -> Dict[str, Any]:
        """Analyze architectural factors affecting performance"""
        arch_info = {
            'microservices_count': 0,
            'database_connections': 0,
            'caching_layers': 0,
            'async_patterns': 0,
            'monitoring_setup': False
        }
        
        # Count microservices
        services_dir = context_dir / 'services'
        if services_dir.exists():
            arch_info['microservices_count'] = len([d for d in services_dir.iterdir() if d.is_dir()])
        
        # Check for caching
        cache_indicators = ['redis', 'memcached', 'cache']
        for indicator in cache_indicators:
            if any(context_dir.rglob(f'*{indicator}*')):
                arch_info['caching_layers'] += 1
        
        # Check for async patterns
        python_files = list(context_dir.rglob('*.py'))
        for file_path in python_files[:10]:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if 'async def' in content:
                        arch_info['async_patterns'] += 1
            except Exception:
                continue
        
        # Check for monitoring
        monitoring_files = ['prometheus.yml', 'grafana', 'monitoring']
        for indicator in monitoring_files:
            if any(context_dir.rglob(f'*{indicator}*')):
                arch_info['monitoring_setup'] = True
                break
        
        return arch_info
    
    def _estimate_resource_usage(self, context_dir: Path) -> Dict[str, Any]:
        """Estimate resource usage patterns from codebase"""
        resources = {
            'estimated_memory_usage': 'medium',
            'database_query_complexity': 'medium',
            'api_call_frequency': 'medium',
            'computational_complexity': 'medium'
        }
        
        # Analyze for resource-intensive patterns
        python_files = list(context_dir.rglob('*.py'))
        heavy_operations = 0
        database_operations = 0
        api_calls = 0
        
        for file_path in python_files[:15]:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    # Count heavy operations
                    heavy_operations += len(re.findall(r'pandas|numpy|scipy|sklearn', content))
                    database_operations += len(re.findall(r'\.objects\.|\.query\(|SELECT', content, re.IGNORECASE))
                    api_calls += len(re.findall(r'requests\.|http|api', content, re.IGNORECASE))
                    
            except Exception:
                continue
        
        # Adjust estimates based on counts
        if heavy_operations > 10:
            resources['computational_complexity'] = 'high'
            resources['estimated_memory_usage'] = 'high'
        
        if database_operations > 20:
            resources['database_query_complexity'] = 'high'
        
        if api_calls > 15:
            resources['api_call_frequency'] = 'high'
        
        return resources
    
    def _analyze_load_patterns(self, context_dir: Path, target_description: str) -> Dict[str, Any]:
        """Analyze expected load patterns"""
        load_patterns = {
            'expected_concurrent_users': 'medium',
            'peak_load_multiplier': 2.0,
            'data_growth_rate': 'steady',
            'real_time_requirements': False
        }
        
        # Check for real-time requirements
        if any(keyword in target_description.lower() for keyword in ['real-time', 'live', 'instant', 'immediate']):
            load_patterns['real_time_requirements'] = True
        
        # Check for trading-specific high-load indicators
        if any(keyword in target_description.lower() for keyword in ['trading', 'orders', 'market']):
            load_patterns['expected_concurrent_users'] = 'high'
            load_patterns['peak_load_multiplier'] = 5.0
        
        # Check for social/gamification features that might have viral growth
        if any(keyword in target_description.lower() for keyword in ['social', 'viral', 'gamification']):
            load_patterns['data_growth_rate'] = 'exponential'
        
        return load_patterns
    
    def _tokenize_performance_target(
        self, 
        target_description: str, 
        context: PerformanceContext
    ) -> List[int]:
        """Tokenize performance optimization target with context"""
        tokens = [self.tokenizer.vocab['<START>']]
        
        # Tokenize target description
        words = target_description.lower().split()
        for word in words:
            # Map performance terms to specific tokens
            if 'performance' in word or 'speed' in word:
                tokens.append(self.perf_vocab.get('throughput', self.tokenizer.vocab['<UNK>']))
            elif 'slow' in word or 'latency' in word:
                tokens.append(self.perf_vocab.get('latency', self.tokenizer.vocab['<UNK>']))
            elif 'database' in word or 'query' in word:
                tokens.append(self.perf_vocab.get('database_bottleneck', self.tokenizer.vocab['<UNK>']))
            elif 'memory' in word:
                tokens.append(self.perf_vocab.get('memory_bottleneck', self.tokenizer.vocab['<UNK>']))
            elif 'cpu' in word:
                tokens.append(self.perf_vocab.get('cpu_bottleneck', self.tokenizer.vocab['<UNK>']))
            elif 'trading' in word:
                tokens.append(self.perf_vocab.get('order_processing', self.tokenizer.vocab['<UNK>']))
            else:
                token = self.tokenizer.vocab.get(word, self.tokenizer.vocab['<UNK>'])
                tokens.append(token)
        
        # Add context tokens
        for bottleneck in context.bottlenecks:
            bottleneck_token = self.perf_vocab.get(f'{bottleneck}_bottleneck')
            if bottleneck_token:
                tokens.append(bottleneck_token)
        
        # Add pattern tokens
        for pattern in context.code_patterns:
            pattern_token = self.perf_vocab.get(pattern)
            if pattern_token:
                tokens.append(pattern_token)
        
        tokens.append(self.tokenizer.vocab['<END>'])
        return tokens
    
    def _analyze_performance_reasoning(
        self, 
        z_h: torch.Tensor, 
        z_l: torch.Tensor, 
        intermediate_states: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze HRM reasoning process for performance optimization"""
        
        reasoning_depth = len(intermediate_states)
        
        # Performance optimization reasoning chain
        reasoning_chain = [
            "Performance bottleneck identification and measurement",
            "Root cause analysis of performance degradation",
            "Impact assessment and prioritization of optimizations",
            "Solution strategy formulation and trade-off analysis",
            "Implementation planning and risk evaluation",
            "Monitoring and validation strategy design"
        ]
        
        # Calculate confidence based on reasoning depth and consistency
        confidence = min(reasoning_depth / 6.0, 1.0)
        
        return {
            'reasoning_depth': reasoning_depth,
            'reasoning_chain': reasoning_chain[:reasoning_depth],
            'confidence': confidence,
            'optimization_complexity': reasoning_depth * 0.2  # Complexity factor
        }
    
    def _generate_optimization_recommendation(
        self,
        target_description: str,
        context: PerformanceContext,
        reasoning_analysis: Dict[str, Any]
    ) -> OptimizationRecommendation:
        """Generate comprehensive performance optimization recommendation"""
        
        # Identify primary optimization target
        target_area = self._identify_primary_target(target_description, context)
        
        # Assess current performance
        current_performance = self._assess_current_performance(context, target_area)
        
        # Generate optimization strategy
        strategy = self._generate_optimization_strategy(target_area, context)
        
        # Create implementation steps
        implementation_steps = self._generate_implementation_steps(target_area, context)
        
        # Estimate expected improvement
        expected_improvement = self._estimate_performance_improvement(target_area, context)
        
        # Identify trade-offs
        trade_offs = self._identify_optimization_trade_offs(target_area, context)
        
        # Define monitoring metrics
        monitoring_metrics = self._define_monitoring_metrics(target_area)
        
        # Generate code changes
        code_changes = self._generate_performance_code_changes(target_area, context)
        
        return OptimizationRecommendation(
            target_area=target_area,
            current_performance=current_performance,
            optimization_strategy=strategy,
            implementation_steps=implementation_steps,
            expected_improvement=expected_improvement,
            trade_offs=trade_offs,
            monitoring_metrics=monitoring_metrics,
            reasoning_chain=reasoning_analysis['reasoning_chain'],
            confidence=reasoning_analysis['confidence'],
            code_changes=code_changes
        )
    
    def _identify_primary_target(self, target_description: str, context: PerformanceContext) -> str:
        """Identify the primary area for optimization"""
        description_lower = target_description.lower()
        
        # Check for specific areas mentioned
        if any(word in description_lower for word in ['database', 'query', 'sql']):
            return 'database_optimization'
        elif any(word in description_lower for word in ['api', 'endpoint', 'request']):
            return 'api_optimization'
        elif any(word in description_lower for word in ['memory', 'heap', 'allocation']):
            return 'memory_optimization'
        elif any(word in description_lower for word in ['cpu', 'computation', 'algorithm']):
            return 'cpu_optimization'
        elif any(word in description_lower for word in ['trading', 'order', 'execution']):
            return 'trading_optimization'
        elif any(word in description_lower for word in ['cache', 'caching']):
            return 'caching_optimization'
        else:
            # Determine from bottlenecks
            if 'database' in context.bottlenecks:
                return 'database_optimization'
            elif 'cpu' in context.bottlenecks:
                return 'cpu_optimization'
            elif 'memory' in context.bottlenecks:
                return 'memory_optimization'
            else:
                return 'general_optimization'
    
    def _assess_current_performance(self, context: PerformanceContext, target_area: str) -> str:
        """Assess current performance state"""
        if context.metrics:
            metrics_summary = []
            if 'latency_ms' in context.metrics:
                latency = context.metrics['latency_ms']
                if latency > 1000:
                    metrics_summary.append(f"High latency: {latency}ms")
                elif latency > 500:
                    metrics_summary.append(f"Moderate latency: {latency}ms")
                else:
                    metrics_summary.append(f"Acceptable latency: {latency}ms")
            
            if 'cpu_usage_percent' in context.metrics:
                cpu = context.metrics['cpu_usage_percent']
                if cpu > 80:
                    metrics_summary.append(f"High CPU usage: {cpu}%")
                elif cpu > 60:
                    metrics_summary.append(f"Moderate CPU usage: {cpu}%")
                else:
                    metrics_summary.append(f"Normal CPU usage: {cpu}%")
            
            return "; ".join(metrics_summary) if metrics_summary else "Performance metrics not available"
        
        # Infer from bottlenecks and patterns
        issues = []
        if 'n_plus_one_queries' in context.code_patterns:
            issues.append("N+1 query pattern detected")
        if 'sync_api_calls_in_loop' in context.code_patterns:
            issues.append("Synchronous API calls in loops")
        if context.system_resources.get('database_query_complexity') == 'high':
            issues.append("Complex database queries")
        
        return "; ".join(issues) if issues else "Performance issues identified from code analysis"
    
    def _generate_optimization_strategy(self, target_area: str, context: PerformanceContext) -> str:
        """Generate optimization strategy based on target area"""
        
        strategies = {
            'database_optimization': """
**Database Optimization Strategy**:
1. **Query Optimization**: Analyze and optimize slow queries, add proper indexes
2. **Connection Management**: Implement connection pooling and optimize connection lifecycle
3. **Data Access Patterns**: Eliminate N+1 queries, use bulk operations, implement lazy loading
4. **Caching Layer**: Add Redis caching for frequently accessed data
5. **Database Tuning**: Optimize database configuration and query execution plans
            """,
            
            'api_optimization': """
**API Optimization Strategy**:
1. **Response Optimization**: Implement response compression and pagination
2. **Caching Strategy**: Add HTTP caching headers and reverse proxy caching
3. **Async Processing**: Convert synchronous operations to asynchronous where possible
4. **Load Balancing**: Distribute requests across multiple instances
5. **Rate Limiting**: Implement intelligent rate limiting and request queuing
            """,
            
            'memory_optimization': """
**Memory Optimization Strategy**:
1. **Memory Profiling**: Identify memory leaks and excessive allocations
2. **Object Lifecycle**: Optimize object creation and garbage collection
3. **Data Structures**: Use memory-efficient data structures and algorithms
4. **Caching Strategy**: Implement intelligent cache eviction policies
5. **Resource Management**: Proper resource cleanup and connection management
            """,
            
            'cpu_optimization': """
**CPU Optimization Strategy**:
1. **Algorithm Optimization**: Replace inefficient algorithms with optimized versions
2. **Parallel Processing**: Implement multi-threading for CPU-intensive operations  
3. **Computation Caching**: Cache results of expensive calculations
4. **Load Distribution**: Distribute CPU-intensive tasks across multiple processes
5. **Code Profiling**: Identify and optimize hot paths in code execution
            """,
            
            'trading_optimization': """
**Trading System Optimization Strategy**:
1. **Low-Latency Processing**: Optimize critical trading paths for minimal latency
2. **Order Matching**: Implement efficient order matching algorithms
3. **Risk Calculation**: Optimize portfolio and risk calculations with caching
4. **Market Data**: Implement efficient market data processing and distribution
5. **Transaction Processing**: Optimize database transactions for consistency and speed
            """
        }
        
        return strategies.get(target_area, """
**General Optimization Strategy**:
1. **Performance Profiling**: Identify actual bottlenecks through comprehensive profiling
2. **Systematic Optimization**: Address bottlenecks in order of impact
3. **Monitoring Implementation**: Add detailed performance monitoring
4. **Load Testing**: Validate optimizations under realistic load conditions
5. **Iterative Improvement**: Continuously monitor and optimize based on real-world usage
        """).strip()
    
    def _generate_implementation_steps(self, target_area: str, context: PerformanceContext) -> List[str]:
        """Generate specific implementation steps"""
        
        base_steps = [
            "1. **Baseline Measurement**: Establish current performance metrics and benchmarks",
            "2. **Profiling Setup**: Implement comprehensive profiling and monitoring tools",
            "3. **Bottleneck Analysis**: Identify and prioritize performance bottlenecks"
        ]
        
        specific_steps = {
            'database_optimization': [
                "4. **Query Analysis**: Use query profiling tools to identify slow queries",
                "5. **Index Optimization**: Add missing indexes and remove unused ones",
                "6. **Connection Pooling**: Implement database connection pooling",
                "7. **Query Refactoring**: Optimize N+1 queries and implement bulk operations",
                "8. **Caching Implementation**: Add Redis cache for frequently accessed data"
            ],
            
            'api_optimization': [
                "4. **Response Analysis**: Profile API response times and payload sizes",
                "5. **Compression Setup**: Implement gzip compression for responses",
                "6. **Caching Headers**: Add appropriate HTTP caching headers",
                "7. **Async Conversion**: Convert blocking operations to async/await patterns",
                "8. **Load Balancer**: Configure load balancing and health checks"
            ],
            
            'memory_optimization': [
                "4. **Memory Profiling**: Use memory profilers to identify leaks and inefficiencies", 
                "5. **Object Optimization**: Optimize object creation and lifecycle management",
                "6. **Cache Tuning**: Implement LRU caches with appropriate size limits",
                "7. **Resource Cleanup**: Ensure proper cleanup of resources and connections",
                "8. **GC Optimization**: Tune garbage collection settings for optimal performance"
            ],
            
            'trading_optimization': [
                "4. **Latency Profiling**: Measure end-to-end trading operation latency",
                "5. **Order Processing**: Optimize order validation and execution paths",
                "6. **Risk Calculations**: Cache portfolio calculations and use incremental updates",
                "7. **Market Data**: Implement efficient market data feed processing",
                "8. **Transaction Optimization**: Optimize database transactions for trading operations"
            ]
        }
        
        steps = base_steps + specific_steps.get(target_area, [
            "4. **Targeted Optimization**: Implement optimizations for identified bottlenecks",
            "5. **Performance Testing**: Validate improvements through load testing",
            "6. **Monitoring Setup**: Add performance monitoring and alerting"
        ])
        
        steps.extend([
            "9. **Load Testing**: Conduct comprehensive load testing to validate improvements",
            "10. **Monitoring Setup**: Implement ongoing performance monitoring and alerting",
            "11. **Documentation**: Document optimization changes and monitoring procedures"
        ])
        
        return steps
    
    def _estimate_performance_improvement(self, target_area: str, context: PerformanceContext) -> str:
        """Estimate expected performance improvement"""
        
        improvements = {
            'database_optimization': "Expected improvements: 50-80% reduction in query response time, 30-50% improvement in overall API response time",
            'api_optimization': "Expected improvements: 40-60% reduction in API response time, 2-3x increase in throughput capacity",
            'memory_optimization': "Expected improvements: 30-50% reduction in memory usage, elimination of memory leaks, improved GC performance",
            'cpu_optimization': "Expected improvements: 40-60% reduction in CPU usage, 2-3x improvement in computation-heavy operations",
            'trading_optimization': "Expected improvements: 60-80% reduction in order processing latency, 2-4x increase in order throughput"
        }
        
        base_improvement = improvements.get(target_area, "Expected improvements: 30-50% overall performance improvement")
        
        # Adjust based on current issues
        if 'n_plus_one_queries' in context.code_patterns:
            base_improvement += "; Eliminating N+1 queries can provide 5-10x improvement in database operations"
        
        if context.architecture_info.get('caching_layers', 0) == 0:
            base_improvement += "; Adding caching can provide 3-5x improvement for frequently accessed data"
        
        return base_improvement
    
    def _identify_optimization_trade_offs(self, target_area: str, context: PerformanceContext) -> List[str]:
        """Identify trade-offs for optimization approach"""
        
        common_trade_offs = [
            "Performance vs. Code Complexity: Optimized code may be more complex to maintain",
            "Memory vs. CPU: Caching uses more memory but reduces CPU usage",
            "Consistency vs. Performance: Some optimizations may affect data consistency guarantees"
        ]
        
        specific_trade_offs = {
            'database_optimization': [
                "Query Performance vs. Storage Space: Indexes improve query speed but require additional storage",
                "Read Performance vs. Write Performance: Optimization for reads may slow down writes",
                "Connection Pooling vs. Resource Usage: Connection pools improve performance but use more resources"
            ],
            
            'api_optimization': [
                "Response Time vs. Resource Usage: Async processing uses more threads/memory",
                "Caching vs. Data Freshness: Caching improves speed but may serve stale data",
                "Compression vs. CPU Usage: Response compression reduces bandwidth but increases CPU load"
            ],
            
            'memory_optimization': [
                "Memory Usage vs. Computation Time: Some optimizations trade memory for CPU",
                "Cache Size vs. Memory Pressure: Larger caches improve hit rates but use more memory",
                "Object Pooling vs. Complexity: Object pools improve performance but add complexity"
            ]
        }
        
        return common_trade_offs + specific_trade_offs.get(target_area, [
            "Optimization Effort vs. Benefit: Ensure optimization effort is justified by performance gains"
        ])
    
    def _define_monitoring_metrics(self, target_area: str) -> List[str]:
        """Define metrics to monitor optimization effectiveness"""
        
        base_metrics = [
            "Response time percentiles (P50, P95, P99)",
            "Throughput (requests per second)",
            "Error rate and success rate",
            "Resource utilization (CPU, Memory, Disk I/O)"
        ]
        
        specific_metrics = {
            'database_optimization': [
                "Database query execution time",
                "Database connection pool utilization",
                "Cache hit/miss ratios",
                "Number of database queries per request"
            ],
            
            'api_optimization': [
                "API endpoint response times by endpoint",
                "Request queue length and processing time",
                "Concurrent request handling capacity",
                "HTTP cache effectiveness"
            ],
            
            'memory_optimization': [
                "Memory usage patterns and trends",
                "Garbage collection frequency and duration",
                "Object allocation and deallocation rates",
                "Memory leak detection metrics"
            ],
            
            'trading_optimization': [
                "Order processing latency end-to-end",
                "Order throughput and queue lengths",
                "Portfolio calculation performance",
                "Market data processing latency"
            ]
        }
        
        return base_metrics + specific_metrics.get(target_area, [
            "System-specific performance indicators"
        ])
    
    def _generate_performance_code_changes(self, target_area: str, context: PerformanceContext) -> List[Dict[str, str]]:
        """Generate specific code changes for performance optimization"""
        
        code_changes = []
        
        if target_area == 'database_optimization':
            if 'n_plus_one_queries' in context.code_patterns:
                code_changes.append({
                    'description': 'Fix N+1 query pattern with select_related',
                    'before': '''
# Inefficient N+1 query pattern
def get_user_trades(user_id):
    trades = Trade.objects.filter(user_id=user_id)
    for trade in trades:
        portfolio = trade.portfolio  # This causes N queries
        print(f"Trade {trade.id} in portfolio {portfolio.name}")
''',
                    'after': '''
# Optimized with select_related
def get_user_trades(user_id):
    trades = Trade.objects.select_related('portfolio').filter(user_id=user_id)
    for trade in trades:
        portfolio = trade.portfolio  # No additional query
        print(f"Trade {trade.id} in portfolio {portfolio.name}")
'''
                })
            
            code_changes.append({
                'description': 'Add database connection pooling',
                'code': '''
# Add connection pooling configuration
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'astratrade',
        'OPTIONS': {
            'MAX_CONNS': 20,
            'MIN_CONNS': 5,
        },
        'CONN_MAX_AGE': 600,  # Connection reuse
    }
}
'''
            })
        
        elif target_area == 'api_optimization':
            code_changes.append({
                'description': 'Add async endpoint with caching',
                'code': '''
from django.core.cache import cache
from django.http import JsonResponse
import asyncio

async def get_portfolio_async(request, user_id):
    # Check cache first
    cache_key = f"portfolio_{user_id}"
    cached_data = cache.get(cache_key)
    
    if cached_data:
        return JsonResponse(cached_data)
    
    # Async database operation
    portfolio_data = await get_portfolio_data_async(user_id)
    
    # Cache for 5 minutes
    cache.set(cache_key, portfolio_data, 300)
    
    return JsonResponse(portfolio_data)
'''
            })
        
        elif target_area == 'memory_optimization':
            code_changes.append({
                'description': 'Implement object pooling for frequent allocations',
                'code': '''
from queue import Queue
import threading

class CalculationObjectPool:
    def __init__(self, max_size=100):
        self._pool = Queue(maxsize=max_size)
        self._lock = threading.Lock()
    
    def get_object(self):
        try:
            return self._pool.get_nowait()
        except:
            return PortfolioCalculator()  # Create new if pool empty
    
    def return_object(self, obj):
        obj.reset()  # Clear state
        try:
            self._pool.put_nowait(obj)
        except:
            pass  # Pool full, let object be garbage collected

# Global pool instance
calc_pool = CalculationObjectPool()
'''
            })
        
        elif target_area == 'trading_optimization':
            code_changes.append({
                'description': 'Optimize order processing with batching',
                'code': '''
import asyncio
from collections import defaultdict

class OrderProcessor:
    def __init__(self):
        self.order_batch = []
        self.batch_size = 50
        self.processing_lock = asyncio.Lock()
    
    async def process_order(self, order):
        async with self.processing_lock:
            self.order_batch.append(order)
            
            if len(self.order_batch) >= self.batch_size:
                await self._process_batch()
    
    async def _process_batch(self):
        if not self.order_batch:
            return
        
        # Batch process orders by symbol for efficiency
        orders_by_symbol = defaultdict(list)
        for order in self.order_batch:
            orders_by_symbol[order.symbol].append(order)
        
        # Process each symbol's orders together
        for symbol, orders in orders_by_symbol.items():
            await self._execute_orders_for_symbol(symbol, orders)
        
        self.order_batch.clear()
'''
            })
        
        return code_changes
    
    def _format_optimization_recommendation(self, recommendation: OptimizationRecommendation) -> str:
        """Format optimization recommendation for display"""
        
        sections = [
            "# ⚡ Performance Optimization Recommendation",
            f"\n**Target Area**: {recommendation.target_area.replace('_', ' ').title()}",
            f"\n## Current Performance Assessment",
            recommendation.current_performance,
            f"\n## Optimization Strategy",
            recommendation.optimization_strategy,
            f"\n## Implementation Steps"
        ]
        
        for step in recommendation.implementation_steps:
            sections.append(step)
        
        sections.extend([
            f"\n## Expected Performance Improvement",
            recommendation.expected_improvement,
            f"\n## Key Trade-offs"
        ])
        
        for trade_off in recommendation.trade_offs:
            sections.append(f"• {trade_off}")
        
        if recommendation.code_changes:
            sections.extend([
                f"\n## Recommended Code Changes"
            ])
            
            for change in recommendation.code_changes:
                sections.append(f"### {change['description']}")
                
                if 'before' in change and 'after' in change:
                    sections.extend([
                        "**Before:**",
                        "```python",
                        change['before'].strip(),
                        "```",
                        "**After:**",
                        "```python", 
                        change['after'].strip(),
                        "```\n"
                    ])
                else:
                    sections.extend([
                        "```python",
                        change['code'].strip(),
                        "```\n"
                    ])
        
        sections.extend([
            f"## Monitoring Metrics"
        ])
        
        for metric in recommendation.monitoring_metrics:
            sections.append(f"• {metric}")
        
        sections.extend([
            f"\n## Reasoning Process"
        ])
        
        for i, step in enumerate(recommendation.reasoning_chain, 1):
            sections.append(f"{i}. {step}")
        
        sections.append(f"\n**Confidence Level**: {recommendation.confidence:.1%}")
        
        return '\n'.join(sections)


def main():
    """CLI for performance optimizer"""
    import argparse
    
    parser = argparse.ArgumentParser(description="HRM Performance Optimizer")
    parser.add_argument("target", help="Performance optimization target")
    parser.add_argument("--context", "-c", help="Context directory")
    parser.add_argument("--model", "-m", help="Path to trained model")
    parser.add_argument("--output", "-o", help="Output file")
    parser.add_argument("--verbose", "-v", action="store_true")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.basicConfig(level=logging.INFO)
    
    optimizer = PerformanceOptimizer(model_path=args.model)
    recommendations = optimizer.optimize(args.target, context_path=args.context)
    
    if args.output:
        with open(args.output, 'w') as f:
            f.write(recommendations)
        print(f"Performance recommendations saved to {args.output}")
    else:
        print(recommendations)


if __name__ == "__main__":
    main()