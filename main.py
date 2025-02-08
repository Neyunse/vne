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
    The function `compile_kag` reads a source file, encodes its content using XOR operation with a given
    key, and writes the result to a target file.
    
    :param source_file: The `source_file` parameter in the `compile_kag` function is the path to the
    source file that contains the plain text data to be compiled. This function reads the content of the
    source file, encodes it as bytes, performs an XOR operation with a given key, and then writes the
    :param target_file: The `target_file` parameter in the `compile_kag` function is the file path where
    the compiled data will be written to in binary format. This file will contain the result of XOR
    operation performed on the data read from the `source_file` using the provided `key`
    :param key: The `key` parameter in the `compile_kag` function is used as the key for performing XOR
    encryption on the data read from the source file. XOR encryption is a simple encryption algorithm
    that uses the bitwise XOR operation with a key to encrypt and decrypt data. In this case, the `key
    """
 
    with open(source_file, "r", encoding="utf-8") as sf:
        plain_text = sf.read()
    plain_bytes = plain_text.encode("utf-8")
    compiled_bytes = xor_data(plain_bytes, key)
    with open(target_file, "wb") as tf:
        tf.write(compiled_bytes)
    print(f"[compile_kag] {source_file} -> {target_file}")

def compile_all_kag_in_folder(data_folder, key):
    """
    This function compiles all KAG files in a specified folder using a given key.
    
    :param data_folder: The `data_folder` parameter in the `compile_all_kag_in_folder` function is the
    directory path where the KAG (Key Archive File) files are located. This function will recursively
    search through this folder and its subfolders to find all KAG files for compilation
    :param key: The `key` parameter in the `compile_all_kag_in_folder` function is a value that is used
    as an input for the `compile_kag` function. It is likely used for some kind of encryption or
    decryption process within the `compile_kag` function. The specific implementation of how
    """
    for root, dirs, files in os.walk(data_folder):
        for file in files:
            if file.endswith(".kag"):
                source_path = os.path.join(root, file)
                target_path = os.path.splitext(source_path)[0] + ".kagc"
                compile_kag(source_path, target_path, key)

def create_data_pkg(source_folder, output_pkg):
    """
    The function `create_data_pkg` zips files from a specified folder into a package, excluding certain
    file types.
    
    :param source_folder: The `source_folder` parameter in the `create_data_pkg` function refers to the
    directory path where the data files are located that you want to package into a zip file. This
    function will recursively walk through this folder and include all files in the zip package,
    excluding files with the extension ".kag
    :param output_pkg: The `output_pkg` parameter in the `create_data_pkg` function is the path to the
    ZIP file that will be created to package the contents of the `source_folder`. This ZIP file will
    contain all the files and directories from the `source_folder`, excluding files with the extension
    ".kag"
    """
    with zipfile.ZipFile(output_pkg, "w", zipfile.ZIP_DEFLATED) as pkg:
        for root, dirs, files in os.walk(source_folder):
            for file in files:
                if file.lower().endswith(".kag") and not file.lower().endswith(".kagc"):
                    continue  # Excluir archivos .kag sueltos
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, source_folder)
                pkg.write(file_path, rel_path)
    print(f"[create_data_pkg] '{source_folder}' empaquetada en '{output_pkg}' (excluyendo .kag)")

def init_game(game_path):
    """
    The `init_game` function initializes a game project by creating directories and generating necessary
    script files.
    
    :param game_path: The `game_path` parameter in the `init_game` function represents the path where
    the game project will be initialized. This path will be used to create directories and generate
    files for the game project
    """
    print(f"Inicializando proyecto en '{game_path}'...")
    directories = [
        f"{game_path}/data",
        f"{game_path}/data/system",
        f"{game_path}/data/scenes",
        f"{game_path}/data/images/bg",
        f"{game_path}/data/images/sprites",
        #f"{game_path}/data/audio/bgm",
        #f"{game_path}/data/audio/sfx",
        #f"{game_path}/data/ui",
        #f"{game_path}/saves",
    ]
    for d in directories:
        os.makedirs(d, exist_ok=True)
        print(f"Directorio creado: {d}")

    startup_file = os.path.join(game_path, "data", "startup.kag")
    scenes_file = os.path.join(game_path, "data","system", "scenes.kag")
    characters_file = os.path.join(game_path, "data","system", "characters.kag")
    first_scene_file = os.path.join(game_path, "data","scenes", "first.kag")


    with open(startup_file, "w", encoding="utf-8") as f:
        f.write("# Script de inicio del juego\n")
        f.write("@Load(\"system/scenes.kag\")\n")
        f.write("@Load(\"system/characters.kag\")\n")
        f.write("@process_scene first\n")

    with open(scenes_file, "w", encoding="utf-8") as f:
        f.write("@scene first = \"first\"")
    
    with open(characters_file, "w", encoding="utf-8") as f:
        f.write("@char K as \"Kuro\" ")

    with open(first_scene_file, "w", encoding="utf-8") as f:
        f.write("Hola Mundo\n")
        f.write("K: I started a new stage in this academy\n")
        f.write("K: my name is {K}.\n")
        f.write("@exit\n")

    print(f"Archivos generados correctamente")


def distribute_game(game_path):
    """
    The function `distribute_game` packages a game located at a specified path, compiles data files,
    creates a package, copies necessary files to a distribution folder, and outputs the distribution
    location.
    
    :param game_path: The `distribute_game` function takes a `game_path` parameter, which is the path to
    the directory containing the game files that need to be distributed. The function then performs a
    series of steps to package and distribute the game
    """

    print(f"Empaquetando juego desde '{game_path}'...")
    game_path = os.path.abspath(game_path)
    game_name = os.path.basename(game_path)
 
    data_folder = os.path.join(game_path, "data")
    compile_all_kag_in_folder(data_folder, key)
 
    pkg_path = os.path.join(game_path, "data.pkg")
    create_data_pkg(data_folder, pkg_path)

    current_dir = os.getcwd()
    dist_root = os.path.join(current_dir, "dist")
    if not os.path.exists(dist_root):
        os.makedirs(dist_root)
    dest_folder = os.path.join(dist_root, game_name)
    if os.path.exists(dest_folder):
        shutil.rmtree(dest_folder)
    os.makedirs(dest_folder)

    shutil.copy2(pkg_path, os.path.join(dest_folder, "data.pkg"))
    print(f"[distribute] data.pkg copiado a {dest_folder}")
 
    os.unlink(pkg_path)
 
    exe_source = os.path.abspath(sys.executable)
    exe_dest = os.path.join(dest_folder, "game.exe")
    shutil.copy2(exe_source, exe_dest)
    print(f"[distribute] Binario copiado: {exe_source} → {exe_dest}")

    print(f"Distribución completada en: {dest_folder}")

def run_game(game_path):
    """
    The function `run_game` compiles all KAG files in a specified folder and then runs the game engine
    with a specified game path in development mode.
    
    :param game_path: The `game_path` parameter is the path to the directory where the game files are
    located. It is used to locate the game data folder and run the game engine from that location
    """
 
    data_folder = os.path.join(game_path, "data")
    compile_all_kag_in_folder(data_folder, key)

    engine = Core(game_path, devMode=True)
    engine.run()

def main():
    """
    The `main` function in this Python script takes command line arguments to initialize, debug, or
    distribute a game based on the specified command.
    """
    if len(sys.argv) < 3:
        print("Uso: engine.exe [init|debug|distribute] <carpeta_del_juego>")
        sys.exit(1)
    command = sys.argv[1]
    game_path = sys.argv[2]

    if command == "init":
        init_game(game_path)
    elif command in "debug":
        run_game(game_path)
    elif command == "distribute":
        distribute_game(game_path)
    else:
        print(f"Comando desconocido: {command}")

if __name__ == "__main__":
 
    exe_name = os.path.basename(sys.executable).lower()
    if "game.exe" in exe_name or "game" in exe_name:
 
 
        engine = Core(os.path.abspath("."))
        engine.run()
    else:
     
        main()