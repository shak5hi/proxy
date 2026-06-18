"""
LLM Provider Abstractions.
"""
from abc import ABC, abstractmethod
from typing import Type, TypeVar
from pydantic import BaseModel

T = TypeVar('T', bound=BaseModel)

class LLMProvider(ABC):
    """Abstract Base Class for LLM providers."""
    
    @abstractmethod
    async def generate_text(self, prompt: str) -> str:
        """Generate raw text from a prompt."""
        pass
        
    @abstractmethod
    async def extract_structured_data(self, prompt: str, schema: Type[T]) -> T:
        """Extract structured output according to a Pydantic schema."""
        pass
