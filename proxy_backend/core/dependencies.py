"""
Centralized FastAPI dependencies.
No external DI containers; native FastAPI Depends() only.
"""
from typing import Generator
from fastapi import Request

# TODO: Add specific provider return types

def get_settings():
    """Dependency to retrieve application settings."""
    pass

def get_logger():
    """Dependency to retrieve the structured logger."""
    pass

def get_llm_provider():
    """Dependency to inject the LLM Provider."""
    pass

def get_embedding_provider():
    """Dependency to inject the Embedding Provider."""
    pass

def get_vector_store():
    """Dependency to inject the Vector Store Provider."""
    pass

def get_email_provider():
    """Dependency to inject the Email Provider."""
    pass
