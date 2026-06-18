"""
Concrete implementation for Gemini LLM.
"""
from typing import Type, TypeVar
from pydantic import BaseModel
import logging
from google import genai
from google.genai import types

from .interfaces import LLMProvider

logger = logging.getLogger(__name__)
T = TypeVar('T', bound=BaseModel)

class GeminiProvider(LLMProvider):
    """Gemini Provider implementation."""
    
    def __init__(self, api_key: str):
        """Initialize the Gemini client."""
        if not api_key:
            logger.warning("Gemini API key is not set. Provider calls will fail.")
        self.client = genai.Client(api_key=api_key)
    
    async def generate_text(self, prompt: str) -> str:
        """Generate raw text using Google's Gemini."""
        response = self.client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        return response.text
        
    async def extract_structured_data(self, prompt: str, schema: Type[T]) -> T:
        """Use Gemini's structured output features to return a validated Pydantic model."""
        response = self.client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=schema,
            ),
        )
        # response.parsed should be available if structured outputs are used
        if response.parsed:
             return response.parsed
        # Fallback to manual validation if needed
        return schema.model_validate_json(response.text)
