#!/usr/bin/env python
import os
import sys
import subprocess
import zipfile

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

def package_platform(platform_name, bin_path, extra_files=None, extra_folders=None, is_engine=False):
    dist_dir = f'./dist/{platform_name}'
    os.makedirs(dist_dir, exist_ok=True)
    import shutil
    # Si es el engine, va directo en dist/<plataforma>
    if is_engine and os.path.isfile(bin_path):
        dest_bin = os.path.join(dist_dir, os.path.basename(bin_path))
        if os.path.abspath(bin_path) != os.path.abspath(dest_bin):
            shutil.copy2(bin_path, dest_bin)
    # Si es bootstrapper, va en dist/lib/<plataforma>
    elif not is_engine and os.path.isfile(bin_path):
        lib_dir = os.path.join(dist_dir, "lib")
        plat_lib_dir = os.path.join(lib_dir, platform_name)
        os.makedirs(plat_lib_dir, exist_ok=True)
        dest_bin = os.path.join(plat_lib_dir, os.path.basename(bin_path))
        if os.path.abspath(bin_path) != os.path.abspath(dest_bin):
            shutil.copy2(bin_path, dest_bin)
    # Copia archivos extra
    if extra_files:
        for f in extra_files:
            if os.path.isfile(f):
                shutil.copy2(f, dist_dir)
    # Copia carpetas extra
    if extra_folders:
        for folder in extra_folders:
            if os.path.isdir(folder):
                dest_folder = os.path.join(dist_dir, os.path.basename(folder))
                if os.path.abspath(folder) != os.path.abspath(dest_folder):
                    shutil.copytree(folder, dest_folder, dirs_exist_ok=True)
    # Empaqueta en zip
    zip_folders_and_files([dist_dir], [], f'./dist/{platform_name}.zip')

def build(spec="engine", platform_name=None):
    # Permite especificar distpath por plataforma
    distpath = f"./dist/lib/{platform_name}" if platform_name else "./dist/lib/win"
    args = [
        "pyinstaller",
        "--clean",
        "--distpath",
        distpath,
        "--workpath",
        "./build",
        f"{spec}.spec"
    ]
    return args

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
    # Verifica main.py y bootstrapper.py
    if not os.path.exists("main.py"):
        print("[build.py] Error: main.py was not found in el directorio actual.")
        sys.exit(1)
    if not os.path.exists("bootstrapper.py"):
        print("[build.py] Error: bootstrapper.py was not found in el directorio actual.")
        sys.exit(1)
    try:
        # Documentación
        print("[build.py] Building local documentation")
        subprocess.check_call(buildDoc())
        print("[build.py] The documentation was correctly constructed")
        # Compilación por plataforma
        platforms = {
            "win": {
                "main": {
                    "spec": "engine",
                    "bin": "./dist/lib/win/engine.exe",
                    "extra_files": [],
                    "extra_folders": ["./dist/docs"]
                },
                "bootstrapper": {
                    "spec": "bootstrapper",
                    "bin": "./dist/lib/win/bootstrapper.exe",
                    "extra_files": [],
                    "extra_folders": ["./dist/docs"]
                }
            },
            "linux": {
                "main": {
                    "spec": "engine",
                    "bin": "./dist/lib/linux/engine",
                    "extra_files": [],
                    "extra_folders": ["./dist/docs"]
                },
                "bootstrapper": {
                    "spec": "bootstrapper",
                    "bin": "./dist/lib/linux/bootstrapper",
                    "extra_files": [],
                    "extra_folders": ["./dist/docs"]
                }
            },
            "mac": {
                "main": {
                    "spec": "engine",
                    "bin": "./dist/lib/mac/engine",
                    "extra_files": [],
                    "extra_folders": ["./dist/docs"]
                },
                "bootstrapper": {
                    "spec": "bootstrapper",
                    "bin": "./dist/lib/mac/bootstrapper",
                    "extra_files": [],
                    "extra_folders": ["./dist/docs"]
                }
            }
        }
        # Compila y empaqueta para cada plataforma y ejecutable
        for plat, infos in platforms.items():
            # Primero engine
            info_engine = infos.get("main")
            if info_engine:
                print(f"[build.py] Compiling engine for {plat}...")
                args = build(info_engine["spec"], plat)
                subprocess.check_call(args)
                print(f"[build.py] Engine for {plat} compiled successfully.")
                package_platform(plat, info_engine["bin"], info_engine["extra_files"], info_engine["extra_folders"], is_engine=True)
                print(f"[build.py] Distribution for {plat} (engine) packaged.")
            # Luego bootstrapper
            info_boot = infos.get("bootstrapper")
            if info_boot:
                print(f"[build.py] Compiling bootstrapper for {plat}...")
                args = build(info_boot["spec"], plat)
                subprocess.check_call(args)
                print(f"[build.py] Bootstrapper for {plat} compiled successfully.")
                package_platform(plat, info_boot["bin"], info_boot["extra_files"], info_boot["extra_folders"], is_engine=False)
                print(f"[build.py] Distribution for {plat} (bootstrapper) packaged.")
     
    except subprocess.CalledProcessError as e:
        print(f"[build.py] Error during compilation: {e}")
        sys.exit(1)

if __name__ == "__main__":
    build_engine()
