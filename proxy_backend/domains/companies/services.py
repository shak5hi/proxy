"""
Service layer for the companies domain.
Contains pure business logic.
"""

class CompaniesService:
    """Orchestrates business use cases for companies."""
    
    def __init__(self, repository) -> None:
        """
        Initialize companies service with repository injection.
        
        Args:
            repository: The companies repository.
        """
        self.repository = repository
