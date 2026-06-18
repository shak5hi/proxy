"""
Pydantic V2 schemas for the gmail domain.
"""
from pydantic import BaseModel, ConfigDict

class GmailBase(BaseModel):
    """Base schema for gmail."""
    model_config = ConfigDict(from_attributes=True)
