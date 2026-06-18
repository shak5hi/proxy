"""
Embedding Provider Abstractions.
"""
from abc import ABC, abstractmethod
from typing import List

class EmbeddingProvider(ABC):
    """Abstract Base Class for Embedding providers."""
    
    @abstractmethod
    async def embed_text(self, text: str) -> List[float]:
        """Convert text into vector embeddings."""
        pass
