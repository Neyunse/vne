#!/usr/bin/env python
import os
import sys
import subprocess
import zipfile

def zip_folder_and_file(folder_path, file_path, zip_path):
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
      
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                full_path = os.path.join(root, file)
                
                arcname = os.path.relpath(full_path, start=os.path.dirname(folder_path))
                zipf.write(full_path, arcname)
        
         
        zipf.write(file_path, os.path.basename(file_path))

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
        
        zip_folder_and_file('./dist/lib', './dist/engine.exe', './dist/vne.zip')
    except subprocess.CalledProcessError as e:
        print(f"[build.py] Error during compilation: {e}")
        sys.exit(1)

if __name__ == "__main__":
    build_engine()
