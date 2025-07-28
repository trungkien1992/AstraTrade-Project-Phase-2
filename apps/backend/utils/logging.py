import logging
import json
from datetime import datetime
from typing import Dict, Any, Optional


class StructuredLogger:
    """Structured logging for FastAPI applications"""
    
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.logger = logging.getLogger(service_name)
        
        # Configure logging
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
    
    def log_structured(self, level: str, event: str, message: str, **kwargs):
        """Log structured data"""
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "service": self.service_name,
            "event": event,
            "message": message,
            **kwargs
        }
        
        log_message = json.dumps(log_data)
        
        if level.upper() == "ERROR":
            self.logger.error(log_message)
        elif level.upper() == "WARNING":
            self.logger.warning(log_message)
        elif level.upper() == "DEBUG":
            self.logger.debug(log_message)
        else:
            self.logger.info(log_message)
    
    def log_api_call(self, endpoint: str, method: str, status_code: int, duration_ms: float, **kwargs):
        """Log API call information"""
        self.log_structured(
            level="INFO",
            event="api_call",
            message=f"{method} {endpoint} - {status_code}",
            endpoint=endpoint,
            method=method,
            status_code=status_code,
            duration_ms=duration_ms,
            **kwargs
        )
    
    def error(self, message: str, **kwargs):
        """Log error message"""
        self.log_structured("ERROR", "error", message, **kwargs)
    
    def info(self, message: str, **kwargs):
        """Log info message"""
        self.log_structured("INFO", "info", message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message"""
        self.log_structured("WARNING", "warning", message, **kwargs)
    
    def debug(self, message: str, **kwargs):
        """Log debug message"""
        self.log_structured("DEBUG", "debug", message, **kwargs)