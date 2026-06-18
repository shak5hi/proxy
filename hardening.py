import os
from pathlib import Path

BACKEND_DIR = Path("C:/Users/shaks/OneDrive/Desktop/Projects/proxy/proxy/proxy_backend")

def write_file(rel_path: str, content: str):
    path = BACKEND_DIR / rel_path
    if not path.parent.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")

# 1. api/profile.py
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
        resume_bytes = await resume.read()
        response = await profile_service.process_upload(
            resume_bytes=resume_bytes,
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

# 2. domains/profile/services.py
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
        resume_bytes: bytes, 
        github_url: Optional[str] = None, 
        linkedin_url: Optional[str] = None
    ) -> ProfileResponse:
        """
        Process the uploaded resume bytes and optional URLs to extract and save a profile.
        """
        logger.info("upload started")
        
        # 1. Parse PDF
        logger.info("pdf extraction started")
        try:
            resume_text = self.pdf_parser.extract_text(resume_bytes)
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
        
        try:
            saved_record = await self.repository.save_profile(profile_data)
        except Exception as e:
            logger.error(f"Failed to save profile to database: {e}")
            raise
            
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

# 3. shared/pdf/interfaces.py & pdf_parser.py
write_file("shared/pdf/interfaces.py", '''"""
Interface for PDF Parsers.
"""
from abc import ABC, abstractmethod

class PDFParser(ABC):
    """Abstract Base Class for extracting text from PDFs."""
    
    @abstractmethod
    def extract_text(self, resume_bytes: bytes) -> str:
        """Extract text from raw PDF bytes."""
        pass
''')

write_file("shared/pdf/pdf_parser.py", '''"""
Concrete implementation of PDFParser using pypdf.
"""
import io
import logging
from pypdf import PdfReader

from .interfaces import PDFParser
from .exceptions import PDFParsingException

logger = logging.getLogger(__name__)

class PyPDFParser(PDFParser):
    """Implementation using PyPDF."""
    
    def extract_text(self, resume_bytes: bytes) -> str:
        """Extract text from PDF bytes."""
        try:
            file_stream = io.BytesIO(resume_bytes)
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

# 4. agents/profile_agent/agent.py
write_file("agents/profile_agent/agent.py", '''"""
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
''')

# 5. domains/profile/repositories.py
write_file("domains/profile/repositories.py", '''"""
Repository for the Profile Domain.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any
import logging
from postgrest.exceptions import APIError

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
            result = self.supabase.table("profiles").insert(profile_data).execute()
            if not result.data:
                raise ValueError("Insert returned no data.")
            return result.data[0]
        except APIError as e:
            logger.error(f"Supabase APIError while saving profile: {e}")
            raise Exception(f"Database insertion failed: {e}")
        except Exception as e:
            logger.error(f"Unexpected database error while saving profile: {e}")
            raise Exception(f"Failed to save profile: {e}")
''')

# 6. tests/unit/profile/test_profile_service.py
write_file("tests/unit/profile/test_profile_service.py", '''"""
Unit tests for Profile Service.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock

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
    resume_bytes = b"fake pdf content"
    response = await profile_service.process_upload(resume_bytes)
    
    assert response.id == "1"
    assert response.skills == ["Python", "FastAPI"]
    mock_pdf_parser.extract_text.assert_called_once_with(resume_bytes)
    mock_profile_agent.extract_profile.assert_called_once_with("Extracted resume text", None, None)
    mock_repository.save_profile.assert_called_once()

@pytest.mark.asyncio
async def test_empty_resume(profile_service, mock_pdf_parser):
    mock_pdf_parser.extract_text.return_value = "   "
    resume_bytes = b"empty"
    
    with pytest.raises(InvalidResumeException):
        await profile_service.process_upload(resume_bytes)

@pytest.mark.asyncio
async def test_pdf_parsing_failure(profile_service, mock_pdf_parser):
    mock_pdf_parser.extract_text.side_effect = PDFParsingException("Corrupted PDF")
    resume_bytes = b"corrupted"
    
    with pytest.raises(InvalidResumeException):
        await profile_service.process_upload(resume_bytes)

@pytest.mark.asyncio
async def test_agent_extraction_failure(profile_service, mock_profile_agent):
    mock_profile_agent.extract_profile.side_effect = Exception("LLM Error")
    resume_bytes = b"valid"
    
    with pytest.raises(ProfileExtractionException):
        await profile_service.process_upload(resume_bytes)
''')

# 7. tests/integration/profile/test_profile_flow.py
write_file("tests/integration/profile/test_profile_flow.py", '''"""
Integration tests for Profile Domain Vertical Slice.
Tests the actual flow using real Gemini and real Supabase.
"""
import pytest
import httpx
from fastapi.testclient import TestClient

# Assumes you have your FastAPI app available in proxy_backend.main.app
# We'll create a minimal mock app here for the integration test to wrap the router if main.py is missing.
from fastapi import FastAPI
from proxy_backend.api.profile import router

app = FastAPI()
app.include_router(router)

client = TestClient(app)

# Note: Integration tests require .env to be configured with valid keys.

# To test this, you must construct a valid PDF. 
# Due to environments, we skip real external calls if keys are not present in CI.
# But you can run this manually: `pytest tests/integration/profile/test_profile_flow.py`

def create_dummy_pdf() -> bytes:
    """Creates a very basic valid PDF byte string."""
    pdf = b"%PDF-1.4\\n1 0 obj\\n<< /Type /Catalog /Pages 2 0 R >>\\nendobj\\n2 0 obj\\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\\nendobj\\n3 0 obj\\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>\\nendobj\\n4 0 obj\\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\\nendobj\\n5 0 obj\\n<< /Length 44 >>\\nstream\\nBT\\n/F1 24 Tf\\n100 700 Td\\n(Jane Doe Resume) Tj\\nET\\nendstream\\nendobj\\nxref\\n0 6\\n0000000000 65535 f \\n0000000009 00000 n \\n0000000058 00000 n \\n0000000115 00000 n \\n0000000223 00000 n \\n0000000311 00000 n \\ntrailer\\n<< /Size 6 /Root 1 0 R >>\\nstartxref\\n406\\n%%EOF\\n"
    return pdf

@pytest.mark.skip(reason="Requires valid GEMINI and SUPABASE API keys in .env")
def test_real_profile_upload_flow():
    """
    Test the full upload flow: API -> Service -> PDFParser -> Gemini -> Supabase
    """
    pdf_bytes = create_dummy_pdf()
    
    response = client.post(
        "/profile/upload",
        files={"resume": ("sample_resume.pdf", pdf_bytes, "application/pdf")},
        data={"github_url": "https://github.com/janedoe", "linkedin_url": "https://linkedin.com/in/janedoe"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert "experience_level" in data
''')

# Ensure main.py exists to bind the router
write_file("main.py", '''"""
Main entrypoint for the Proxy backend.
"""
from fastapi import FastAPI
from proxy_backend.api.profile import router as profile_router

app = FastAPI(title="Proxy API")

app.include_router(profile_router, prefix="/api/v1")
''')
