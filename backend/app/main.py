import sys
from pathlib import Path
import logging

# Ensure backend root is in sys.path
_backend_dir = str(Path(__file__).resolve().parent.parent)
if _backend_dir not in sys.path:
    sys.path.insert(0, _backend_dir)

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

try:
    from app.config import get_settings
    from app.routes.incident import router as incident_router
except ImportError:
    from backend.app.config import get_settings
    from backend.app.routes.incident import router as incident_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("incident_response_backend")

settings = get_settings()

app = FastAPI(
    title="AI Incident Response Agent API",
    description=(
        "Backend API for analyzing incident logs, retrieving verified historical "
        "incident memory with Hindsight, and generating root cause investigations with Groq."
    ),
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(incident_router)


@app.get("/", tags=["Health"])
def health_check():
    """Health check endpoint to verify backend service status."""
    return {
        "status": "ok",
        "message": "Incident Response Backend is running"
    }


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler to avoid leaking internal environment or stack details."""
    logger.exception("Unhandled error occurred while processing %s: %s", request.url.path, exc)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "An internal server error occurred. Please check backend logs."
        }
    )


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
