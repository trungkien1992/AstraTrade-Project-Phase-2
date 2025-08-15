"""
Base package for AstraTrade microservices.
Provides common functionality and utilities.
"""

from .config import config, ServiceConfig
from .health import health_checker, setup_health_checker
from .metrics import metrics_collector, track_database_operation, track_redis_operation
from .dependencies import (
    database_manager, 
    redis_manager, 
    event_bus_manager,
    get_database_session,
    get_redis_client,
    get_event_bus,
    initialize_dependencies,
    cleanup_dependencies
)
from .main_template import create_app, register_with_api_gateway, start_heartbeat

__all__ = [
    "config",
    "ServiceConfig", 
    "health_checker",
    "setup_health_checker",
    "metrics_collector",
    "track_database_operation",
    "track_redis_operation",
    "database_manager",
    "redis_manager", 
    "event_bus_manager",
    "get_database_session",
    "get_redis_client",
    "get_event_bus",
    "initialize_dependencies",
    "cleanup_dependencies",
    "create_app",
    "register_with_api_gateway", 
    "start_heartbeat"
]