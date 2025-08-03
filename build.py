#!/usr/bin/env python
import os
import sys
import subprocess
import zipfile
import platform

def zip_folders_and_files(folders, files, zip_path):
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
 
        if folders:
            for folder_path in folders:
                if folder_path and os.path.isdir(folder_path):
                    for root, dirs, folder_files in os.walk(folder_path):
                        for file in folder_files:
                            full_path = os.path.join(root, file)
                            arcname = os.path.relpath(full_path, start=os.path.dirname(folder_path))
                            zipf.write(full_path, arcname)

 
        if files:
            for file_path in files:
                if file_path and os.path.isfile(file_path):
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

def buildDoc():
    return [
        "sphinx-build",
        "-b",
        "dirhtml",
        "-E",
        "-a",
        "./sphinx/source",
        "./dist/docs"
    ]

def build_engine():
    # Verify that main.py exists in the current directory.
    if not os.path.exists("main.py"):
        print("[build.py] Error: main.py was not found in the current directory.")
        sys.exit(1)
    
    try:
        engine = build()
        bootstrapper = build("bootstrapper")
        doc = buildDoc()
        
        
        print("[build.py] Compiling the engine with PyInstaller...")
        subprocess.check_call(engine)
        print("[build.py] Engine compiled successfully in the 'dist' folder.")
        
        print("[build.py] Compiling the bootstrapper with PyInstaller...")
        subprocess.check_call(bootstrapper)
        print("[build.py] Engine compiled successfully in the 'dist' folder.")
        
        print("[build.py] Building local documentation")
        subprocess.check_call(doc)
        print("[build.py] The documentation was correctly constructed")
        
        if platform.system() == "Windows":
            print("[build.py] Zipping the engine and documentation...")
            zip_folders_and_files(['./dist/lib', './dist/docs'], ['./dist/engine.exe'], f'./dist/vne-{platform.architecture()[0]}-{platform.system()}.zip')
        else:
            print("[build.py] Zipping the engine and documentation for non-Windows platforms...")
            zip_folders_and_files(['./dist/lib', './dist/docs'], ['./dist/engine'], f'./dist/vne-{platform.architecture()[0]}-{platform.system()}.zip')
        
    except subprocess.CalledProcessError as e:
        print(f"[build.py] Error during compilation: {e}")
        sys.exit(1)

if __name__ == "__main__":
    build_engine()