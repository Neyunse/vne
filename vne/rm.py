# engine/vne/resource_manager.py

import os
import zipfile
import io
from .xor_data import xor_data
from .config import key
class ResourceManager:
    def __init__(self, base_path):
        """
        base_path: Carpeta donde se encuentra el ejecutable final (game.exe o engine.exe)
        Se espera que en esta carpeta existan:
          - data.pkg (opcional)
          - data/ (como fallback)
        """
        self.base_path = base_path
        self.pkg_path = os.path.join(base_path, "data.pkg")
        self.data_folder = os.path.join(base_path, "data")
        self.zipfile = None

        if os.path.exists(self.pkg_path):
            try:
                self.zipfile = zipfile.ZipFile(self.pkg_path, "r")
                print(f"[ResourceManager] data.pkg encontrado en {self.pkg_path}")
            except Exception as e:
                print(f"[ResourceManager] Error al abrir '{self.pkg_path}': {e}")
                self.zipfile = None
        else:
            print(f"[ResourceManager] No se encontró '{self.pkg_path}'. Se usará la carpeta data/ suelta.")

    def get_bytes(self, internal_path):
        # Normalizar la ruta para el ZIP: reemplazar os.sep por "/"
        zip_internal_path = internal_path.replace(os.sep, "/")
        
        # Intentar primero en data.pkg
        if self.zipfile:
            try:
                return self.zipfile.read(zip_internal_path)
            except KeyError:
                pass

        # Intentar en la carpeta data/ suelta
        local_path = os.path.join(self.data_folder, internal_path)
        if os.path.exists(local_path):
            with open(local_path, "rb") as f:
                return f.read()

        # Si no se encontró y la ruta termina en .kag, intentar con .kagc
        if internal_path.lower().endswith(".kag"):
            alt_path = internal_path[:-4] + ".kagc"
            zip_alt_path = alt_path.replace(os.sep, "/")
            print(f"[ResourceManager] Reintentando con '{zip_alt_path}'")
            if self.zipfile:
                try:
                    return self.zipfile.read(zip_alt_path)
                except KeyError:
                    pass
            local_alt = os.path.join(self.data_folder, alt_path)
            if os.path.exists(local_alt):
                with open(local_alt, "rb") as f:
                    return f.read()

        raise FileNotFoundError(f"No se encontró '{internal_path}' ni en data.pkg ni en '{local_path}'")


    def get_script_bytes(self, base_name):
        """
        Intenta cargar el script compilado (<base_name>.kagc) y lo descifra usando XOR.
        Si no se encuentra, lanza un error.
        """
        compiled_path = base_name + ".kagc"
        try:
            xor_content = self.get_bytes(compiled_path)
            plain_bytes = xor_data(xor_content, key)
            # Opcional: Validar que el contenido descifrado sea correcto
            if b'\x00' in plain_bytes:
                raise Exception("El contenido descifrado contiene caracteres nulos.")
            return plain_bytes
        except FileNotFoundError:
            raise Exception(f"[ERROR] No se encontró la versión compilada del script para '{base_name}'.")



    def close(self):
        if self.zipfile:
            self.zipfile.close()
            self.zipfile = None

    def __del__(self):
        self.close()
