"""
Main entrypoint for the Proxy backend.
"""
from fastapi import FastAPI
from proxy_backend.api.profile import router as profile_router

app = FastAPI(title="Proxy API")

app.include_router(profile_router, prefix="/api/v1")
