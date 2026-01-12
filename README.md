# Clony Bird - Terminal Version

A terminal-based Flappy Bird clone written in Python using only built-in libraries (curses).

## Features

- **Terminal-based graphics** - Works without a display (perfect for SSH/headless systems)
- **Level system** - 5 levels with increasing difficulty
- **Progressive difficulty** - Each level increases pipe speed
- **Score tracking** - Track level progress and total score
- **No external dependencies** - Uses only Python standard library

## Requirements

### To Run the Python Script:
- Python 3.6+ (with curses module - usually included)
- Linux/Unix terminal

### To Build Standalone Executable:
- Python 3.6+
- PyInstaller (will be installed automatically by build script)

## Quick Start

### Run from Source:
```bash
python3 clony_bird.py
```

### Build Standalone Executable:
```bash
chmod +x build.sh
./build.sh
```

The executable will be created in `dist/clony_bird`

### Run the Executable:
```bash
./dist/clony_bird
```

### Install System-Wide (Optional):
```bash
sudo cp dist/clony_bird /usr/local/bin/
clony_bird  # Now you can run it from anywhere
```

## Controls

- **SPACE** or **W** - Jump/Start game
- **R** - Restart after game over
- **Q** or **ESC** - Quit

## Game Mechanics

- **Levels**: 5 levels total
- **Points per Level**: 30 points needed to advance
- **Speed Progression**:
  - Level 1: Speed 1.0
  - Level 2: Speed 1.5
  - Level 3: Speed 2.0
  - Level 4: Speed 2.5
  - Level 5: Speed 3.0

## Building for Distribution

The standalone executable created by PyInstaller is a single file that includes Python and all dependencies. It can be run on any Debian Linux system (and most Linux distributions) without requiring Python to be installed.

### Manual Build Steps:
```bash
# Install PyInstaller
pip3 install pyinstaller

# Build executable
pyinstaller --onefile --name clony_bird --console clony_bird.py

# Executable will be in dist/clony_bird
```

## Troubleshooting

### Terminal too small
Make sure your terminal is at least 40x20 characters.

### Curses not available
On some systems, you may need to install python3-dev:
```bash
sudo apt-get install python3-dev
```

### Build fails
Make sure you have pip3 and Python development tools:
```bash
sudo apt-get install python3-pip python3-dev
```

## License

Free to use and modify.

