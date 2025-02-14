import os
import pyzipper
from .xor_data import xor_data
from .config import key

class ResourceManager:
    def __init__(self, base_path, log):
        self.base_path = base_path
        self.Log = log
        self.pkg_path = os.path.join(base_path, "data.pkg")
        self.data_folder = os.path.join(base_path, "data")
        self.zipfile = None

        if os.path.exists(self.pkg_path):
            try:
                 
                self.zipfile = pyzipper.AESZipFile(self.pkg_path, "r")
         
                self.zipfile.setpassword(key)
                self.Log(f"[ResourceManager] data.pkg found at {self.pkg_path}")
            except Exception as e:
                self.Log(f"[ResourceManager] Error opening '{self.pkg_path}': {e}")
                self.zipfile = None
        else:
            self.Log(f"[ResourceManager] '{self.pkg_path}' not found. Using loose data folder.")

    def get_bytes(self, internal_path):
        """
        Reads and returns the content of a file specified by the internal path from either a
        password-protected zipfile or from the loose data folder, with fallback for alternative file names.
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
            self.Log(f"[ResourceManager] Retrying with '{zip_alt_path}'")
            if self.zipfile:
                try:
                    return self.zipfile.read(zip_alt_path)
                except KeyError:
                    pass
            local_alt = os.path.join(self.data_folder, alt_path)
            if os.path.exists(local_alt):
                with open(local_alt, "rb") as f:
                    return f.read()

        raise FileNotFoundError(f"'File not found in path '{os.path.normpath(local_path)}'")

    def get_script_bytes(self, base_name):
        """
        Retrieves and decrypts the content of a compiled script file based on a given base name.
        The compiled file should have a header line starting with "VNEFILE:".
        """
        compiled_path = base_name + ".kagc"
        try:
            file_bytes = self.get_bytes(compiled_path)
            header, encrypted_content = file_bytes.split(b'\n', 1)
             
            if not header.startswith(b"VNEFILE:"):
                raise Exception("Invalid header in compiled script.")
             
            header_content = header.decode("utf-8").strip()  
            parts = header_content.split(";")
            id_part = parts[0]
            if not id_part.startswith("VNEFILE:"):
                raise Exception("Invalid header: missing 'VNEFILE:'")
            file_identifier = id_part[len("VNEFILE:"):].strip()
 
            expected_identifier = os.path.basename(base_name)
            if file_identifier != expected_identifier:
                raise Exception(f"File identifier ('{file_identifier}') does not match expected ('{expected_identifier}').")
        
            plain_bytes = xor_data(encrypted_content, key)
            if b'\x00' in plain_bytes:
                raise Exception("The decrypted content contains null characters.")
            return plain_bytes
        except FileNotFoundError:
            raise Exception(f"[ERROR] Compiled version of the script for '{base_name}' was not found.")

    def close(self):
        if self.zipfile:
            self.zipfile.close()
            self.zipfile = None

    def __del__(self):
        self.close()
