# Build Instructions

## Prerequisites

To build the standalone executable, you need to install `python3-pip` first:

```bash
sudo apt-get update
sudo apt-get install python3-pip
```

## Building the Executable

Once pip is installed, run:

```bash
./build.sh
```

Or manually:

```bash
# Install PyInstaller
pip3 install --user pyinstaller

# Build executable
pyinstaller --onefile --name clony_bird --console clony_bird.py

# The executable will be in dist/clony_bird
```

## Alternative: Using System Python3-pip Package

If you prefer to use the system package manager:

```bash
sudo apt-get install python3-pip
pip3 install --user pyinstaller
./build.sh
```

## Note

The build process requires pip to install PyInstaller. If you don't have sudo access, you may need to:
1. Ask your system administrator to install python3-pip
2. Or use a virtual environment if you have user-level Python package installation capabilities

