#!/usr/bin/env python3
"""
Parking Management System - Startup Script
Automatically handles platform detection and dependency checking
"""

import sys
import subprocess
import os
import platform

def check_python_version():
    """Check if Python version is compatible"""
    major, minor = sys.version_info[:2]
    if major < 3 or (major == 3 and minor < 8):
        print("❌ Python 3.8+ required")
        print(f"Current version: {sys.version}")
        print("Please upgrade Python from https://python.org")
        return False
    print(f"✅ Python {major}.{minor} - Compatible")
    return True

def check_dependencies():
    """Check if required libraries are installed"""
    try:
        import tkinter
        print("✅ tkinter - Available")
    except ImportError:
        print("❌ tkinter not found")
        print("Please install tkinter:")
        if platform.system() == "Linux":
            print("  sudo apt install python3-tk")
        return False
    
    try:
        import reportlab
        print("✅ reportlab - Available")
    except ImportError:
        print("❌ reportlab not found")
        print("Installing reportlab...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "reportlab"], check=True)
            print("✅ reportlab installed successfully")
        except subprocess.CalledProcessError:
            print("❌ Failed to install reportlab")
            print("Please run: pip install reportlab")
            return False
    
    return True

def main():
    """Main startup function"""
    print("🚀 Parking Management System Startup")
    print("=" * 45)
    
    # Check Python version
    if not check_python_version():
        input("Press Enter to exit...")
        sys.exit(1)
    
    # Check dependencies
    if not check_dependencies():
        input("Press Enter to exit...")
        sys.exit(1)
    
    # Check if main app exists
    if not os.path.exists("parking_app.py"):
        print("❌ parking_app.py not found in current directory")
        print("Please run this script from the parking app folder")
        input("Press Enter to exit...")
        sys.exit(1)
    
    print("\n🎉 All checks passed! Starting application...")
    print("=" * 45)
    
    # Import and run the main application
    try:
        import parking_app
        print("✅ Application started successfully")
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        input("Press Enter to exit...")
        sys.exit(1)

if __name__ == "__main__":
    main()
