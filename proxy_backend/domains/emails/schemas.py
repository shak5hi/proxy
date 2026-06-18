"""
Pydantic V2 schemas for the emails domain.
"""
from pydantic import BaseModel, ConfigDict

class EmailsBase(BaseModel):
    """Base schema for emails."""
    model_config = ConfigDict(from_attributes=True)
