"""
Service layer for the analytics domain.
Contains pure business logic.
"""

class AnalyticsService:
    """Orchestrates business use cases for analytics."""
    
    def __init__(self, repository) -> None:
        """
        Initialize analytics service with repository injection.
        
        Args:
            repository: The analytics repository.
        """
        self.repository = repository
