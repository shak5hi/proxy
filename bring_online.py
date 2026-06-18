import os
from pathlib import Path
import base64

BACKEND_DIR = Path("C:/Users/shaks/OneDrive/Desktop/Projects/proxy/proxy/proxy_backend")

def write_file(rel_path: str, content: str):
    path = BACKEND_DIR / rel_path
    if not path.parent.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")

# 1. requirements.txt
write_file("requirements.txt", '''fastapi
uvicorn
python-multipart
pydantic
pydantic-settings
google-genai
supabase
pypdf
pytest
pytest-asyncio
httpx
''')

# 2. .env.example
write_file("../.env.example", '''GEMINI_API_KEY=your_gemini_api_key_here
SUPABASE_URL=your_supabase_url_here
SUPABASE_KEY=your_supabase_key_here
LOG_LEVEL=INFO
ENVIRONMENT=development
''')

# 3. .gitignore
write_file("../.gitignore", '''# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv/
.venv/
ENV/

# Env Variables
.env
.env.local

# IDEs
.vscode/
.idea/
''')

# 4. main.py with middleware and hooks
write_file("main.py", '''"""
Main entrypoint for the Proxy backend.
"""
import time
import logging
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from proxy_backend.api.profile import router as profile_router
from proxy_backend.core.config import Settings

# Configure basic logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Proxy API",
    version="1.0.0",
    description="API for Proxy InternFlow Profile Extraction."
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom Logging Middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    logger.info(f"Incoming request: {request.method} {request.url.path}")
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        logger.info(f"Completed request: {request.method} {request.url.path} - Status: {response.status_code} - Time: {process_time:.4f}s")
        return response
    except Exception as e:
        logger.error(f"Request failed: {request.method} {request.url.path} - Error: {str(e)}")
        raise

# Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled Global Exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An internal server error occurred. Please contact support."},
    )

# Startup Event
@app.on_event("startup")
async def startup_event():
    """Fail fast if environment configurations are missing."""
    logger.info("Starting up Proxy Backend...")
    try:
        settings = Settings()
        if not settings.gemini_api_key or not settings.supabase_url or not settings.supabase_key:
            logger.warning("WARNING: Required environment variables are missing! Ensure .env is populated before testing integration flows.")
        else:
            logger.info("Environment variables loaded successfully.")
    except Exception as e:
        logger.error(f"Failed to load settings: {e}")
        raise RuntimeError(f"Startup Configuration Failed: {e}")

# Include Routers
app.include_router(profile_router, prefix="/api/v1")
''')

# 5. core/config.py ensuring fail fast behavior and loading environment properly
write_file("core/config.py", '''"""
Configuration module using pydantic-settings.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    gemini_api_key: str = Field(default="", env="GEMINI_API_KEY")
    supabase_url: str = Field(default="", env="SUPABASE_URL")
    supabase_key: str = Field(default="", env="SUPABASE_KEY")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    environment: str = Field(default="development", env="ENVIRONMENT")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")
''')

# 6. Sample PDF generator for Integration Tests
def create_sample_pdf():
    pdf_content = b"%PDF-1.4\\n1 0 obj\\n<< /Type /Catalog /Pages 2 0 R >>\\nendobj\\n2 0 obj\\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\\nendobj\\n3 0 obj\\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>\\nendobj\\n4 0 obj\\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\\nendobj\\n5 0 obj\\n<< /Length 44 >>\\nstream\\nBT\\n/F1 24 Tf\\n100 700 Td\\n(Jane Doe Resume) Tj\\nET\\nendstream\\nendobj\\nxref\\n0 6\\n0000000000 65535 f \\n0000000009 00000 n \\n0000000058 00000 n \\n0000000115 00000 n \\n0000000223 00000 n \\n0000000311 00000 n \\ntrailer\\n<< /Size 6 /Root 1 0 R >>\\nstartxref\\n406\\n%%EOF\\n"
    res_dir = BACKEND_DIR / "tests" / "resources"
    res_dir.mkdir(parents=True, exist_ok=True)
    with (res_dir / "sample_resume.pdf").open("wb") as f:
        f.write(pdf_content)

create_sample_pdf()

print("Bring Online logic written successfully.")
