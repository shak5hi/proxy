"""
Service layer for the user domain.
Contains pure business logic.
"""

class UserService:
    """Orchestrates business use cases for user."""
    
    def __init__(self, repository) -> None:
        """
        Initialize user service with repository injection.
        
        Args:
            repository: The user repository.
        """
        self.repository = repository
