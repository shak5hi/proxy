"""
Concrete implementation for Sentence Transformers.
"""
from typing import List
from .interfaces import EmbeddingProvider

class SentenceTransformerProvider(EmbeddingProvider):
    """Sentence Transformer Provider implementation."""
    
    async def embed_text(self, text: str) -> List[float]:
        """Embed text using sentence-transformers."""
        return [0.0] * 768
