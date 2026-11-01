#!/bin/bash

echo "🚀 Parking Management System - Unix Startup"
echo "============================================="
echo

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found"
    echo "Please install Python 3.8+ from your package manager:"
    echo "  Ubuntu/Debian: sudo apt install python3 python3-pip python3-tk"
    echo "  macOS: brew install python-tk"
    echo "  CentOS/RHEL: sudo yum install python3 python3-pip python3-tkinter"
    echo
    read -p "Press Enter to exit..."
    exit 1
fi

# Check Python version
python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ Python 3.8+ required"
    echo "Current version: $(python3 --version)"
    echo "Please install Python 3.8+ from https://python.org"
    echo
    read -p "Press Enter to exit..."
    exit 1
fi

echo "✅ Python 3 found and compatible"
echo

# Run the startup script
echo "Starting Parking Management System..."
echo
python3 start_parking_app.py

# Check if there was an error
if [ $? -ne 0 ]; then
    echo
    echo "❌ Application failed to start"
    read -p "Press Enter to exit..."
fi
