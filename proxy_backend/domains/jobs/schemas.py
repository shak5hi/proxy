"""
Pydantic V2 schemas for the jobs domain.
"""
from pydantic import BaseModel, ConfigDict

class JobsBase(BaseModel):
    """Base schema for jobs."""
    model_config = ConfigDict(from_attributes=True)
