import os
import shutil
import sys
import argparse
import pyzipper
from datetime import datetime
import platform
from vne import Core
from vne import xor_data
from vne import config as CONFIG
from vne.config import key
from vne._version import __version__

engine_version = __version__

def compile_kag(source_file, target_file, key):
    """
    Reads a source file, encodes its content using an XOR operation with a given key,
    and writes the result to a target file.
    
    :param source_file: The path to the source file containing the plain text data.
    :param target_file: The file path where the compiled data will be written in binary format.
    :param key: The key used to perform XOR encryption on the data.
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
    Compiles all KAG files in the specified folder using the given key.
    
    :param data_folder: The directory path where the KAG files are located.
    :param key: The key used for encryption/decryption.
    """
    for root, dirs, files in os.walk(data_folder):
        for file in files:
            if file.endswith(".kag"):
                source_path = os.path.join(root, file)
                target_path = os.path.splitext(source_path)[0] + ".kagc"
                compile_kag(source_path, target_path, key)


def create_data_pkg(source_folder, output_pkg):
    """
    Recursively packs the files in the source_folder into an encrypted ZIP archive,
    excluding single .kag files (only .kagc or other files are included).

    param source_folder: Path of the folder with the data to be packed.
    :param output_pkg: Path of the ZIP file to be created.
    """
    with pyzipper.AESZipFile(
            output_pkg,
            'w',
            compression=pyzipper.ZIP_DEFLATED,
            encryption=pyzipper.WZ_AES) as pkg:
        pkg.setpassword(key)
        for root, dirs, files in os.walk(source_folder):
            for file in files:
                
                if file.lower().endswith(".kag") and not file.lower().endswith(".kagc"):
                    continue
                file_path = os.path.join(root, file)
            
                rel_path = os.path.relpath(file_path, source_folder)
                pkg.write(file_path, rel_path)
    print(f"[create_data_pkg] '{source_folder}' packed in '{output_pkg}' (excluding .kag files)")

def init_game(game_path, project_name):
    """
    Initializes a game project by creating directories and generating necessary script files.
    
    :param game_path: The path where the game project will be initialized.
    """
    print(f"Initializing project in '{game_path}'...")
    directories = [
        f"{game_path}/data",
        f"{game_path}/data/system",
        f"{game_path}/data/scenes",
        f"{game_path}/data/images/bg",
        f"{game_path}/data/images/sprites",
        # f"{game_path}/data/audio/bgm",
        # f"{game_path}/data/audio/sfx",
        # f"{game_path}/data/ui",
        # f"{game_path}/saves",
    ]
    for d in directories:
        os.makedirs(d, exist_ok=True)
        print(f"Directory created: {d}")

    main_menu_file = os.path.join(game_path, "data", "system", "main_menu.kag")
    scenes_file = os.path.join(game_path, "data", "system", "scenes.kag")
    characters_file = os.path.join(game_path, "data", "system", "characters.kag")
    ui_file = os.path.join(game_path, "data", "system", "ui.kag")
    vars_file = os.path.join(game_path, "data", "system", "vars.kag")
    startup_file = os.path.join(game_path, "data", "startup.kag")

    # scenes
    first_scene_file = os.path.join(game_path, "data", "scenes", "first.kag")

    with open(main_menu_file, "w", encoding="utf-8") as f:
        f.write("# Main Menu\n")
        f.write("@menu\n")
        f.write("@button \"Start game\" event Scene(\"first\") \n")
        f.write("@button \"Quit\" event Quit() \n")
        f.write("@endMenu\n")

    with open(ui_file, "w", encoding="utf-8") as f:
        f.write("# set the window size. eg: @Display(800,600)\n")
        f.write("# the recomended max size is 1280x720 \n")
        f.write("@Display(800,600)\n")
        f.write("# set the game title\n")
        f.write(f"@GameTitle(\"{project_name}\")\n")
        f.write("# set the gane icon. eg. @GameIconName(\"window_icon\")\n")
        f.write("# by default window_icon. \n")
        f.write(f"# @GameIconName()\n")


    with open(startup_file, "w", encoding="utf-8") as f:
        f.write("# Game startup script\n")
        f.write("\n")
        f.write("# Load here somthing before that system files\n")
        f.write("\n")
        f.write("@LoadSystem()\n")
        f.write("\n")
        f.write("# Load here somthing after that system files\n")
        f.write("\n")
        f.write("# Load the main menu from system/\n")
        f.write("@LoadMainMenu()\n")

    with open(scenes_file, "w", encoding="utf-8") as f:
        f.write("@scene first = \"first\"")
    
    with open(characters_file, "w", encoding="utf-8") as f:
        f.write("@char K as \"Kuro\" ")
    
    with open(vars_file, "w", encoding="utf-8") as f:
        f.write("# Include variables here")

    with open(first_scene_file, "w", encoding="utf-8") as f:
        f.write("K: Hello!\n")
        f.write("K: my name is {K}.\n")
        f.write("K: start editing scenes/first.kag to add dialogues.\n")
        f.write("K: good luck in your stories.\n")
        f.write("@exit\n")

    print("Files generated successfully")

