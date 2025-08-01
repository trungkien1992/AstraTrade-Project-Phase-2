"""
Repository Pattern Interfaces

Abstract repository interfaces for the domain layer.
Implements the Repository pattern to decouple domain logic from data persistence.

These interfaces will be implemented in the infrastructure layer with
specific database technologies (SQLAlchemy, MongoDB, etc.)
"""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional, List, Any, Dict

# Generic type for entity
T = TypeVar('T')


class Repository(Generic[T], ABC):
    """
    Generic repository interface for domain entities.
    
    Provides standard CRUD operations that can be implemented
    for any persistence technology.
    """
    
    @abstractmethod
    async def save(self, entity: T) -> T:
        """Persist an entity and return the saved version."""
        pass
    
    @abstractmethod
    async def get_by_id(self, entity_id: Any) -> Optional[T]:
        """Retrieve an entity by its identifier."""
        pass
    
    @abstractmethod
    async def exists(self, entity_id: Any) -> bool:
        """Check if an entity exists by its identifier."""
        pass
    
    @abstractmethod
    async def delete(self, entity_id: Any) -> bool:
        """Delete an entity by its identifier. Returns True if deleted."""
        pass
    
    @abstractmethod
    async def list_all(self, limit: Optional[int] = None, offset: int = 0) -> List[T]:
        """List all entities with optional pagination."""
        pass
    
    @abstractmethod
    async def count(self) -> int:
        """Count total number of entities."""
        pass


class QueryableRepository(Repository[T], ABC):
    """
    Extended repository interface with querying capabilities.
    
    Provides additional methods for complex queries while maintaining
    domain-focused abstractions.
    """
    
    @abstractmethod
    async def find_by_criteria(
        self, 
        criteria: Dict[str, Any], 
        limit: Optional[int] = None,
        offset: int = 0
    ) -> List[T]:
        """Find entities matching the given criteria."""
        pass
    
    @abstractmethod
    async def find_one_by_criteria(self, criteria: Dict[str, Any]) -> Optional[T]:
        """Find a single entity matching the given criteria."""
        pass
    
    @abstractmethod
    async def count_by_criteria(self, criteria: Dict[str, Any]) -> int:
        """Count entities matching the given criteria."""
        pass


class UnitOfWork(ABC):
    """
    Unit of Work pattern interface for managing transactions.
    
    Ensures that all changes within a business transaction
    are committed or rolled back together.
    """
    
    @abstractmethod
    async def __aenter__(self):
        """Enter the async context manager."""
        pass
    
    @abstractmethod
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit the async context manager."""
        pass
    
    @abstractmethod
    async def commit(self) -> None:
        """Commit all changes in the unit of work."""
        pass
    
    @abstractmethod
    async def rollback(self) -> None:
        """Rollback all changes in the unit of work."""
        pass