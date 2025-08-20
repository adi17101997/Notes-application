#!/usr/bin/env python3
"""
Development server runner for NotesApp API
"""
import uvicorn
import os
from app.main import app

if __name__ == "__main__":
    # Load environment variables
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    reload = os.getenv("RELOAD", "true").lower() == "true"
    
    print(f"Starting NotesApp API on {host}:{port}")
    print(f"Reload mode: {reload}")
    print("API Documentation: http://localhost:8000/docs")
    print("Health Check: http://localhost:8000/health")
    
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )