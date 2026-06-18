"""
Centralized FastAPI dependencies.
No external DI containers; native FastAPI Depends() only.
"""
from typing import Any
from fastapi import Depends
from supabase import create_client, Client
import logging

from proxy_backend.core.config import Settings
from proxy_backend.shared.pdf.interfaces import PDFParser
from proxy_backend.shared.pdf.pdf_parser import PyPDFParser
from proxy_backend.providers.llm.interfaces import LLMProvider
from proxy_backend.providers.llm.gemini_provider import GeminiProvider
from proxy_backend.agents.profile_agent.agent import ProfileAgent
from proxy_backend.domains.profile.repositories import AbstractProfileRepository, ProfileRepository
from proxy_backend.domains.profile.services import ProfileService

logger = logging.getLogger(__name__)

def get_settings() -> Settings:
    """Dependency to retrieve application settings."""
    return Settings()

def get_supabase_client(settings: Settings = Depends(get_settings)) -> Client:
    """Dependency to retrieve Supabase client."""
    if not settings.supabase_url or not settings.supabase_key:
        logger.warning("Supabase URL or Key not set. Returning a mock client for compilation.")
        class MockSupabase:
            def table(self, name): return self
            def insert(self, data): return self
            def execute(self): 
                class Result: data = [{"id": "123", **data}]
                return Result()
        return MockSupabase()
    return create_client(settings.supabase_url, settings.supabase_key)

def get_pdf_parser() -> PDFParser:
    """Dependency to inject PDF Parser."""
    return PyPDFParser()

def get_llm_provider(settings: Settings = Depends(get_settings)) -> LLMProvider:
    """Dependency to inject the LLM Provider."""
    return GeminiProvider(api_key=settings.gemini_api_key)

def get_profile_repository(supabase_client: Any = Depends(get_supabase_client)) -> AbstractProfileRepository:
    """Dependency to inject Profile Repository."""
    return ProfileRepository(supabase_client=supabase_client)

def get_profile_agent(llm_provider: LLMProvider = Depends(get_llm_provider)) -> ProfileAgent:
    """Dependency to inject Profile Agent."""
    return ProfileAgent(llm_provider=llm_provider)

def get_profile_service(
    pdf_parser: PDFParser = Depends(get_pdf_parser),
    profile_agent: ProfileAgent = Depends(get_profile_agent),
    repository: AbstractProfileRepository = Depends(get_profile_repository)
) -> ProfileService:
    """Dependency to inject Profile Service."""
    return ProfileService(
        pdf_parser=pdf_parser,
        profile_agent=profile_agent,
        repository=repository
    )
