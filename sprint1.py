import os
from pathlib import Path

BACKEND_DIR = Path("C:/Users/shaks/OneDrive/Desktop/Projects/proxy/proxy/proxy_backend")

def write_file(rel_path: str, content: str):
    path = BACKEND_DIR / rel_path
    if not path.parent.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")

# 1. shared/pdf/
write_file("shared/pdf/__init__.py", "")
write_file("shared/pdf/exceptions.py", '''"""
Exceptions for PDF Parsing.
"""

class PDFParsingException(Exception):
    """Raised when PDF parsing fails."""
    pass
''')

write_file("shared/pdf/interfaces.py", '''"""
Interface for PDF Parsers.
"""
from abc import ABC, abstractmethod
from typing import BinaryIO

class PDFParser(ABC):
    """Abstract Base Class for extracting text from PDFs."""
    
    @abstractmethod
    def extract_text(self, file_stream: BinaryIO) -> str:
        """Extract text from a binary PDF stream."""
        pass
''')

write_file("shared/pdf/pdf_parser.py", '''"""
Concrete implementation of PDFParser using pypdf.
"""
from typing import BinaryIO
from pypdf import PdfReader
import logging

from .interfaces import PDFParser
from .exceptions import PDFParsingException

logger = logging.getLogger(__name__)

class PyPDFParser(PDFParser):
    """Implementation using PyPDF."""
    
    def extract_text(self, file_stream: BinaryIO) -> str:
        """Extract text from a PDF file stream."""
        try:
            reader = PdfReader(file_stream)
            text = []
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text.append(page_text)
            return "\\n".join(text)
        except Exception as e:
            logger.error(f"Failed to parse PDF: {e}")
            raise PDFParsingException(f"Failed to parse PDF: {e}")
''')

# 2. domains/profile/
write_file("domains/profile/exceptions.py", '''"""
Exceptions for the Profile Domain.
"""

class ProfileNotFoundException(Exception):
    """Raised when a profile cannot be found in the database."""
    pass

class ProfileExtractionException(Exception):
    """Raised when the agent fails to extract a profile from the provided text."""
    pass

class InvalidResumeException(Exception):
    """Raised when the uploaded resume is invalid or unreadable."""
    pass
''')

write_file("domains/profile/schemas.py", '''"""
Schemas for the Profile Domain.
"""
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, HttpUrl, ConfigDict

class ExperienceLevelEnum(str, Enum):
    JUNIOR = "junior"
    MID = "mid"
    SENIOR = "senior"
    STAFF = "staff"
    PRINCIPAL = "principal"

class ProfileUploadRequest(BaseModel):
    """Request schema for uploading a resume. 
    Note: resume_file is handled via FastAPI UploadFile, not included here.
    """
    github_url: Optional[HttpUrl] = None
    linkedin_url: Optional[HttpUrl] = None
    
    model_config = ConfigDict(from_attributes=True)

class ProfileExtraction(BaseModel):
    """Internal schema for extracted structured data from LLM."""
    skills: List[str]
    tech_stack: List[str]
    projects: List[str]
    experience_level: ExperienceLevelEnum
    preferred_roles: List[str]

class ProfileResponse(BaseModel):
    """Response schema sent to the client."""
    id: str
    skills: List[str]
    tech_stack: List[str]
    projects: List[str]
    experience_level: ExperienceLevelEnum
    preferred_roles: List[str]
    
    model_config = ConfigDict(from_attributes=True)
''')

write_file("domains/profile/repositories.py", '''"""
Repository for the Profile Domain.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class AbstractProfileRepository(ABC):
    """Interface for Profile Repository."""
    
    @abstractmethod
    async def save_profile(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Save a new profile to the database."""
        pass

class ProfileRepository(AbstractProfileRepository):
    """Concrete implementation for Supabase."""
    
    def __init__(self, supabase_client: Any) -> None:
        """Inject the Supabase client."""
        self.supabase = supabase_client
        
    async def save_profile(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Insert profile into Supabase profiles table."""
        try:
            # Using real supabase-py commands
            result = self.supabase.table("profiles").insert(profile_data).execute()
            if not result.data:
                raise Exception("Insert returned no data.")
            return result.data[0]
        except Exception as e:
            logger.error(f"Database error while saving profile: {e}")
            raise Exception(f"Failed to save profile: {e}")
''')

