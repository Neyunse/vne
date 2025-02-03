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
    Empaqueta el juego ubicado en 'game_path' generando:
      - Una carpeta 'dist' en el directorio actual.
      - Dentro de 'dist', se crea una carpeta con el mismo nombre del juego.
      - Se copia todo el contenido del juego a esa carpeta, pero en lugar de copiar la carpeta 'data',
        se la comprime en un archivo 'data.pkg'.
      
    Esto permite generar un paquete con todos los recursos y archivos necesarios para distribuir el juego.
    """
    print(f"Empaquetando juego desde {game_path}...")
    
    # Determinar ruta absoluta del juego y del directorio de distribución.
    game_path = os.path.abspath(game_path)
    game_name = os.path.basename(game_path)
    current_dir = os.getcwd()
    dist_dir = os.path.join(current_dir, "dist")
    
    # Crear el directorio 'dist' si no existe.
    if not os.path.exists(dist_dir):
        os.makedirs(dist_dir)
    
    # Definir la carpeta de destino dentro de 'dist'
    dest_path = os.path.join(dist_dir, game_name)
    
    # Si la carpeta de destino ya existe, se elimina.
    if os.path.exists(dest_path):
        shutil.rmtree(dest_path)
    os.makedirs(dest_path)
    
    # Recorrer todos los elementos en la carpeta del juego.
    for item in os.listdir(game_path):
        s = os.path.join(game_path, item)
        d = os.path.join(dest_path, item)
        
        # Si es la carpeta 'data', la comprimimos en 'data.pkg'
        if os.path.isdir(s) and item.lower() == "data":
            pkg_path = os.path.join(dest_path, "data.pkg")
            print(f"Empaquetando carpeta 'data' en {pkg_path}...")
            with zipfile.ZipFile(pkg_path, "w", zipfile.ZIP_DEFLATED) as pkg:
                for root, dirs, files in os.walk(s):
                    for file in files:
                        file_path = os.path.join(root, file)
                        # Se obtiene la ruta relativa para mantener la estructura
                        rel_path = os.path.relpath(file_path, s)
                        pkg.write(file_path, rel_path)
        else:
            # Si es una carpeta (que no sea 'data') se copia recursivamente
            if os.path.isdir(s):
                shutil.copytree(s, d)
            else:
                shutil.copy2(s, d)
    
    print(f"Juego empaquetado en: {dest_path}")

 
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