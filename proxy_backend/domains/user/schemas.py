"""
Pydantic V2 schemas for the user domain.
"""
from pydantic import BaseModel, ConfigDict

class UserBase(BaseModel):
    """Base schema for user."""
    model_config = ConfigDict(from_attributes=True)