write_file("domains/profile/services.py", '''"""
Service Layer for the Profile Domain.
Orchestrates parsing, agent extraction, and saving.
"""
import logging
from typing import Optional

from .schemas import ProfileResponse, ProfileExtraction
from .exceptions import ProfileExtractionException, InvalidResumeException
from .repositories import AbstractProfileRepository
from proxy_backend.agents.profile_agent.agent import ProfileAgent
from proxy_backend.shared.pdf.interfaces import PDFParser
from proxy_backend.shared.pdf.exceptions import PDFParsingException

logger = logging.getLogger(__name__)

class ProfileService:
    """Orchestrator for Profile logic."""
    
    def __init__(
        self, 
        pdf_parser: PDFParser, 
        profile_agent: ProfileAgent, 
        repository: AbstractProfileRepository
    ) -> None:
        """Constructor injection of all required dependencies."""
        self.pdf_parser = pdf_parser
        self.profile_agent = profile_agent
        self.repository = repository

    async def process_upload(
        self, 
        file_stream, 
        github_url: Optional[str] = None, 
        linkedin_url: Optional[str] = None
    ) -> ProfileResponse:
        """
        Process the uploaded resume and optional URLs to extract and save a profile.
        """
        logger.info("upload started")
        
        # 1. Parse PDF
        try:
            resume_text = self.pdf_parser.extract_text(file_stream)
            if not resume_text.strip():
                raise InvalidResumeException("Parsed resume text is empty.")
        except PDFParsingException as e:
            logger.error(f"PDF Parsing failed: {e}")
            raise InvalidResumeException(f"Invalid resume file: {e}")
            
        # 2. Agent Extraction
        logger.info("profile extraction started")
        try:
            extraction: ProfileExtraction = await self.profile_agent.extract_profile(resume_text, github_url, linkedin_url)
        except Exception as e:
            logger.error(f"Agent extraction failed: {e}")
            raise ProfileExtractionException(f"Could not extract profile: {e}")
            
        logger.info("profile extraction completed")
        
        # 3. Save to Repository
        profile_data = {
            "skills": extraction.skills,
            "tech_stack": extraction.tech_stack,
            "projects": extraction.projects,
            "experience_level": extraction.experience_level.value,
            "preferred_roles": extraction.preferred_roles,
            "github_url": github_url,
            "linkedin_url": linkedin_url
        }
        
        saved_record = await self.repository.save_profile(profile_data)
        logger.info("database save completed")
        
        # 4. Return Response
        return ProfileResponse(
            id=str(saved_record.get("id")),
            skills=saved_record.get("skills", []),
            tech_stack=saved_record.get("tech_stack", []),
            projects=saved_record.get("projects", []),
            experience_level=saved_record.get("experience_level"),
            preferred_roles=saved_record.get("preferred_roles", [])
        )
''')

# 3. agents/profile_agent/
write_file("agents/profile_agent/schemas.py", '''"""
Schemas for Profile Agent.
Exports from the domain to keep agent separated.
"""
from proxy_backend.domains.profile.schemas import ProfileExtraction
''')

write_file("prompts/profile_prompt.txt", '''Extract the following structured information from the provided resume:
- Skills
- Tech Stack
- Projects
- Experience Level (JUNIOR, MID, SENIOR, STAFF, PRINCIPAL)
- Preferred Roles

Resume Text:
{resume_text}

GitHub URL: {github_url}
LinkedIn URL: {linkedin_url}

Return strictly structured data conforming to the required JSON schema.
''')

write_file("agents/profile_agent/agent.py", '''"""
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
''')

# 4. providers/llm/
write_file("providers/llm/interfaces.py", '''"""
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
''')

write_file("providers/llm/gemini_provider.py", '''"""
Concrete implementation for Gemini LLM.
"""
from typing import Type, TypeVar
from pydantic import BaseModel
import logging

from .interfaces import LLMProvider

logger = logging.getLogger(__name__)
T = TypeVar('T', bound=BaseModel)

class GeminiProvider(LLMProvider):
    """Gemini Provider implementation."""
    
    def __init__(self):
        # We would initialize the google genai client here
        pass
    
    async def generate_text(self, prompt: str) -> str:
        """Generate raw text using Google's Gemini."""
        return "Generated text from Gemini."
        
    async def extract_structured_data(self, prompt: str, schema: Type[T]) -> T:
        """
        Use Gemini's structured output features.
        Mock implementation for compilation, but interface strictly follows rules.
        In a real scenario, use google.genai sdk with response_schema.
        """
        # Pseudo-implementation
        # response = client.generate_content(prompt, config=GenerateContentConfig(response_schema=schema))
        # return schema.model_validate(response.parsed)
        raise NotImplementedError("Real implementation requires google-genai package setup.")
''')

