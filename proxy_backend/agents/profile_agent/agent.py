"""
Profile Agent logic.
"""
from typing import Optional
from pathlib import Path
import logging

from proxy_backend.providers.llm.interfaces import LLMProvider
from .schemas import ProfileExtraction

logger = logging.getLogger(__name__)

class ProfileAgent:
    """Agent responsible for parsing resumes."""
    
    def __init__(self, llm_provider: LLMProvider) -> None:
        """Inject LLM Provider and load prompts."""
        self.llm_provider = llm_provider
        
        prompt_path = Path(__file__).resolve().parent.parent.parent / "prompts" / "profile_prompt.txt"
        if not prompt_path.exists():
            raise RuntimeError(f"Prompt file not found at {prompt_path}")
            
        with open(prompt_path, "r", encoding="utf-8") as f:
            self.prompt_template = f.read()
            
        if not self.prompt_template.strip():
            raise RuntimeError("Prompt file is empty.")
        
    async def extract_profile(
        self, 
        resume_text: str, 
        github_url: Optional[str] = None, 
        linkedin_url: Optional[str] = None
    ) -> ProfileExtraction:
        """Extract structured profile from raw text and URLs."""
        
        prompt = self.prompt_template.format(
            resume_text=resume_text,
            github_url=github_url or "None",
            linkedin_url=linkedin_url or "None"
        )
        
        return await self.llm_provider.extract_structured_data(
            prompt=prompt,
            schema=ProfileExtraction
        )
