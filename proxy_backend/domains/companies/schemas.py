"""
Pydantic V2 schemas for the companies domain.
"""
from pydantic import BaseModel, ConfigDict

class CompaniesBase(BaseModel):
    """Base schema for companies."""
    model_config = ConfigDict(from_attributes=True)
