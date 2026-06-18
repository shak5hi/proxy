"""
LLM Provider Abstractions.
"""
from abc import ABC, abstractmethod

class LLMProvider(ABC):
    """Abstract Base Class for LLM providers."""
    
    @abstractmethod
    async def generate_text(self, prompt: str) -> str:
        """Generate text from a prompt."""
        pass
