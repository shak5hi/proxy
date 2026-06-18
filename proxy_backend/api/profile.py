"""
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
