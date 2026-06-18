"""
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
