from sqlalchemy import Column, BigInteger, String, DateTime, Integer, Enum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from enum import Enum as PyEnum

Base = declarative_base()

class OutboxStatus(PyEnum):
    PENDING = "pending"
    PUBLISHED = "published"
    FAILED = "failed"

class EventOutbox(Base):
    __tablename__ = "event_outbox"
    
    id = Column(BigInteger, primary_key=True)
    aggregate_id = Column(String, nullable=False)
    event_type = Column(String, nullable=False)
    payload = Column(JSONB, nullable=False)
    status = Column(Enum(OutboxStatus), nullable=False, default=OutboxStatus.PENDING)
    priority = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)