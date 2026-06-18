"""
Repository for the Profile Domain.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any
import logging
from postgrest.exceptions import APIError

logger = logging.getLogger(__name__)

class AbstractProfileRepository(ABC):
    """Interface for Profile Repository."""
    
    @abstractmethod
    async def save_profile(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Save a new profile to the database."""
        pass

class ProfileRepository(AbstractProfileRepository):
    """Concrete implementation for Supabase."""
    
    def __init__(self, supabase_client: Any) -> None:
        """Inject the Supabase client."""
        self.supabase = supabase_client
        
    async def save_profile(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Insert profile into Supabase profiles table."""
        try:
            result = self.supabase.table("profiles").insert(profile_data).execute()
            if not result.data:
                raise ValueError("Insert returned no data.")
            return result.data[0]
        except APIError as e:
            logger.error(f"Supabase APIError while saving profile: {e}")
            raise Exception(f"Database insertion failed: {e}")
        except Exception as e:
            logger.error(f"Unexpected database error while saving profile: {e}")
            raise Exception(f"Failed to save profile: {e}")
