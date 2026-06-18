"""
Service layer for the jobs domain.
Contains pure business logic.
"""

class JobsService:
    """Orchestrates business use cases for jobs."""
    
    def __init__(self, repository) -> None:
        """
        Initialize jobs service with repository injection.
        
        Args:
            repository: The jobs repository.
        """
        self.repository = repository
