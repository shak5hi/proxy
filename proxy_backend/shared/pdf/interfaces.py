"""
Interface for PDF Parsers.
"""
from abc import ABC, abstractmethod
from typing import BinaryIO

class PDFParser(ABC):
    """Abstract Base Class for extracting text from PDFs."""
    
    @abstractmethod
    def extract_text(self, file_stream: BinaryIO) -> str:
        """Extract text from a binary PDF stream."""
        pass
