"""
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
