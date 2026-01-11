#!/bin/bash

# Navigate to the backend directory
cd backend

# Install dependencies if not already installed
pip install -r requirements.txt

# Start Gunicorn with Uvicorn workers
# -w: number of worker processes
# -k uvicorn.workers.UvicornWorker: use Uvicorn worker class for FastAPI
# --bind 0.0.0.0:8000: bind to all network interfaces on port 8000
# app.main:app: the FastAPI application instance
exec gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
