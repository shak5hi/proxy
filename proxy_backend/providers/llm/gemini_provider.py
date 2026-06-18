"""
Concrete implementation for Gemini LLM.
"""
from .interfaces import LLMProvider

class GeminiProvider(LLMProvider):
    """Gemini Provider implementation."""
    
    async def generate_text(self, prompt: str) -> str:
        """Generate text using Google's Gemini."""
        return "Generated text from Gemini."
