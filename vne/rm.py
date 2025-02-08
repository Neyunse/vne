import os
import zipfile
import io
from .xor_data import xor_data
from .config import key
class ResourceManager:
    def __init__(self, base_path):

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
        The function `get_bytes` reads and returns the content of a file specified by the internal path
        from either a zipfile or a local file system, with a fallback mechanism for specific file
        extensions.
        
        :param internal_path: The `get_bytes` method you provided is a part of a class that seems to be
        responsible for reading bytes from a zip file or a local file system. The method first converts
        the `internal_path` to a format compatible with zip file paths, then attempts to read the file
        from the zip file
        :return: The `get_bytes` method returns the bytes of the file located at the specified
        `internal_path`. If the file is found within a zipfile, it reads and returns the bytes from the
        zipfile. If the file is not found in the zipfile, it checks the local file system and returns
        the bytes from the local file if found. If the `internal_path` ends with ".kag", it also
        """
   
        zip_internal_path = internal_path.replace(os.sep, "/")
        
  
        if self.zipfile:
            try:
                return self.zipfile.read(zip_internal_path)
            except KeyError:
                pass


        local_path = os.path.join(self.data_folder, internal_path)
        if os.path.exists(local_path):
            with open(local_path, "rb") as f:
                return f.read()

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
        The function `get_script_bytes` retrieves and decrypts the content of a compiled script file
        based on a given base name.
        
        :param base_name: The `base_name` parameter in the `get_script_bytes` method is a string that
        represents the base name of the script file. It is used to construct the path to the compiled
        script file by appending ".kagc" to the base name. For example, if `base_name` is
        :return: the decrypted content of a script file after extracting and verifying its header
        information.
        """
 
        compiled_path = base_name + ".kagc"
        try:
            file_bytes = self.get_bytes(compiled_path)
        
            header, encrypted_content = file_bytes.split(b'\n', 1)
             
            if not header.startswith(b"VNEFILE:"):
                raise Exception("Header inválido en el script compilado.")
             
            header_content = header.decode("utf-8").strip()  
            parts = header_content.split(";")
            id_part = parts[0]   
            if not id_part.startswith("VNEFILE:"):
                raise Exception("Header inválido: falta 'VNEFILE:'")
            file_identifier = id_part[len("VNEFILE:"):].strip()
 
            expected_identifier = os.path.basename(base_name)
            if file_identifier != expected_identifier:
                raise Exception(f"Identificador del archivo ('{file_identifier}') no coincide con lo esperado ('{expected_identifier}').")
        
            plain_bytes = xor_data(encrypted_content, key)
            if b'\x00' in plain_bytes:
                raise Exception("El contenido descifrado contiene caracteres nulos.")
            return plain_bytes
        except FileNotFoundError:
            raise Exception(f"[ERROR] No se encontró la versión compilada del script para '{base_name}'.")



    def close(self):
        """
        The `close` function closes the `zipfile` attribute if it is not `None`.
        """
        if self.zipfile:
            self.zipfile.close()
            self.zipfile = None

    def __del__(self):
        """
        The above function is a destructor method in Python that closes resources when an object is
        deleted.
        """
        self.close()
