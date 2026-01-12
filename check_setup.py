#!/usr/bin/env python3
"""Quick check to verify all dependencies are installed"""
import sys

print("Checking dependencies...")
print("-" * 40)

# Check curses (required for terminal graphics)
try:
    import curses
    print("✓ curses: OK")
except ImportError:
    print("✗ curses: MISSING")
    print("  curses should be built-in on Linux/Unix systems")
    print("  If missing, install python3-dev: sudo apt-get install python3-dev")
    sys.exit(1)

# Check other built-in modules
try:
    import random
    import time
    print("✓ random: OK")
    print("✓ time: OK")
except ImportError as e:
    print(f"✗ Error: {e}")
    sys.exit(1)

print("-" * 40)
print("All dependencies are installed!")
print("You can now run: python3 clony_bird.py")
print("")
print("Controls:")
print("  SPACE or W - Jump/Start game")
print("  R - Restart after game over")
print("  Q or ESC - Quit")

