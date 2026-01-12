#!/bin/bash
# Verify build environment for Flappy Bird

echo "Verifying build environment..."
echo ""

ERRORS=0

# Check Python
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo "✓ Python found: $PYTHON_VERSION"
else
    echo "✗ Python3 not found"
    ERRORS=$((ERRORS + 1))
fi

# Check pip
if command -v pip3 &> /dev/null; then
    echo "✓ pip3 found"
elif command -v pip &> /dev/null; then
    echo "✓ pip found"
else
    echo "⚠ pip/pip3 not found (may need to install python3-pip)"
    # Don't count as error, build script can handle it
fi

# Check PyInstaller
if command -v pyinstaller &> /dev/null; then
    PYINSTALLER_VERSION=$(pyinstaller --version)
    echo "✓ PyInstaller found: $PYINSTALLER_VERSION"
else
    echo "⚠ PyInstaller not found (will be installed by build script)"
fi

# Check if source file exists
if [ -f "clony_bird.py" ]; then
    echo "✓ Source file found: clony_bird.py"
else
    echo "✗ Source file not found: clony_bird.py"
    ERRORS=$((ERRORS + 1))
fi

# Check Python syntax
if python3 -m py_compile clony_bird.py 2>/dev/null; then
    echo "✓ Python syntax check passed"
else
    echo "✗ Python syntax errors found"
    ERRORS=$((ERRORS + 1))
fi

echo ""
if [ $ERRORS -eq 0 ]; then
    echo "✓ Build environment is ready!"
    echo "Run './build.sh' to create the executable"
    exit 0
else
    echo "✗ Build environment has $ERRORS error(s)"
    echo "Please fix the issues above before building"
    exit 1
fi

