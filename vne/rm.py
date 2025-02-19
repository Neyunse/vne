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

        raise FileNotFoundError(f"'{internal_path}' not found in data.pkg nor in '{local_path}'")

    def close(self):
        if self.zipfile:
            self.zipfile.close()
            self.zipfile = None

    def __del__(self):
        self.close()
