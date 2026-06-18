"""
Concrete implementation for Supabase pgvector.
"""
from typing import List, Any
from .interfaces import VectorStoreProvider

class SupabaseVectorProvider(VectorStoreProvider):
    """Supabase Vector Store Provider implementation."""
    
    async def search(self, embedding: List[float], limit: int = 5) -> List[Any]:
        """Search pgvector in Supabase."""
        return []
