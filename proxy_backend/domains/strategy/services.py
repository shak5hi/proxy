"""
Service layer for the strategy domain.
Contains pure business logic.
"""

class StrategyService:
    """Orchestrates business use cases for strategy."""
    
    def __init__(self, repository) -> None:
        """
        Initialize strategy service with repository injection.
        
        Args:
            repository: The strategy repository.
        """
        self.repository = repository
