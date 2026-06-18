"""
Pydantic V2 schemas for the profile domain.
"""
from pydantic import BaseModel, ConfigDict

class ProfileBase(BaseModel):
    """Base schema for profile."""
    model_config = ConfigDict(from_attributes=True)
