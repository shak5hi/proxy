"""
Pydantic V2 schemas for the strategy domain.
"""
from pydantic import BaseModel, ConfigDict

class StrategyBase(BaseModel):
    """Base schema for strategy."""
    model_config = ConfigDict(from_attributes=True)
