from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.api.api_router import api_router
from app.core.scheduler import start_scheduler, shutdown_scheduler
from app.core.config import settings # Import settings
import os

app = FastAPI(title="Podcast Ad-Remover", version="0.1.0")

@app.on_event("startup")
async def startup_event():
    start_scheduler()

@app.on_event("shutdown")
async def shutdown_event():
    shutdown_scheduler()

# API router
app.include_router(api_router, prefix="/api/v1")

# Static files for the frontend
app.mount("/static", StaticFiles(directory=os.path.join(settings.BASE_DIR, "frontend/static")), name="static")

# Serve frontend
@app.get("/{full_path:path}")
async def serve_frontend(full_path: str):
    # This catch-all route serves the index.html file for any non-api, non-static path.
    # The frontend router will then handle the path.
    # Check if the file exists in the static directory first
    static_file_path = os.path.join(settings.BASE_DIR, "frontend", full_path)
    if os.path.isfile(static_file_path):
        return FileResponse(static_file_path)
        
    # If not a file, and not an api call, serve the index
    if not full_path.startswith("api/"):
        return FileResponse(os.path.join(settings.BASE_DIR, "frontend/index.html"))

    # For API calls that are not found, FastAPI will return a 404
    # You might want to add more specific error handling here
    return {"message": "Not Found"}, 404

