"""
Event Bus Abstraction.
Prepares for future Redis pub/sub migration.
"""
from abc import ABC, abstractmethod
from typing import Any

class EventBus(ABC):
    """Abstract Base Class for Event Bus."""
    
    @abstractmethod
    async def publish(self, topic: str, event: Any) -> None:
        """Publish an event to a topic."""
        pass
        
    @abstractmethod
    async def subscribe(self, topic: str, handler: Any) -> None:
        """Subscribe to a topic with a handler."""
        pass
