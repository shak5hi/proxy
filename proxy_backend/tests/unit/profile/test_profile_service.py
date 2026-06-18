"""
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
