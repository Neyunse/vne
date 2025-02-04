import os
import shutil
import sys
import zipfile

from vne import Core
from vne import xor_data
from vne import config as CONFIG
from vne.config import key

def compile_kag(source_file, target_file, key):
    """
    'Compila' un archivo .kag a .kagc aplicando XOR para ofuscar.
    """
    with open(source_file, "r", encoding="utf-8") as sf:
        plain_text = sf.read()
    plain_bytes = plain_text.encode("utf-8")
    compiled_bytes = xor_data(plain_bytes, key)
    with open(target_file, "wb") as tf:
        tf.write(compiled_bytes)
    print(f"[compile_kag] {source_file} -> {target_file}")

def compile_all_kag_in_folder(data_folder, key):
    for root, dirs, files in os.walk(data_folder):
        for file in files:
            if file.endswith(".kag"):
                source_path = os.path.join(root, file)
                target_path = os.path.splitext(source_path)[0] + ".kagc"
                compile_kag(source_path, target_path, key)

# ----------------------------------------------------------------------------
# 4. Función para Empaquetar Recursos en data.pkg (excluyendo .kag)
# ----------------------------------------------------------------------------

def create_data_pkg(source_folder, output_pkg):
    with zipfile.ZipFile(output_pkg, "w", zipfile.ZIP_DEFLATED) as pkg:
        for root, dirs, files in os.walk(source_folder):
            for file in files:
                if file.lower().endswith(".kag") and not file.lower().endswith(".kagc"):
                    continue  # Excluir archivos .kag sueltos
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, source_folder)
                pkg.write(file_path, rel_path)
    print(f"[create_data_pkg] '{source_folder}' empaquetada en '{output_pkg}' (excluyendo .kag)")

# ----------------------------------------------------------------------------
# 5. Funciones CLI: init, run, distribute
# ----------------------------------------------------------------------------

def init_game(game_path):
    print(f"Inicializando proyecto en '{game_path}'...")
    directories = [
        f"{game_path}/data",
        f"{game_path}/data/system",
        f"{game_path}/data/scenes",
        f"{game_path}/data/images/bg",
        f"{game_path}/data/images/sprites",
        f"{game_path}/data/audio/bgm",
        f"{game_path}/data/audio/sfx",
        f"{game_path}/data/ui",
        f"{game_path}/saves",
    ]
    for d in directories:
        os.makedirs(d, exist_ok=True)
        print(f"Directorio creado: {d}")

    startup_file = os.path.join(game_path, "data", "startup.kag")
    with open(startup_file, "w", encoding="utf-8") as f:
        f.write("# Script de inicio del juego\n")
        f.write("@Load(\"system/scenes.kag\")\n")
        f.write("@Load(\"system/characters.kag\")\n")
        f.write("@process_scene first\n")
    print(f"Archivo de inicio creado: {startup_file}")

def distribute_game(game_path):
    """
    Realiza el pipeline completo de distribución para Windows:
      1) Compila los scripts .kag a .kagc usando XOR.
      2) Empaqueta la carpeta data/ en un archivo data.pkg (excluyendo los .kag).
      3) Crea una carpeta de distribución en dist/<game_folder>/ y copia allí:
         - data.pkg
         - El propio binario actual (engine.exe) renombrado a game.exe.
    """
    print(f"Empaquetando juego desde '{game_path}'...")
    game_path = os.path.abspath(game_path)
    game_name = os.path.basename(game_path)

    # 1) Compilar .kag -> .kagc en data/
    data_folder = os.path.join(game_path, "data")
    compile_all_kag_in_folder(data_folder, key)

    # 2) Empaquetar data/ en data.pkg (excluyendo .kag)
    pkg_path = os.path.join(game_path, "data.pkg")
    create_data_pkg(data_folder, pkg_path)

    # 3) Crear la carpeta de distribución en dist/<game_name>/
    current_dir = os.getcwd()
    dist_root = os.path.join(current_dir, "dist")
    if not os.path.exists(dist_root):
        os.makedirs(dist_root)
    dest_folder = os.path.join(dist_root, game_name)
    if os.path.exists(dest_folder):
        shutil.rmtree(dest_folder)
    os.makedirs(dest_folder)

    # Copiar data.pkg a la carpeta de distribución
    shutil.copy2(pkg_path, os.path.join(dest_folder, "data.pkg"))
    print(f"[distribute] data.pkg copiado a {dest_folder}")

    # elimina data.pkg de la carpeta principal
    #os.unlink(pkg_path)

    # 4) Copiar el binario actual (engine.exe) y renombrarlo a game.exe
    exe_source = os.path.abspath(sys.executable)
    exe_dest = os.path.join(dest_folder, "game.exe")
    shutil.copy2(exe_source, exe_dest)
    print(f"[distribute] Binario copiado: {exe_source} → {exe_dest}")

    print(f"Distribución completada en: {dest_folder}")

def run_game(game_path):
    """
    Ejecuta el juego en modo desarrollo.
    Se espera que game_path sea la carpeta del juego (donde están data/, etc.).
    """
 
    engine = Core(game_path)
    engine.run()

# ---------------------------------------------------------------------------
# 5. Modo de Ejecución (CLI)
# ---------------------------------------------------------------------------

def main():
    if len(sys.argv) < 3:
        print("Uso: engine.exe [init|run|distribute] <carpeta_del_juego>")
        sys.exit(1)
    command = sys.argv[1]
    game_path = sys.argv[2]

    if command == "init":
        init_game(game_path)
    elif command in ("run", "debug"):
        run_game(game_path)
    elif command == "distribute":
        distribute_game(game_path)
    else:
        print(f"Comando desconocido: {command}")

if __name__ == "__main__":
    # Si el binario se llama game.exe, se asume que es la versión final
    exe_name = os.path.basename(sys.executable).lower()
    if "game.exe" in exe_name or "game" in exe_name:
        # Modo juego: ejecutar directamente (en producción)
 
        engine = Core(os.path.abspath("."))
        engine.run()
    else:
        # Modo SDK: mostrar CLI
        main()