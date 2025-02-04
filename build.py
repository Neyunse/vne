#!/usr/bin/env python
import os
import sys
import subprocess

def build_engine():
    # Verifica que main.py exista en el directorio actual.
    if not os.path.exists("main.py"):
        print("[build.py] Error: No se encontró main.py en el directorio actual.")
        sys.exit(1)
    
    # Construir el comando para PyInstaller.
    # --onefile: genera un único ejecutable.
    # --name engine: el ejecutable se llamará engine.exe (o engine en Linux/Mac).
    # --clean: limpia archivos temporales del build anterior.
    # Puedes agregar otros flags según tus necesidades (por ejemplo, --noconsole si no deseas consola).
    cmd = [
        "pyinstaller",
        "--clean",
        "engine.spec"
    ]
    
    try:
        print("[build.py] Compilando el engine con PyInstaller...")
        subprocess.check_call(cmd)
        print("[build.py] Engine compilado correctamente en la carpeta 'dist'.")
    except subprocess.CalledProcessError as e:
        print(f"[build.py] Error durante la compilación: {e}")
        sys.exit(1)

def main():
    if len(sys.argv) < 2:
        print("Uso: python build.py build")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    if command == "build":
        build_engine()
    else:
        print(f"[build.py] Comando desconocido: {command}")
        print("Uso: python build.py build")
        sys.exit(1)

if __name__ == "__main__":
    main()
