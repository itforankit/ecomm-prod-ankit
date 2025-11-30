"""
FastAPI application entry point for the Product Assistant API.
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from prod_assistant.router.main import router as scraper_router


app = FastAPI(
    title="Product Assistant API",
    description="API for web scraping and vector database operations",
    version="1.0.0",
)

# Configure CORS - use environment variable for production, default to localhost for development
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:8000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Include routers
app.include_router(scraper_router)


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Product Assistant API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "scraper": "/api/v1/scraper",
        },
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
