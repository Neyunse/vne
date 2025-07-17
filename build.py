#!/usr/bin/env python
import os
import sys
import subprocess

def build(spec="engine"):
    if spec == "bootstrapper":
        return [
        "pyinstaller",
        "--clean",
        "--distpath",
        "./dist/lib/win",
        "--workpath",
        "./build",
        f"{spec}.spec"
    ]
        
    return [
        "pyinstaller",
        "--clean",
        f"{spec}.spec"
    ]

def build_engine():
    # Verify that main.py exists in the current directory.
    if not os.path.exists("main.py"):
        print("[build.py] Error: main.py was not found in the current directory.")
        sys.exit(1)
    
    try:
        engine = build()
        bootstrapper = build("bootstrapper")
        
        
        print("[build.py] Compiling the engine with PyInstaller...")
        subprocess.check_call(engine)
        print("[build.py] Engine compiled successfully in the 'dist' folder.")
        
        print("[build.py] Compiling the bootstrapper with PyInstaller...")
        subprocess.check_call(bootstrapper)
        print("[build.py] Engine compiled successfully in the 'dist' folder.")
    except subprocess.CalledProcessError as e:
        print(f"[build.py] Error during compilation: {e}")
        sys.exit(1)

if __name__ == "__main__":
    build_engine()