def distribute_game(game_path):
    """
    Packages a game located at the specified path by compiling data files, creating a package,
    copying necessary files to a distribution folder, and outputting the distribution location.
    
    :param game_path: The path to the directory containing the game files to be distributed.
    """
    print(f"Packaging game from '{game_path}'...")
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
    print(f"[distribute] data.pkg copied to {dest_folder}")
 
    os.unlink(pkg_path)
 
    exe_source = os.path.abspath(sys.executable)
    exe_dest = os.path.join(dest_folder, "game.exe")
    shutil.copy2(exe_source, exe_dest)
    print(f"[distribute] Binary copied: {exe_source} → {exe_dest}")

    print(f"Distribution completed at: {dest_folder}")

def run_game(game_path):
    """
    Compiles all KAG files in the specified folder and runs the game engine with the given game path in development mode.
    
    :param game_path: The path to the directory where the game files are located.
    """
    data_folder = os.path.join(game_path, "data")

    print("---------[DEVELOPER]---------")
    compile_all_kag_in_folder(data_folder, key)
    print("-----------------------------")

    engine = Core(game_path, devMode=True)
    engine.run()

def main():
    """
    Parses command line arguments to initialize, debug, or distribute a game based on the specified command.
    """
    exe_name = os.path.basename(sys.executable).lower()
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', dest="new_project", default=False, action="store_true", help="initializes a new project")
    parser.add_argument('-p', dest="project_name", default=None, type=str, help="allows you to add a name to the project if -i is present", required='-i' in sys.argv)
    
    parser.add_argument('-r', dest="debug_project", default=False, action="store_true", help="debug a project")
    parser.add_argument('-d', dest="distribute_project", default=False, action="store_true", help="distribute a project")
    
    parser.add_argument('-f', dest="project_folder", default=None, type=str, help="Project Folder (required)", required=True)
    
    args = parser.parse_args()

    isNewProject = args.new_project
    project_name = args.project_name
    debug_project = args.debug_project
    distribute_project = args.distribute_project
    project_folder = args.project_folder
    
    
    if isNewProject and project_name and project_folder and not "python.exe" in exe_name:
        init_game(project_folder, project_name)
    elif debug_project and project_folder:
        run_game(project_folder)
    elif distribute_project and project_folder and not "python.exe" in exe_name:
        distribute_game(project_folder)
    else:
        raise Exception("Mising aguments or argument is invalid")

if __name__ == "__main__":

    try:
        exe_name = os.path.basename(sys.executable).lower()
        if "game.exe" in exe_name or "game" in exe_name:
            engine = Core(os.path.abspath("."))
            engine.run()
        else:
            main()
    except Exception as e:
        traceback_template = '''Exception error:
  %(message)s\n

  %(plataform)s
  '''
        traceback_details = {
            'message' : e,
            'plataform': f"{platform.system()}-{platform.version()}"
        }

        print(traceback_template % traceback_details)
        with open('engine-error.txt', 'w') as f:
            f.write(traceback_template % traceback_details)
            f.close()
