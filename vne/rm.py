# engine/vne/resource_manager.py

import os
import zipfile
import io

def xor_data(data: bytes, key: bytes) -> bytes:
    out = bytearray(len(data))
    key_len = len(key)
    for i, b in enumerate(data):
        out[i] = b ^ key[i % key_len]
    return bytes(out)

class ResourceManager:
    def __init__(self, data_folder="data", pkg_path="data.pkg", xor_key=b"MyXorKey"):
        self.data_folder = data_folder
        self.pkg_path = pkg_path
        self.xor_key = xor_key
        self.zipfile = None

        if os.path.exists(self.pkg_path):
            try:
                self.zipfile = zipfile.ZipFile(self.pkg_path, "r")
                print(f"[ResourceManager] data.pkg detectado en {self.pkg_path}")
            except Exception as e:
                print(f"[ResourceManager] Error al abrir '{self.pkg_path}': {e}")
                self.zipfile = None
        else:
            print(f"[ResourceManager] No se encontró '{self.pkg_path}'. Usando archivos sueltos.")

    def get_bytes(self, internal_path):
        """
        Fallback pkg -> disco. Lanza FileNotFoundError si no existe en ninguno.
        """
        # 1) pkg
        if self.zipfile:
            try:
                return self.zipfile.read(internal_path)
            except KeyError:
                pass
        # 2) disco
        local_path = os.path.join(self.data_folder, internal_path)
        if not os.path.exists(local_path):
            raise FileNotFoundError(f"No se encontró '{internal_path}' en pkg ni en '{local_path}'")
        with open(local_path, "rb") as f:
            return f.read()

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
            plain_bytes = xor_data(xor_content, self.xor_key)
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
