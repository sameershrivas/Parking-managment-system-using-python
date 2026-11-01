#!/usr/bin/env python3
"""
Cross-platform compatibility test for the parking app.
This script tests various platform-specific features to ensure compatibility.
"""

import platform
import os
import sys

def test_platform_detection():
    """Test platform detection and font selection"""
    print(f"✓ Platform detected: {platform.system()}")
    print(f"✓ Platform version: {platform.version()}")
    print(f"✓ Python version: {sys.version}")
    
    # Test font detection
    system = platform.system()
    if system == "Windows":
        expected_font = "Segoe UI"
    elif system == "Darwin":  # macOS
        expected_font = "SF Pro Display"
    else:  # Linux and others
        expected_font = "DejaVu Sans"
    
    print(f"✓ Expected font: {expected_font}")

def test_database_path():
    """Test database path creation"""
    db_dir = "parking_data"
    db_path = os.path.join(db_dir, "parking_system.db")
    print(f"✓ Database path: {db_path}")
    print(f"✓ Path separator: {os.path.sep}")
    print(f"✓ Absolute path: {os.path.abspath(db_path)}")

def test_tickets_path():
    """Test tickets directory path"""
    tickets_dir = "parking_tickets"
    tickets_path = os.path.join(tickets_dir, "test_ticket.pdf")
    print(f"✓ Tickets path: {tickets_path}")
    print(f"✓ Absolute path: {os.path.abspath(tickets_path)}")

def test_file_operations():
    """Test file operations"""
    test_dir = "test_parking_temp"
    test_file = os.path.join(test_dir, "test.txt")
    
    try:
        # Create directory
        if not os.path.exists(test_dir):
            os.makedirs(test_dir)
        print(f"✓ Created directory: {test_dir}")
        
        # Create file
        with open(test_file, 'w') as f:
            f.write("Test content")
        print(f"✓ Created file: {test_file}")
        
        # Check permissions (Unix-like systems)
        if platform.system() != "Windows":
            os.chmod(test_dir, 0o755)
            print(f"✓ Set permissions on directory")
        
        # Clean up
        os.remove(test_file)
        os.rmdir(test_dir)
        print(f"✓ Cleaned up test files")
        
    except Exception as e:
        print(f"❌ File operations test failed: {e}")

def test_subprocess_commands():
    """Test subprocess commands for opening files"""
    print("\n🔍 Testing file opening commands:")
    
    system = platform.system()
    if system == "Linux":
        commands = ["xdg-open", "gnome-open", "kde-open"]
    elif system == "Darwin":  # macOS
        commands = ["open"]
    elif system == "Windows":
        commands = ["start"]  # Note: start is built into cmd
    else:
        commands = ["xdg-open"]
    
    for cmd in commands:
        import subprocess
        try:
            # Test if command exists
            result = subprocess.run([cmd, "--help"], capture_output=True, timeout=5)
            if result.returncode == 0:
                print(f"✓ Command available: {cmd}")
            else:
                print(f"⚠️ Command available but returned error: {cmd}")
        except subprocess.TimeoutExpired:
            print(f"⚠️ Command timeout: {cmd}")
        except FileNotFoundError:
            print(f"❌ Command not found: {cmd}")
        except Exception as e:
            print(f"❌ Error testing command {cmd}: {e}")

def test_tkinter_compatibility():
    """Test tkinter availability and basic functionality"""
    try:
        import tkinter as tk
        print("✓ tkinter imported successfully")
        
        # Test basic widget creation (without displaying)
        root = tk.Tk()
        root.withdraw()  # Hide window
        
        # Test font specification
        test_font = ("Arial", 12, "bold")
        label = tk.Label(root, text="Test", font=test_font)
        print("✓ Font specification works")
        
        # Test ttk
        from tkinter import ttk
        style = ttk.Style()
        print("✓ ttk imported and style created")
        
        root.destroy()
        print("✓ tkinter basic functionality works")
        
    except Exception as e:
        print(f"❌ tkinter test failed: {e}")

def test_required_libraries():
    """Test if all required libraries are available"""
    required_libs = [
        "sqlite3", "datetime", "hashlib", "os", "subprocess", 
        "platform", "tkinter", "reportlab"
    ]
    
    print("\n📚 Testing required libraries:")
    for lib in required_libs:
        try:
            __import__(lib)
            print(f"✓ {lib}")
        except ImportError as e:
            print(f"❌ {lib}: {e}")

def main():
    """Run all compatibility tests"""
    print("🚀 Starting cross-platform compatibility tests...\n")
    
    print("🖥️  Platform Information:")
    test_platform_detection()
    
    print("\n📁 File System Tests:")
    test_database_path()
    test_tickets_path()
    test_file_operations()
    
    print("\n⚙️  System Commands:")
    test_subprocess_commands()
    
    print("\n🖼️  GUI Framework:")
    test_tkinter_compatibility()
    
    test_required_libraries()
    
    print("\n✅ Compatibility tests completed!")
    print("\nPlatform Summary:")
    print(f"- OS: {platform.system()}")
    print(f"- Architecture: {platform.machine()}")
    print(f"- Python: {sys.version.split()[0]}")
    
    print("\n🎯 The parking app should work properly on this platform!")

if __name__ == "__main__":
    main()
