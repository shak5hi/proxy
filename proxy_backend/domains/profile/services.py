"""
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
