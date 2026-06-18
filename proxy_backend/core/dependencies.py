"""
Centralized FastAPI dependencies.
No external DI containers; native FastAPI Depends() only.
"""
from typing import Any

from proxy_backend.shared.pdf.interfaces import PDFParser
from proxy_backend.shared.pdf.pdf_parser import PyPDFParser
from proxy_backend.providers.llm.interfaces import LLMProvider
from proxy_backend.providers.llm.gemini_provider import GeminiProvider
from proxy_backend.agents.profile_agent.agent import ProfileAgent
from proxy_backend.domains.profile.repositories import AbstractProfileRepository, ProfileRepository
from proxy_backend.domains.profile.services import ProfileService

def get_supabase_client() -> Any:
    """Mock dependency to retrieve Supabase client."""
    class MockSupabase:
        def table(self, name): return self
        def insert(self, data): return self
        def execute(self): 
            class Result: data = [{"id": "123", **data}]
            return Result()
    return MockSupabase()

def get_pdf_parser() -> PDFParser:
    """Dependency to inject PDF Parser."""
    return PyPDFParser()

def get_llm_provider() -> LLMProvider:
    """Dependency to inject the LLM Provider."""
    return GeminiProvider()

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
