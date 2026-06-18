"""
Service layer for the gmail domain.
Contains pure business logic.
"""

class GmailService:
    """Orchestrates business use cases for gmail."""
    
    def __init__(self, repository) -> None:
        """
        Initialize gmail service with repository injection.
        
        Args:
            repository: The gmail repository.
        """
        self.repository = repository
