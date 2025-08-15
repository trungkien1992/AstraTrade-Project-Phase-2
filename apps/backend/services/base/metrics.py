"""
Prometheus metrics for AstraTrade microservices.
Provides consistent metrics collection across all services.
"""

import time
from typing import Dict, Any
from functools import wraps
from fastapi import Request, Response
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
import prometheus_client

from .config import config

# Clear default registry to avoid conflicts
prometheus_client.REGISTRY._collector_to_names.clear()
prometheus_client.REGISTRY._names_to_collectors.clear()

# HTTP Metrics
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status_code', 'service']
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint', 'service'],
    buckets=[0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
)

http_requests_in_progress = Gauge(
    'http_requests_in_progress',
    'HTTP requests currently being processed',
    ['method', 'endpoint', 'service']
)

# Database Metrics
database_connections_active = Gauge(
    'database_connections_active',
    'Active database connections',
    ['service']
)

database_query_duration_seconds = Histogram(
    'database_query_duration_seconds',
    'Database query duration in seconds',
    ['operation', 'service'],
    buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0]
)

database_queries_total = Counter(
    'database_queries_total',
    'Total database queries',
    ['operation', 'status', 'service']
)

# Redis Metrics
redis_operations_total = Counter(
    'redis_operations_total',
    'Total Redis operations',
    ['operation', 'status', 'service']
)

redis_operation_duration_seconds = Histogram(
    'redis_operation_duration_seconds',
    'Redis operation duration in seconds',
    ['operation', 'service'],
    buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5]
)

# Event Bus Metrics
events_published_total = Counter(
    'events_published_total',
    'Total events published',
    ['event_type', 'stream', 'service']
)

events_consumed_total = Counter(
    'events_consumed_total',
    'Total events consumed',
    ['event_type', 'stream', 'consumer_group', 'service']
)

event_processing_duration_seconds = Histogram(
    'event_processing_duration_seconds',
    'Event processing duration in seconds',
    ['event_type', 'service'],
    buckets=[0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0]
)

events_failed_total = Counter(
    'events_failed_total',
    'Total failed event processing',
    ['event_type', 'error_type', 'service']
)

# Service Health Metrics
service_health_status = Gauge(
    'service_health_status',
    'Service health status (1=healthy, 0=unhealthy)',
    ['service', 'dependency']
)

service_uptime_seconds = Gauge(
    'service_uptime_seconds',
    'Service uptime in seconds',
    ['service']
)

# Business Metrics (can be extended per service)
business_operations_total = Counter(
    'business_operations_total',
    'Total business operations',
    ['operation_type', 'status', 'service']
)


