"""Main FastAPI Application for Huvo AI Northstar Homes Conversational Agent."""

import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.config import settings
from app.routes.chat import router as chat_router, get_test_scenarios
from app.routes.analytics import router as analytics_router

app = FastAPI(
    title="Northstar Homes - AI Conversational Sales Agent",
    description="Conversational AI agent for Northstar One (Sector 79, Gurugram) supporting Voice & Chat interactions.",
    version="1.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(chat_router)
app.include_router(analytics_router)

# Mount direct alias for scenarios
@app.get("/api/scenarios", tags=["Scenarios"])
async def scenarios_alias():
    return await get_test_scenarios()

# Mount Static Files Directory
static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

@app.get("/")
async def get_index():
    """Serve the conversational web interface."""
    index_file = static_dir / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {
        "message": "Northstar Homes AI Sales Agent API is running.",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "Northstar Homes AI Sales Agent",
        "provider": settings.LLM_PROVIDER,
        "project": settings.PROJECT_NAME,
        "location": settings.PROJECT_LOCATION
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
