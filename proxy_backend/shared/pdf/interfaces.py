"""
Interface for PDF Parsers.
"""
from abc import ABC, abstractmethod

class PDFParser(ABC):
    """Abstract Base Class for extracting text from PDFs."""
    
    @abstractmethod
    def extract_text(self, resume_bytes: bytes) -> str:
        """Extract text from raw PDF bytes."""
        pass
