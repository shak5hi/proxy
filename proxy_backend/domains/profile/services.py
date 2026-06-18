"""
Service layer for the profile domain.
Contains pure business logic.
"""

class ProfileService:
    """Orchestrates business use cases for profile."""
    
    def __init__(self, repository) -> None:
        """
        Initialize profile service with repository injection.
        
        Args:
            repository: The profile repository.
        """
        self.repository = repository
