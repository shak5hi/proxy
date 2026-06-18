"""
Pydantic V2 schemas for the analytics domain.
"""
from pydantic import BaseModel, ConfigDict

class AnalyticsBase(BaseModel):
    """Base schema for analytics."""
    model_config = ConfigDict(from_attributes=True)
