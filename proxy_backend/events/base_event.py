"""
Base Event definitions.
"""
from pydantic import BaseModel
from datetime import datetime

class BaseEvent(BaseModel):
    """Base schema for all events in the system."""
    event_id: str
    timestamp: datetime
