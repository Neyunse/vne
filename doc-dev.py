#!/usr/bin/env python
import os
import sys
import subprocess

if __name__ == "__main__":
    cmd = [
        "sphinx-autobuild",
        "-E",
        "-a",
    
        "./sphinx/source",
        "./docs"
    ]

    try:
        print("[doc-dev.py] Preview doc...")
        subprocess.check_call(cmd)
 
    except subprocess.CalledProcessError as e:
        print(f"[build.py] Error during compilation: {e}")
        sys.exit(1)