"""
Vector Store Provider Abstractions.
"""
from abc import ABC, abstractmethod
from typing import List, Any

class VectorStoreProvider(ABC):
    """Abstract Base Class for Vector Store providers."""
    
    @abstractmethod
    async def search(self, embedding: List[float], limit: int = 5) -> List[Any]:
        """Search vector database."""
        pass
