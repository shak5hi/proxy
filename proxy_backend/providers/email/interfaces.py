"""
Email Provider Abstractions.
"""
from abc import ABC, abstractmethod

class EmailProvider(ABC):
    """Abstract Base Class for Email providers."""
    
    @abstractmethod
    async def send_email(self, to_address: str, subject: str, body: str) -> bool:
        """Send an email."""
        pass
