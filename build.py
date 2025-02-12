#!/usr/bin/env python
import os
import sys
import subprocess

def build_engine():
    # Verify that main.py exists in the current directory.
    if not os.path.exists("main.py"):
        print("[build.py] Error: main.py was not found in the current directory.")
        sys.exit(1)
    
    # Build the command for PyInstaller.
    # --onefile: generates a single executable.
    # --name engine: the executable will be called engine.exe (or engine on Linux/Mac).
    # --clean: cleans temporary files from the previous build.
    # You can add other flags as needed (for example, --noconsole if you do not want a console).
    cmd = [
        "pyinstaller",
        "--clean",
        "engine.spec"
    ]
    
    try:
        print("[build.py] Compiling the engine with PyInstaller...")
        subprocess.check_call(cmd)
        print("[build.py] Engine compiled successfully in the 'dist' folder.")
    except subprocess.CalledProcessError as e:
        print(f"[build.py] Error during compilation: {e}")
        sys.exit(1)

def main():
    if len(sys.argv) < 2:
        print("Usage: python build.py build")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    if command == "build":
        build_engine()
    else:
        print(f"[build.py] Unknown command: {command}")
        print("Usage: python build.py build")
        sys.exit(1)

if __name__ == "__main__":
    main()