# 5. API Layer
write_file("api/profile.py", '''"""
Profile API Router.
Thin controller containing no business logic.
"""
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from typing import Optional
import logging

from proxy_backend.domains.profile.services import ProfileService
from proxy_backend.domains.profile.schemas import ProfileResponse
from proxy_backend.domains.profile.exceptions import InvalidResumeException, ProfileExtractionException
from proxy_backend.core.dependencies import get_profile_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/profile", tags=["profile"])

@router.post("/upload", response_model=ProfileResponse)
async def upload_profile(
    resume: UploadFile = File(...),
    github_url: Optional[str] = Form(None),
    linkedin_url: Optional[str] = Form(None),
    profile_service: ProfileService = Depends(get_profile_service)
):
    """
    Upload a resume and optional URLs to extract a structured profile.
    """
    if not resume.filename.endswith('.pdf'):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only PDF resumes are supported.")
        
    try:
        # File.file is a SpooledTemporaryFile which acts as BinaryIO
        response = await profile_service.process_upload(
            file_stream=resume.file,
            github_url=github_url,
            linkedin_url=linkedin_url
        )
        return response
    except InvalidResumeException as e:
        logger.warning(f"Invalid resume uploaded: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except ProfileExtractionException as e:
        logger.error(f"Extraction failed: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to extract profile from resume.")
    except Exception as e:
        logger.error(f"Unexpected error during profile upload: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred.")
''')

# 6. Core Dependencies
write_file("core/dependencies.py", '''"""
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
''')

# 7. Testing
write_file("tests/unit/profile/test_profile_service.py", '''"""
Unit tests for Profile Service.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock
from io import BytesIO

from proxy_backend.domains.profile.services import ProfileService
from proxy_backend.domains.profile.exceptions import InvalidResumeException, ProfileExtractionException
from proxy_backend.domains.profile.schemas import ProfileExtraction, ExperienceLevelEnum
from proxy_backend.shared.pdf.exceptions import PDFParsingException

@pytest.fixture
def mock_pdf_parser():
    parser = MagicMock()
    parser.extract_text.return_value = "Extracted resume text"
    return parser

@pytest.fixture
def mock_profile_agent():
    agent = AsyncMock()
    agent.extract_profile.return_value = ProfileExtraction(
        skills=["Python", "FastAPI"],
        tech_stack=["Postgres"],
        projects=["Proxy"],
        experience_level=ExperienceLevelEnum.SENIOR,
        preferred_roles=["Backend Engineer"]
    )
    return agent

@pytest.fixture
def mock_repository():
    repo = AsyncMock()
    repo.save_profile.return_value = {
        "id": "1",
        "skills": ["Python", "FastAPI"],
        "tech_stack": ["Postgres"],
        "projects": ["Proxy"],
        "experience_level": "senior",
        "preferred_roles": ["Backend Engineer"]
    }
    return repo

@pytest.fixture
def profile_service(mock_pdf_parser, mock_profile_agent, mock_repository):
    return ProfileService(
        pdf_parser=mock_pdf_parser,
        profile_agent=mock_profile_agent,
        repository=mock_repository
    )

@pytest.mark.asyncio
async def test_successful_upload(profile_service, mock_pdf_parser, mock_profile_agent, mock_repository):
    file_stream = BytesIO(b"fake pdf content")
    response = await profile_service.process_upload(file_stream)
    
    assert response.id == "1"
    assert response.skills == ["Python", "FastAPI"]
    mock_pdf_parser.extract_text.assert_called_once_with(file_stream)
    mock_profile_agent.extract_profile.assert_called_once_with("Extracted resume text", None, None)
    mock_repository.save_profile.assert_called_once()

@pytest.mark.asyncio
async def test_empty_resume(profile_service, mock_pdf_parser):
    mock_pdf_parser.extract_text.return_value = "   "
    file_stream = BytesIO(b"empty")
    
    with pytest.raises(InvalidResumeException):
        await profile_service.process_upload(file_stream)

@pytest.mark.asyncio
async def test_pdf_parsing_failure(profile_service, mock_pdf_parser):
    mock_pdf_parser.extract_text.side_effect = PDFParsingException("Corrupted PDF")
    file_stream = BytesIO(b"corrupted")
    
    with pytest.raises(InvalidResumeException):
        await profile_service.process_upload(file_stream)

@pytest.mark.asyncio
async def test_agent_extraction_failure(profile_service, mock_profile_agent):
    mock_profile_agent.extract_profile.side_effect = Exception("LLM Error")
    file_stream = BytesIO(b"valid")
    
    with pytest.raises(ProfileExtractionException):
        await profile_service.process_upload(file_stream)
''')

print("Sprint 1 Bootstrap logic written.")
