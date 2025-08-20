#!/usr/bin/env python3
"""
Setup script for NotesApp Backend
This script will create the necessary environment and start the application.
"""

import os
import subprocess
import sys
import platform

def get_python_version():
    """Get Python version as tuple."""
    return sys.version_info[:2]

def get_requirements_files():
    """Get list of requirements files in order of preference."""
    version = get_python_version()

    if version >= (3, 13):
        print(f"🐍 Python {version[0]}.{version[1]} detected - trying multiple compatibility levels")
        return [
            'requirements-py313.txt',
            'requirements-minimal.txt',
            'requirements-basic.txt'
        ]
    else:
        print(f"🐍 Python {version[0]}.{version[1]} detected - using standard requirements")
        return ['requirements.txt']

def create_venv():
    """Create virtual environment if it doesn't exist."""
    if not os.path.exists('venv'):
        print("🐍 Creating virtual environment...")
        try:
            subprocess.run([sys.executable, '-m', 'venv', 'venv'], check=True)
            print("✅ Virtual environment created successfully")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to create virtual environment")
            return False
    else:
        print("✅ Virtual environment already exists")
        return True

def get_venv_python():
    """Get the Python executable from virtual environment."""
    if platform.system() == "Windows":
        return os.path.join('venv', 'Scripts', 'python.exe')
    else:
        return os.path.join('venv', 'bin', 'python')

def get_venv_pip():
    """Get the pip executable from virtual environment."""
    if platform.system() == "Windows":
        return os.path.join('venv', 'Scripts', 'pip.exe')
    else:
        return os.path.join('venv', 'bin', 'pip')

def create_env_file():
    """Create .env file if it doesn't exist."""
    env_content = """DATABASE_URL=sqlite:///./notesapp.db
SECRET_KEY=your-secret-key-change-in-production
FRONTEND_URL=http://localhost:5173
"""

    if not os.path.exists('.env'):
        with open('.env', 'w') as f:
            f.write(env_content)
        print("✅ Created .env file")
    else:
        print("✅ .env file already exists")

def install_dependencies():
    """Install Python dependencies in virtual environment."""
    print("📦 Installing Python dependencies...")

    venv_pip = get_venv_pip()
    requirements_files = get_requirements_files()

    for req_file in requirements_files:
        if os.path.exists(req_file):
            print(f"📋 Trying requirements file: {req_file}")
            try:
                subprocess.run([venv_pip, 'install', '-r', req_file], check=True)
                print(f"✅ Successfully installed dependencies from {req_file}")
                return True
            except subprocess.CalledProcessError:
                print(f"❌ Failed with {req_file}, trying next...")
                continue
        else:
            print(f"⚠️  Requirements file {req_file} not found, skipping...")

    print("❌ All requirements files failed!")
    return False

def main():
    print("🚀 Setting up NotesApp Backend...")
    print(f"🐍 Python version: {sys.version}")

    # Create virtual environment
    if not create_venv():
        print("❌ Setup failed. Could not create virtual environment.")
        return

    # Create .env file
    create_env_file()

    # Install dependencies
    if not install_dependencies():
        print("❌ Setup failed. Please check the error messages above.")
        print("\n🔧 Troubleshooting options:")
        print("1. Try using Python 3.11 or 3.12 instead of 3.13")
        print("2. Install Rust compiler: brew install rust")
        print("3. Try installing dependencies manually in the virtual environment")
        print("4. Use the ultra-basic requirements: pip install -r requirements-basic.txt")
        return

    print("\n🎉 Setup completed successfully!")
    print("\nTo start the backend, run:")
    print("  source venv/bin/activate  # On macOS/Linux")
    print("  venv\\Scripts\\activate     # On Windows")
    print("  python run.py")
    print("\nOr use the quick start command:")
    print("  python start.py")
    print("\nThe API will be available at: http://localhost:8000")
    print("API documentation at: http://localhost:8000/docs")

if __name__ == "__main__":
    main()
