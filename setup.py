#!/usr/bin/env python3
"""
Setup script for PDF Adjective Counter
Easy installation and dependency checking
"""

import sys
import subprocess
import os
from pathlib import Path

def check_python_version():
    """Check if Python version is 3.7+"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print(f"❌ Error: Python 3.7+ required (you have {version.major}.{version.minor})")
        sys.exit(1)
    print(f"✓ Python {version.major}.{version.minor} detected")

def install_requirements():
    """Install required packages"""
    print("\n📦 Installing required packages...")
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ])
        print("✓ All packages installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install packages")
        print("Try manually: pip install -r requirements.txt")
        return False

def test_imports():
    """Test if all required modules can be imported"""
    print("\n🔍 Testing imports...")
    required = ["pandas", "PyPDF2", "xlsxwriter"]
    failed = []
    
    for module in required:
        try:
            __import__(module)
            print(f"  ✓ {module}")
        except ImportError:
            print(f"  ❌ {module}")
            failed.append(module)
    
    return len(failed) == 0

def create_output_directory():
    """Create default output directory"""
    output_dir = Path("output")
    if not output_dir.exists():
        output_dir.mkdir()
        print(f"\n📁 Created output directory: {output_dir.absolute()}")
    else:
        print(f"\n📁 Output directory exists: {output_dir.absolute()}")

def test_tool():
    """Run a basic test of the tool"""
    print("\n🧪 Testing the tool...")
    try:
        result = subprocess.run([
            sys.executable, "pdf_adjective_counter.py", "--version"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✓ Tool is working correctly")
            print(f"  Version: {result.stdout.strip()}")
            return True
        else:
            print("⚠️  Tool test had issues")
            return False
    except Exception as e:
        print(f"⚠️  Could not test tool: {e}")
        return False

def print_usage():
    """Print usage instructions"""
    print("\n" + "="*60)
    print("🎉 Setup Complete!")
    print("="*60)
    print("\n📖 Quick Start Guide:\n")
    print("1. Simple mode (edit settings in file):")
    print("   - Edit pdf_adjective_counter.py")
    print("   - Set INPUT_PATHS to your PDF folder")
    print("   - Run: python3 pdf_adjective_counter.py\n")
    print("2. Command line mode:")
    print("   python3 pdf_adjective_counter.py /path/to/pdfs -o results.xlsx\n")
    print("3. Get help:")
    print("   python3 pdf_adjective_counter.py --help\n")
    print("📚 See README.md for full documentation")
    print("❓ See FAQ.md for common questions")
    print("="*60)

def main():
    """Main setup process"""
    print("="*60)
    print("PDF Adjective Counter - Setup")
    print("="*60)
    
    # Check Python version
    check_python_version()
    
    # Install requirements
    success = install_requirements()
    
    if success:
        # Test imports
        if test_imports():
            # Create output directory
            create_output_directory()
            
            # Test tool
            test_tool()
            
            # Print usage
            print_usage()
        else:
            print("\n⚠️  Some imports failed. Please install manually:")
            print("pip install -r requirements.txt")
    
    print("\nSetup script finished.\n")

if __name__ == "__main__":
    main()
