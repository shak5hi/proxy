"""
Integration tests for Profile Domain Vertical Slice.
Tests the actual flow using real Gemini and real Supabase.
"""
import pytest
import httpx
from fastapi.testclient import TestClient

# Assumes you have your FastAPI app available in proxy_backend.main.app
# We'll create a minimal mock app here for the integration test to wrap the router if main.py is missing.
from fastapi import FastAPI
from proxy_backend.api.profile import router

app = FastAPI()
app.include_router(router)

client = TestClient(app)

# Note: Integration tests require .env to be configured with valid keys.

# To test this, you must construct a valid PDF. 
# Due to environments, we skip real external calls if keys are not present in CI.
# But you can run this manually: `pytest tests/integration/profile/test_profile_flow.py`

def create_dummy_pdf() -> bytes:
    """Creates a very basic valid PDF byte string."""
    pdf = b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>\nendobj\n4 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n5 0 obj\n<< /Length 44 >>\nstream\nBT\n/F1 24 Tf\n100 700 Td\n(Jane Doe Resume) Tj\nET\nendstream\nendobj\nxref\n0 6\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \n0000000223 00000 n \n0000000311 00000 n \ntrailer\n<< /Size 6 /Root 1 0 R >>\nstartxref\n406\n%%EOF\n"
    return pdf

@pytest.mark.skip(reason="Requires valid GEMINI and SUPABASE API keys in .env")
def test_real_profile_upload_flow():
    """
    Test the full upload flow: API -> Service -> PDFParser -> Gemini -> Supabase
    """
    pdf_bytes = create_dummy_pdf()
    
    response = client.post(
        "/profile/upload",
        files={"resume": ("sample_resume.pdf", pdf_bytes, "application/pdf")},
        data={"github_url": "https://github.com/janedoe", "linkedin_url": "https://linkedin.com/in/janedoe"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert "experience_level" in data
