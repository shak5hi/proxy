"""
Profile Agent logic.
"""
from typing import Optional
import os

from proxy_backend.providers.llm.interfaces import LLMProvider
from .schemas import ProfileExtraction

class ProfileAgent:
    """Agent responsible for parsing resumes."""
    
    def __init__(self, llm_provider: LLMProvider) -> None:
        """Inject LLM Provider."""
        self.llm_provider = llm_provider
        
    async def extract_profile(
        self, 
        resume_text: str, 
        github_url: Optional[str] = None, 
        linkedin_url: Optional[str] = None
    ) -> ProfileExtraction:
        """Extract structured profile from raw text and URLs."""
        
        # Load prompt
        # Assuming run from proxy_backend root.
        prompt_path = os.path.join(os.path.dirname(__file__), "../../prompts/profile_prompt.txt")
        try:
            with open(prompt_path, "r") as f:
                prompt_template = f.read()
        except FileNotFoundError:
            # Fallback
            prompt_template = "Extract data from resume: {resume_text}"
            
        prompt = prompt_template.format(
            resume_text=resume_text,
            github_url=github_url or "None",
            linkedin_url=linkedin_url or "None"
        )
        
        # Call LLM
        return await self.llm_provider.extract_structured_data(
            prompt=prompt,
            schema=ProfileExtraction
        )
