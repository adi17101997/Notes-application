#!/usr/bin/env python3
"""
Quick start script for NotesApp Backend
Automatically handles virtual environment and starts the application.
"""

import os
import subprocess
import sys
import platform

def get_venv_python():
    """Get the Python executable from virtual environment."""
    if platform.system() == "Windows":
        return os.path.join('venv', 'Scripts', 'python.exe')
    else:
        return os.path.join('venv', 'bin', 'python')

def check_venv():
    """Check if virtual environment exists and has dependencies."""
    venv_python = get_venv_python()

    if not os.path.exists(venv_python):
        print("❌ Virtual environment not found!")
        print("Please run 'python setup.py' first to set up the environment.")
        return False

    # Check if uvicorn is installed
    try:
        subprocess.run([venv_python, '-c', 'import uvicorn'],
                      check=True, capture_output=True)
        return True
    except subprocess.CalledProcessError:
        print("❌ Dependencies not installed!")
        print("Please run 'python setup.py' first to install dependencies.")
        return False

def start_app():
    """Start the FastAPI application."""
    venv_python = get_venv_python()

    print("🚀 Starting NotesApp Backend...")
    print("📍 API will be available at: http://localhost:8000")
    print("📚 API docs will be available at: http://localhost:8000/docs")
    print("🛑 Press Ctrl+C to stop the server")
    print("-" * 50)

    try:
        subprocess.run([venv_python, 'run.py'], check=True)
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start server: {e}")
        return False

    return True

def main():
    print("🎯 NotesApp Backend Quick Start")
    print("=" * 40)

    # Check if virtual environment is ready
    if not check_venv():
        return

    # Start the application
    start_app()

if __name__ == "__main__":
    main()
