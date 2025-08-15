"""
Distributed Tracing System for AstraTrade

Implements OpenTelemetry-based distributed tracing across microservices
to track requests through the entire system and correlate business events.
"""

import time
import uuid
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
import logging
import asyncio
from contextlib import asynccontextmanager

logger = logging.getLogger("distributed-tracing")

try:
    from opentelemetry import trace
    from opentelemetry.exporter.jaeger.thrift import JaegerExporter
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
    from opentelemetry.instrumentation.requests import RequestsInstrumentor
    from opentelemetry.instrumentation.redis import RedisInstrumentor
    from opentelemetry.instrumentation.psycopg2 import Psycopg2Instrumentor
    OPENTELEMETRY_AVAILABLE = True
except ImportError:
    OPENTELEMETRY_AVAILABLE = False
    logger.warning("OpenTelemetry not available - using mock tracing implementation")


class SpanStatus(Enum):
    """Span status enumeration."""
    UNSET = "UNSET"
    OK = "OK"
    ERROR = "ERROR"


@dataclass
class TraceSpan:
    """Represents a single trace span."""
    span_id: str
    trace_id: str
    parent_span_id: Optional[str]
    operation_name: str
    service_name: str
    start_time: float
    end_time: Optional[float] = None
    status: SpanStatus = SpanStatus.UNSET
    tags: Dict[str, Any] = field(default_factory=dict)
    logs: List[Dict[str, Any]] = field(default_factory=list)
    
    @property
    def duration(self) -> Optional[float]:
        """Get span duration in seconds."""
        if self.end_time:
            return self.end_time - self.start_time
        return None
    
    def finish(self, status: SpanStatus = SpanStatus.OK):
        """Finish the span."""
        self.end_time = time.time()
        self.status = status
    
    def add_tag(self, key: str, value: Any):
        """Add a tag to the span."""
        self.tags[key] = value
    
    def add_log(self, message: str, level: str = "info", **kwargs):
        """Add a log entry to the span."""
        self.logs.append({
            "timestamp": time.time(),
            "level": level,
            "message": message,
            **kwargs
        })
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert span to dictionary for serialization."""
        return {
            "span_id": self.span_id,
            "trace_id": self.trace_id,
            "parent_span_id": self.parent_span_id,
            "operation_name": self.operation_name,
            "service_name": self.service_name,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration": self.duration,
            "status": self.status.value,
            "tags": self.tags,
            "logs": self.logs
        }


class DistributedTracer:
    """
    Distributed tracing implementation for AstraTrade microservices.
    
    Provides correlation tracking across service boundaries and
    business process monitoring capabilities.
    """
    
    def __init__(self, service_name: str, jaeger_endpoint: str = None):
        self.service_name = service_name
        self.jaeger_endpoint = jaeger_endpoint or "http://localhost:14268/api/traces"
        self.active_spans: Dict[str, TraceSpan] = {}
        self.completed_spans: List[TraceSpan] = []
        self.tracer = None
        
        # Business operation tracking
        self.business_traces: Dict[str, List[TraceSpan]] = {}
        
        # Initialize OpenTelemetry if available
        if OPENTELEMETRY_AVAILABLE:
            self._initialize_opentelemetry()
        else:
            logger.info("Using mock tracing implementation")
    
    def _initialize_opentelemetry(self):
        """Initialize OpenTelemetry tracing."""
        try:
            # Set up tracer provider
            trace.set_tracer_provider(TracerProvider())
            self.tracer = trace.get_tracer(self.service_name)
            
            # Set up Jaeger exporter
            jaeger_exporter = JaegerExporter(
                agent_host_name="localhost",
                agent_port=6831,
            )
            
            span_processor = BatchSpanProcessor(jaeger_exporter)
            trace.get_tracer_provider().add_span_processor(span_processor)
            
            logger.info(f"✅ OpenTelemetry initialized for {self.service_name}")
            
        except Exception as e:
            logger.error(f"Failed to initialize OpenTelemetry: {e}")
            self.tracer = None
    
    def start_span(
        self, 
        operation_name: str, 
        parent_span_id: str = None,
        trace_id: str = None,
        correlation_id: str = None,
        **tags
    ) -> TraceSpan:
        """Start a new trace span."""
        # Generate IDs
        span_id = str(uuid.uuid4())
        if not trace_id:
            trace_id = correlation_id or str(uuid.uuid4())
        
        # Create span
        span = TraceSpan(
            span_id=span_id,
            trace_id=trace_id,
            parent_span_id=parent_span_id,
            operation_name=operation_name,
            service_name=self.service_name,
            start_time=time.time()
        )
        
        # Add default tags
        span.add_tag("service.name", self.service_name)
        span.add_tag("correlation.id", correlation_id)
        
        # Add custom tags
        for key, value in tags.items():
            span.add_tag(key, value)
        
        # Store active span
        self.active_spans[span_id] = span
        
        # Add to business trace if correlation_id provided
        if correlation_id:
            if correlation_id not in self.business_traces:
                self.business_traces[correlation_id] = []
            self.business_traces[correlation_id].append(span)
        
        logger.debug(f"Started span: {operation_name} ({span_id})")
        return span
    
    def finish_span(self, span: TraceSpan, status: SpanStatus = SpanStatus.OK):
        """Finish a trace span."""
        span.finish(status)
        
        # Move from active to completed
        if span.span_id in self.active_spans:
            del self.active_spans[span.span_id]
        
        self.completed_spans.append(span)
        
        logger.debug(f"Finished span: {span.operation_name} ({span.span_id}) - {span.duration:.3f}s")
        
        # Send to OpenTelemetry if available
        if self.tracer and OPENTELEMETRY_AVAILABLE:
            self._send_to_opentelemetry(span)
    
    def _send_to_opentelemetry(self, span: TraceSpan):
        """Send span to OpenTelemetry tracer."""
        try:
            with self.tracer.start_as_current_span(span.operation_name) as otel_span:
                # Add attributes
                for key, value in span.tags.items():
                    otel_span.set_attribute(key, str(value))
                
                # Add logs as events
                for log in span.logs:
                    otel_span.add_event(log["message"], attributes={
                        "level": log["level"],
                        "timestamp": log["timestamp"]
                    })
                
                # Set status
                if span.status == SpanStatus.ERROR:
                    otel_span.set_status(trace.Status(trace.StatusCode.ERROR))
                else:
                    otel_span.set_status(trace.Status(trace.StatusCode.OK))
        
        except Exception as e:
            logger.error(f"Failed to send span to OpenTelemetry: {e}")
    
    @asynccontextmanager
    async def trace_operation(
        self, 
        operation_name: str,
        correlation_id: str = None,
        **tags
    ):
        """Context manager for tracing operations."""
        span = self.start_span(
            operation_name=operation_name,
            correlation_id=correlation_id,
            **tags
        )
        
        try:
            yield span
            self.finish_span(span, SpanStatus.OK)
        
        except Exception as e:
            span.add_tag("error", True)
            span.add_tag("error.message", str(e))
            span.add_log(f"Error occurred: {str(e)}", level="error")
            self.finish_span(span, SpanStatus.ERROR)
            raise
    
    def trace_business_operation(
        self, 
        operation_type: str, 
        correlation_id: str,
        user_id: str = None,
        **metadata
    ) -> TraceSpan:
        """Trace a business operation with enhanced metadata."""
        span = self.start_span(
            operation_name=f"business.{operation_type}",
            correlation_id=correlation_id,
            **{
                "business.operation": operation_type,
                "user.id": user_id,
                "business.timestamp": datetime.now(timezone.utc).isoformat(),
                **metadata
            }
        )
        
        return span
    
    def get_business_trace(self, correlation_id: str) -> List[TraceSpan]:
        """Get all spans for a business operation."""
        return self.business_traces.get(correlation_id, [])
    
    def get_trace_summary(self, correlation_id: str) -> Dict[str, Any]:
        """Get summary of a business trace."""
        spans = self.get_business_trace(correlation_id)
        
        if not spans:
            return {"correlation_id": correlation_id, "spans": 0, "services": []}
        
        services = list(set(span.service_name for span in spans))
        total_duration = sum(span.duration for span in spans if span.duration)
        error_count = len([span for span in spans if span.status == SpanStatus.ERROR])
        
        return {
            "correlation_id": correlation_id,
            "spans": len(spans),
            "services": services,
            "total_duration": total_duration,
            "error_count": error_count,
            "status": "error" if error_count > 0 else "success",
            "start_time": min(span.start_time for span in spans),
            "end_time": max(span.end_time for span in spans if span.end_time) or time.time()
        }
    
    def get_service_metrics(self) -> Dict[str, Any]:
        """Get tracing metrics for this service."""
        total_spans = len(self.completed_spans)
        error_spans = len([s for s in self.completed_spans if s.status == SpanStatus.ERROR])
        
        if self.completed_spans:
            avg_duration = sum(s.duration for s in self.completed_spans if s.duration) / len(self.completed_spans)
            operations = {}
            for span in self.completed_spans:
                op = span.operation_name
                if op not in operations:
                    operations[op] = {"count": 0, "total_duration": 0.0, "errors": 0}
                
                operations[op]["count"] += 1
                if span.duration:
                    operations[op]["total_duration"] += span.duration
                if span.status == SpanStatus.ERROR:
                    operations[op]["errors"] += 1
        else:
            avg_duration = 0.0
            operations = {}
        
        return {
            "service_name": self.service_name,
            "total_spans": total_spans,
            "error_spans": error_spans,
            "error_rate": error_spans / total_spans if total_spans > 0 else 0.0,
            "average_duration": avg_duration,
            "operations": operations,
            "active_spans": len(self.active_spans),
            "business_traces": len(self.business_traces)
        }
    
    def export_traces(self, correlation_id: str = None) -> List[Dict[str, Any]]:
        """Export traces for external analysis."""
        if correlation_id:
            spans = self.get_business_trace(correlation_id)
        else:
            spans = self.completed_spans
        
        return [span.to_dict() for span in spans]


# Global tracer registry
_tracers: Dict[str, DistributedTracer] = {}


def get_tracer(service_name: str) -> DistributedTracer:
    """Get or create a tracer for a service."""
    if service_name not in _tracers:
        _tracers[service_name] = DistributedTracer(service_name)
    
    return _tracers[service_name]


def initialize_tracing_for_fastapi(app, service_name: str):
    """Initialize distributed tracing for a FastAPI application."""
    tracer = get_tracer(service_name)
    
    if OPENTELEMETRY_AVAILABLE:
        # Instrument FastAPI automatically
        FastAPIInstrumentor.instrument_app(app)
        RequestsInstrumentor().instrument()
        
        logger.info(f"✅ FastAPI tracing instrumentation enabled for {service_name}")
    
    # Add manual tracing middleware
    @app.middleware("http")
    async def tracing_middleware(request, call_next):
        correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
        
        async with tracer.trace_operation(
            operation_name=f"{request.method} {request.url.path}",
            correlation_id=correlation_id,
            http_method=request.method,
            http_url=str(request.url),
            user_agent=request.headers.get("User-Agent", ""),
            remote_addr=request.client.host if request.client else ""
        ) as span:
            
            # Add request details
            span.add_tag("http.method", request.method)
            span.add_tag("http.url", str(request.url))
            span.add_tag("correlation.id", correlation_id)
            
            # Set correlation ID in request state
            request.state.correlation_id = correlation_id
            request.state.trace_span = span
            
            response = await call_next(request)
            
            # Add response details
            span.add_tag("http.status_code", response.status_code)
            
            # Add correlation ID to response
            response.headers["X-Correlation-ID"] = correlation_id
            response.headers["X-Trace-ID"] = span.trace_id
            
            return response
    
    return tracer


# Business operation decorators
def trace_business_operation(operation_type: str):
    """Decorator for tracing business operations."""
    def decorator(func):
        async def async_wrapper(*args, **kwargs):
            # Extract correlation_id from kwargs or args
            correlation_id = kwargs.get('correlation_id') or getattr(args[0], 'correlation_id', str(uuid.uuid4()))
            
            # Get service name from function module
            service_name = func.__module__.split('.')[0] if '.' in func.__module__ else 'unknown'
            tracer = get_tracer(service_name)
            
            async with tracer.trace_operation(
                operation_name=f"business.{operation_type}.{func.__name__}",
                correlation_id=correlation_id,
                business_operation=operation_type,
                function=func.__name__
            ) as span:
                span.add_tag("business.operation", operation_type)
                span.add_tag("function.name", func.__name__)
                
                result = await func(*args, **kwargs)
                
                # Add result metadata if available
                if isinstance(result, dict):
                    if 'success' in result:
                        span.add_tag("business.success", result['success'])
                    if 'data' in result and isinstance(result['data'], dict):
                        for key, value in result['data'].items():
                            if key in ['trade_id', 'user_id', 'amount', 'revenue']:
                                span.add_tag(f"business.{key}", value)
                
                return result
        
        def sync_wrapper(*args, **kwargs):
            # Similar implementation for sync functions
            return func(*args, **kwargs)
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    
    return decorator


# Convenience functions
def trace_database_operation(operation: str, table: str = None):
    """Trace database operations."""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            service_name = func.__module__.split('.')[0] if '.' in func.__module__ else 'unknown'
            tracer = get_tracer(service_name)
            
            correlation_id = kwargs.get('correlation_id') or str(uuid.uuid4())
            
            async with tracer.trace_operation(
                operation_name=f"db.{operation}",
                correlation_id=correlation_id,
                db_operation=operation,
                db_table=table
            ) as span:
                span.add_tag("db.operation", operation)
                if table:
                    span.add_tag("db.table", table)
                
                return await func(*args, **kwargs)
        
        return wrapper
    return decorator


def trace_external_api_call(api_name: str):
    """Trace external API calls."""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            service_name = func.__module__.split('.')[0] if '.' in func.__module__ else 'unknown'
            tracer = get_tracer(service_name)
            
            correlation_id = kwargs.get('correlation_id') or str(uuid.uuid4())
            
            async with tracer.trace_operation(
                operation_name=f"external.{api_name}",
                correlation_id=correlation_id,
                external_api=api_name
            ) as span:
                span.add_tag("external.api", api_name)
                
                return await func(*args, **kwargs)
        
        return wrapper
    return decorator


# Export functions for easy integration
__all__ = [
    'DistributedTracer',
    'TraceSpan',
    'SpanStatus',
    'get_tracer',
    'initialize_tracing_for_fastapi',
    'trace_business_operation',
    'trace_database_operation',
    'trace_external_api_call'
]


if __name__ == "__main__":
    # Example usage
    async def test_tracing():
        tracer = get_tracer("test-service")
        
        # Test business operation tracing
        async with tracer.trace_operation(
            "test_operation",
            correlation_id="test-123",
            user_id="user-456"
        ) as span:
            span.add_tag("test.data", "example")
            span.add_log("Starting test operation")
            
            await asyncio.sleep(0.1)  # Simulate work
            
            span.add_log("Test operation completed")
        
        # Get metrics
        metrics = tracer.get_service_metrics()
        print(f"Service metrics: {metrics}")
        
        # Get trace summary
        summary = tracer.get_trace_summary("test-123")
        print(f"Trace summary: {summary}")
    
    asyncio.run(test_tracing())