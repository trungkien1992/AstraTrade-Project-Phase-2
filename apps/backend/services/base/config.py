"""
Base configuration for AstraTrade microservices.
Environment-based configuration management.
"""

import os
from typing import Optional
from dataclasses import dataclass, field


@dataclass
class ServiceConfig:
    """Base configuration for all microservices."""
    
    # Service identification
    service_name: str = os.getenv("SERVICE_NAME", "unknown")
    service_version: str = os.getenv("SERVICE_VERSION", "1.0.0")
    service_port: int = int(os.getenv("SERVICE_PORT", "8000"))
    service_host: str = os.getenv("SERVICE_HOST", "0.0.0.0")
    
    # Environment
    environment: str = os.getenv("ENVIRONMENT", "development")
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Database configuration
    database_url: str = os.getenv("DATABASE_URL", "postgresql://localhost:5432/astradb")
    db_pool_size: int = int(os.getenv("DB_POOL_SIZE", "5"))
    db_max_overflow: int = int(os.getenv("DB_MAX_OVERFLOW", "10"))
    db_pool_recycle: int = int(os.getenv("DB_POOL_RECYCLE", "3600"))
    db_pool_pre_ping: bool = os.getenv("DB_POOL_PRE_PING", "true").lower() == "true"
    
    # Redis configuration
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    redis_pool_size: int = int(os.getenv("REDIS_POOL_SIZE", "10"))
    redis_retry_attempts: int = int(os.getenv("REDIS_RETRY_ATTEMPTS", "3"))
    
    # API Gateway configuration
    api_gateway_url: str = os.getenv("API_GATEWAY_URL", "http://localhost:8000")
    service_registry_url: str = os.getenv("SERVICE_REGISTRY_URL", "redis://localhost:6379")
    
    # Security
    service_token: Optional[str] = os.getenv("SERVICE_TOKEN")
    cors_origins: list = field(default_factory=lambda: os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:8000").split(","))
    
    # Monitoring
    metrics_enabled: bool = os.getenv("METRICS_ENABLED", "true").lower() == "true"
    health_check_interval: int = int(os.getenv("HEALTH_CHECK_INTERVAL", "30"))
    
    # Resource limits
    max_connections: int = int(os.getenv("MAX_CONNECTIONS", "100"))
    request_timeout: int = int(os.getenv("REQUEST_TIMEOUT", "30"))
    
    def get_container_id(self) -> str:
        """Get container ID for service identification."""
        # Try to get from hostname (Docker sets this)
        hostname = os.getenv("HOSTNAME", "")
        if hostname:
            return hostname[:12]  # First 12 chars like Docker
        
        # Fallback to service name with random suffix
        import uuid
        return f"{self.service_name}-{uuid.uuid4().hex[:8]}"
    
    def get_database_config(self) -> dict:
        """Get SQLAlchemy database configuration."""
        return {
            "url": self.database_url,
            "pool_size": self.db_pool_size,
            "max_overflow": self.db_max_overflow,
            "pool_recycle": self.db_pool_recycle,
            "pool_pre_ping": self.db_pool_pre_ping,
            "echo": self.debug
        }
    
    def get_redis_config(self) -> dict:
        """Get Redis connection configuration."""
        return {
            "url": self.redis_url,
            "retry_on_timeout": True,
            "health_check_interval": 30,
            "max_connections": self.redis_pool_size
        }


# Global configuration instance
config = ServiceConfig()