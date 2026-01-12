#!/bin/bash
# Build script for Flappy Bird - Creates standalone executable

set -e

# Add user's local bin to PATH if pip/pyinstaller installed with --user
export PATH="$HOME/.local/bin:$PATH"

echo "=========================================="
echo "Flappy Bird - Build Script"
echo "=========================================="
echo ""

# Check for binutils (required for PyInstaller on Linux)
if ! command -v objdump &> /dev/null; then
    echo "objdump (binutils) is required but not found."
    echo "Attempting to install binutils..."
    sudo apt-get install -y binutils 2>/dev/null || {
        echo "Could not install binutils automatically."
        echo "Please install it manually: sudo apt-get install binutils"
        exit 1
    }
fi

# Check if virtual environment exists, if not create one
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Check if PyInstaller is installed
if ! command -v pyinstaller &> /dev/null; then
    echo "PyInstaller is not installed."
    echo "Installing PyInstaller..."
    
    # Try to ensure pip is available first
    if ! command -v pip3 &> /dev/null && ! command -v pip &> /dev/null; then
        echo "pip not found. Attempting to bootstrap pip..."
        python3 -m ensurepip --user 2>/dev/null || {
            echo "Could not bootstrap pip. Please install python3-pip:"
            echo "  sudo apt-get install python3-pip"
            exit 1
        }
    fi
    
    # Install PyInstaller in virtual environment (no --user needed in venv)
    echo "Installing PyInstaller in virtual environment..."
    pip install pyinstaller
    
    # Check if installation was successful
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to install PyInstaller"
        exit 1
    fi
    
    # Verify installation
    if ! command -v pyinstaller &> /dev/null; then
        echo "ERROR: Failed to install PyInstaller. Please install manually:"
        echo "  source venv/bin/activate && pip install pyinstaller"
        exit 1
    fi
fi

echo "Building standalone executable..."
echo ""

# Check if spec file exists, use it if available
if [ -f "clony_bird.spec" ]; then
    echo "Using clony_bird.spec file..."
    pyinstaller --clean --noconfirm clony_bird.spec
else
    echo "Building with default settings..."
# Build with PyInstaller
pyinstaller --onefile \
    --name clony_bird \
    --console \
    --clean \
    --noconfirm \
    clony_bird.py
fi

if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "Build successful!"
    echo "=========================================="
    echo ""
    echo "Executable location: dist/clony_bird"
    echo ""
    echo "To run the game:"
    echo "  ./dist/clony_bird"
    echo ""
    echo "To copy to system path (optional):"
    echo "  sudo cp dist/clony_bird /usr/local/bin/"
    echo ""
else
    echo ""
    echo "Build failed. Please check the error messages above."
    exit 1
fi

