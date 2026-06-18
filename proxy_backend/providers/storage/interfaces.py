"""
Storage Provider Abstractions.
"""
from abc import ABC, abstractmethod

class StorageProvider(ABC):
    """Abstract Base Class for Storage providers."""
    
    @abstractmethod
    async def upload_file(self, file_path: str, destination: str) -> str:
        """Upload file to storage."""
        pass
