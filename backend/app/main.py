from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.api.routes import router as api_router
from app.core.config import settings
from app.utils.logger import logger

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize resources or log system info
    logger.info(f"Starting {settings.PROJECT_NAME} Engine v{settings.VERSION}")
    logger.info(f"Compute Hardware detected: {settings.COMPUTE_DEVICE}")
    yield
    # Shutdown: Clean up or close persistent connections
    logger.info(f"Shutting down {settings.PROJECT_NAME} Engine")

app = FastAPI(
    title=settings.PROJECT_NAME, 
    version=settings.VERSION,
    lifespan=lifespan
)

# Standard CORS configuration for React integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/health")
async def health_check():
    """Endpoint for monitoring engine availability."""
    return {"status": "healthy", "device": settings.COMPUTE_DEVICE}