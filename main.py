import os
import shutil
import sys
import zipfile

from vne.core import VNEngine as Core


def init_game(game_path):
    print(f"Inicializando proyecto en {game_path}...")
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

    # Crea un archivo startup.kag de ejemplo con directivas avanzadas
    startup_file = f"{game_path}/data/startup.kag"
    with open(startup_file, "w", encoding="utf-8") as f:
        f.write("# Load initial configurations\n\n")
        f.write("# Carga/importa las definiciones de las escenas\n")
        f.write("@Load(\"system/scenes.kag\")\n")
        f.write("# Carga/importa las definiciones de los personajes\n")
        f.write("@Load(\"system/characters.kag\")\n\n")
        f.write("# Llama/procesa/importa la primera escena\n")
        f.write("@process_scene first | system/scenes.kag: @scene first = \"first\" | system/characters.kag:\n")
        f.write("@char K as \"Kuro\"\n")
        f.write("# También se puede asignar un nombre personalizado\n")
        f.write("# @char Kuro as \"Kuro\". Las escenas con diálogos deben ir dentro de la carpeta /scenes/*\n")
    print(f"Archivo de inicio creado: {startup_file}")

def distribute_game(game_path):
    """
    1) (Opcional) compila scripts .kag -> .kagc
    2) crea data.pkg
    3) copia binario actual (engine.exe) renombrado a game.exe
    """
    import os
    import shutil
    import sys
    import zipfile

    # game_path absoluto
    game_path = os.path.abspath(game_path)
    data_folder = os.path.join(game_path, "data")

    # 1) compila (si así lo deseas)
    compile_all_kag_in_folder(data_folder)

    # 2) empaquetar data/
    pkg_path = os.path.join(game_path, "data.pkg")
    with zipfile.ZipFile(pkg_path, "w", zipfile.ZIP_DEFLATED) as pkg:
        for root, dirs, files in os.walk(data_folder):
            for file in files:
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, data_folder)
                pkg.write(file_path, rel_path)

    # 3) copiar engine.exe renombrado a game.exe
    exe_source = os.path.abspath(sys.executable)  # El binario actual
    exe_dest = os.path.join(game_path, "game.exe")
    shutil.copy2(exe_source, exe_dest)

    print(f"¡Distribución completada! El usuario final puede ejecutar 'game.exe' en '{game_path}' junto a data.pkg.")
 
def xor_data(data: bytes, key: bytes) -> bytes:
    out = bytearray(len(data))
    key_len = len(key)
    for i, b in enumerate(data):
        out[i] = b ^ key[i % key_len]
    return bytes(out)

def compile_kag(source_file, target_file, key=b"MyXorKey"):
    """
    'Compila' un .kag -> .kagc usando XOR con la clave dada.
    """
    with open(source_file, "r", encoding="utf-8") as sf:
        plain_text = sf.read()
    # Convertir el texto a bytes
    plain_bytes = plain_text.encode("utf-8")
    # Ofuscar con XOR
    compiled_bytes = xor_data(plain_bytes, key)
    # Guardar .kagc en binario
    with open(target_file, "wb") as tf:
        tf.write(compiled_bytes)

def compile_all_kag_in_folder(data_folder, key=b"MyXorKey"):
    for root, dirs, files in os.walk(data_folder):
        for file in files:
            if file.endswith(".kag"):
                source_path = os.path.join(root, file)
                target_path = os.path.splitext(source_path)[0] + ".kagc"
                print(f"Compilando {source_path} -> {target_path} con XOR")
                compile_kag(source_path, target_path, key=key)


if __name__ == "__main__":

    if len(sys.argv) < 3:
        print("Uso: python run.py [init|run|distribute] <carpeta>")
        sys.exit(1)
    
    command = sys.argv[1]
    game_path = sys.argv[2]
    project_folder = os.path.join(os.path.dirname(__file__), sys.argv[2])
    data_folder = os.path.join(os.path.dirname(__file__), sys.argv[2], "data")

    
    if command in ("debug"):
        core = Core(project_folder)
        compile_all_kag_in_folder(data_folder, key=b"MyXorKey")
        core.run()
    elif command == "init":
        init_game(project_folder)
    elif command == "distribute":
        distribute_game(project_folder)
    else:
        print(f"Comando desconocido: {command}")