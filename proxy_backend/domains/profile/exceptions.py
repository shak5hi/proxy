"""
Exceptions for the Profile Domain.
"""

class ProfileNotFoundException(Exception):
    """Raised when a profile cannot be found in the database."""
    pass

class ProfileExtractionException(Exception):
    """Raised when the agent fails to extract a profile from the provided text."""
    pass

class InvalidResumeException(Exception):
    """Raised when the uploaded resume is invalid or unreadable."""
    pass
