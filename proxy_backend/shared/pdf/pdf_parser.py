"""
Concrete implementation of PDFParser using pypdf.
"""
from typing import BinaryIO
from pypdf import PdfReader
import logging

from .interfaces import PDFParser
from .exceptions import PDFParsingException

logger = logging.getLogger(__name__)

class PyPDFParser(PDFParser):
    """Implementation using PyPDF."""
    
    def extract_text(self, file_stream: BinaryIO) -> str:
        """Extract text from a PDF file stream."""
        try:
            reader = PdfReader(file_stream)
            text = []
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text.append(page_text)
            return "\n".join(text)
        except Exception as e:
            logger.error(f"Failed to parse PDF: {e}")
            raise PDFParsingException(f"Failed to parse PDF: {e}")
