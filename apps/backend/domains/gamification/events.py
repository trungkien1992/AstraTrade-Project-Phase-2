from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any


@dataclass
class DomainEvent:
    """Simple domain event for gamification domain"""
    event_type: str
    entity_id: str
    data: Dict[str, Any]
    occurred_at: datetime = None
    
    def __post_init__(self):
        if self.occurred_at is None:
            self.occurred_at = datetime.utcnow()