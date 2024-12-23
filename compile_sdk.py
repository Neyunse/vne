import os
from PyInstaller.__main__ import run
import zipfile
# Paso 1: Ofuscar scripts (opcional, usando PyArmor)
def obfuscate_script(script_path):
    os.system(f'pyarmor gen {script_path}')

# Paso 2: Crear el ejecutable
def create_executable(script_path, output_name, icon_path=None):
    options = [
        '--onefile',
        '--noconsole',
        '--hidden-import=pygame',
        '--clean',
        f'--name={output_name}',
        script_path
    ]
    if icon_path:
        options.append(f'--icon={icon_path}')
    run(options)


# Ejecución del flujo
if __name__ == "__main__":
    # Ofuscar script principal
    obfuscate_script('engine.py')
    
    if os.path.exists('dist'):
        # Crear ejecutable
        create_executable(
            script_path='dist/engine.py',
            output_name='vne',
            #icon_path='icon.ico'
        )
 
        print("Empaquetado completado.")
