# Quick Build Instructions

## Current Status
✅ Pip installed  
✅ Virtual environment created  
✅ PyInstaller installed in venv  

## Required: Install binutils

PyInstaller requires `objdump` from the `binutils` package. Install it with:

```bash
sudo apt-get install binutils
```

## Then Run Build

After installing binutils, simply run:

```bash
./build.sh
```

The executable will be created in `dist/clony_bird`

## Alternative: Manual Build

If you prefer to build manually:

```bash
cd /home/b0r1s/FlappyCopy
source venv/bin/activate
pyinstaller --onefile --name clony_bird --console --clean --noconfirm clony_bird.py
```

## What's Already Done

- Virtual environment: `venv/`
- PyInstaller: Installed in venv
- Build script: Updated and ready

## Next Step

Just install binutils and run the build script!

