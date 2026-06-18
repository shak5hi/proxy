"""
Service layer for the emails domain.
Contains pure business logic.
"""

class EmailsService:
    """Orchestrates business use cases for emails."""
    
    def __init__(self, repository) -> None:
        """
        Initialize emails service with repository injection.
        
        Args:
            repository: The emails repository.
        """
        self.repository = repository
