#!/usr/bin/env python3
"""
Setup script for Python Automation Scripts Collection
Installs dependencies and sets up the environment
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors."""
    print(f"📦 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        if e.stdout:
            print(f"Output: {e.stdout}")
        if e.stderr:
            print(f"Error: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print(f"❌ Python 3.7 or higher is required. Current version: {version.major}.{version.minor}")
        return False
    print(f"✅ Python version {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def install_dependencies():
    """Install required dependencies."""
    requirements_file = Path(__file__).parent / "requirements.txt"
    
    if not requirements_file.exists():
        print("❌ requirements.txt not found")
        return False
    
    command = f"{sys.executable} -m pip install -r {requirements_file}"
    return run_command(command, "Installing dependencies")

def setup_scripts():
    """Make scripts executable (Unix-like systems)."""
    if os.name != 'nt':  # Not Windows
        script_dirs = [
            "bulk-file-renamer",
            "image-converter", 
            "web-scraper",
            "folder-organizer"
        ]
        
        for script_dir in script_dirs:
            script_path = Path(__file__).parent / script_dir
            if script_path.exists():
                for py_file in script_path.glob("*.py"):
                    command = f"chmod +x {py_file}"
                    run_command(command, f"Making {py_file.name} executable")
    
    return True

def main():
    """Main setup function."""
    print("🚀 Python Automation Scripts Collection Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("\n❌ Setup failed during dependency installation")
        sys.exit(1)
    
    # Setup scripts
    setup_scripts()
    
    print("\n" + "=" * 50)
    print("🎉 Setup completed successfully!")
    print("\nAvailable scripts:")
    print("  📁 bulk-file-renamer/bulk_renamer.py")
    print("  🖼️  image-converter/image_converter.py") 
    print("  🌐 web-scraper/web_scraper.py")
    print("  📂 folder-organizer/folder_organizer.py")
    print("\nUsage examples:")
    print("  python bulk-file-renamer/bulk_renamer.py --help")
    print("  python image-converter/image_converter.py --help")
    print("  python web-scraper/web_scraper.py --help")
    print("  python folder-organizer/folder_organizer.py --help")
    print("\nFor detailed documentation, check the README.md in each script folder.")

if __name__ == "__main__":
    main()
