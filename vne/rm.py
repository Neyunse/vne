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
        """
        Intenta leer 'internal_path' desde data.pkg; si no se encuentra, busca en data/.
        Ejemplo: internal_path = "scenes/startup.kagc" o "startup.kag"
        """
        if self.zipfile:
            try:
                return self.zipfile.read(internal_path)
            except KeyError:
                pass
        local_path = os.path.join(self.data_folder, internal_path)
        if os.path.exists(local_path):
            with open(local_path, "rb") as f:
                return f.read()
        raise FileNotFoundError(f"No se encontró '{internal_path}' ni en data.pkg ni en '{local_path}'")
    def get_script_bytes(self, base_name):
            """
            Primero <base_name>.kagc (XOR); si no existe, fallback <base_name>.kag (texto).
            """
            compiled_path = base_name + ".kagc"
            uncompiled_path = base_name + ".kag"
            # 1) Intentar .kagc
            try:
                xor_content = self.get_bytes(compiled_path)  # bytes ofuscados
                # Deshacer XOR
                plain_bytes = xor_data(xor_content, key)
                return plain_bytes
            except FileNotFoundError:
                # fallback .kag
                return self.get_bytes(uncompiled_path)

    def close(self):
        if self.zipfile:
            self.zipfile.close()
            self.zipfile = None

    def __del__(self):
        self.close()