class MetricsCollector:
    """Centralized metrics collection for microservices."""
    
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.start_time = time.time()
    
    def record_http_request(self, method: str, endpoint: str, status_code: int, duration: float):
        """Record HTTP request metrics."""
        http_requests_total.labels(
            method=method,
            endpoint=endpoint,
            status_code=status_code,
            service=self.service_name
        ).inc()
        
        http_request_duration_seconds.labels(
            method=method,
            endpoint=endpoint,
            service=self.service_name
        ).observe(duration)
    
    def record_database_query(self, operation: str, duration: float, success: bool = True):
        """Record database query metrics."""
        status = "success" if success else "error"
        
        database_queries_total.labels(
            operation=operation,
            status=status,
            service=self.service_name
        ).inc()
        
        database_query_duration_seconds.labels(
            operation=operation,
            service=self.service_name
        ).observe(duration)
    
    def record_redis_operation(self, operation: str, duration: float, success: bool = True):
        """Record Redis operation metrics."""
        status = "success" if success else "error"
        
        redis_operations_total.labels(
            operation=operation,
            status=status,
            service=self.service_name
        ).inc()
        
        redis_operation_duration_seconds.labels(
            operation=operation,
            service=self.service_name
        ).observe(duration)
    
    def record_event_published(self, event_type: str, stream: str):
        """Record event publication metrics."""
        events_published_total.labels(
            event_type=event_type,
            stream=stream,
            service=self.service_name
        ).inc()
    
    def record_event_consumed(self, event_type: str, stream: str, consumer_group: str, 
                            duration: float, success: bool = True):
        """Record event consumption metrics."""
        events_consumed_total.labels(
            event_type=event_type,
            stream=stream,
            consumer_group=consumer_group,
            service=self.service_name
        ).inc()
        
        event_processing_duration_seconds.labels(
            event_type=event_type,
            service=self.service_name
        ).observe(duration)
        
        if not success:
            events_failed_total.labels(
                event_type=event_type,
                error_type="processing_error",
                service=self.service_name
            ).inc()
    
    def record_health_status(self, dependency: str, is_healthy: bool):
        """Record service health status."""
        service_health_status.labels(
            service=self.service_name,
            dependency=dependency
        ).set(1 if is_healthy else 0)
    
    def update_uptime(self):
        """Update service uptime metric."""
        uptime = time.time() - self.start_time
        service_uptime_seconds.labels(service=self.service_name).set(uptime)
    
    def record_business_operation(self, operation_type: str, success: bool = True):
        """Record business operation metrics."""
        status = "success" if success else "error"
        business_operations_total.labels(
            operation_type=operation_type,
            status=status,
            service=self.service_name
        ).inc()


# Global metrics collector
metrics_collector = MetricsCollector(config.service_name)


def track_http_requests():
    """Middleware to track HTTP requests."""
    async def middleware(request: Request, call_next):
        if not config.metrics_enabled:
            return await call_next(request)
        
        # Skip metrics endpoint itself
        if request.url.path == "/metrics":
            return await call_next(request)
        
        method = request.method
        endpoint = request.url.path
        
        # Track request in progress
        http_requests_in_progress.labels(
            method=method,
            endpoint=endpoint,
            service=config.service_name
        ).inc()
        
        start_time = time.time()
        
        try:
            response = await call_next(request)
            duration = time.time() - start_time
            
            # Record successful request
            metrics_collector.record_http_request(
                method=method,
                endpoint=endpoint,
                status_code=response.status_code,
                duration=duration
            )
            
            return response
            
        except Exception as e:
            duration = time.time() - start_time
            
            # Record failed request
            metrics_collector.record_http_request(
                method=method,
                endpoint=endpoint,
                status_code=500,
                duration=duration
            )
            
            raise
        
        finally:
            # Decrement in-progress counter
            http_requests_in_progress.labels(
                method=method,
                endpoint=endpoint,
                service=config.service_name
            ).dec()
    
    return middleware


def track_database_operation(operation: str):
    """Decorator to track database operations."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            if not config.metrics_enabled:
                return await func(*args, **kwargs)
            
            start_time = time.time()
            success = True
            
            try:
                result = await func(*args, **kwargs)
                return result
            except Exception:
                success = False
                raise
            finally:
                duration = time.time() - start_time
                metrics_collector.record_database_query(operation, duration, success)
        
        return wrapper
    return decorator


def track_redis_operation(operation: str):
    """Decorator to track Redis operations."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            if not config.metrics_enabled:
                return await func(*args, **kwargs)
            
            start_time = time.time()
            success = True
            
            try:
                result = await func(*args, **kwargs)
                return result
            except Exception:
                success = False
                raise
            finally:
                duration = time.time() - start_time
                metrics_collector.record_redis_operation(operation, duration, success)
        
        return wrapper
    return decorator


async def metrics_endpoint():
    """Prometheus metrics endpoint."""
    if not config.metrics_enabled:
        return Response(content="Metrics disabled", status_code=404)
    
    # Update uptime before generating metrics
    metrics_collector.update_uptime()
    
    # Generate metrics in Prometheus format
    metrics_data = generate_latest()
    
    return Response(
        content=metrics_data,
        media_type=CONTENT_TYPE_LATEST
    )