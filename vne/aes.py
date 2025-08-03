from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.exceptions import InvalidTag
import os, base64
from vne.config import engine_version

SCRIPT_AAD = engine_version.encode("utf-8")

class SaveCorruptError(Exception):
    pass

class AES:
    def __init__(self, key: bytes):
        if len(key) not in (16, 24, 32):
            raise ValueError("La clave AES debe ser de 16, 24 o 32 bytes")
        self.key = key

    def encrypt(self, data: bytes, aad: bytes = None, encode: bool = False) -> bytes:
        iv = os.urandom(12)  # recomendado para GCM
        encryptor = Cipher(
            algorithms.AES(self.key),
            modes.GCM(iv),
            backend=default_backend()
        ).encryptor()

        if aad:
            encryptor.authenticate_additional_data(aad)

        ciphertext = encryptor.update(data) + encryptor.finalize()
        result = iv + encryptor.tag + ciphertext

        return base64.b64encode(result) if encode else result

    def decrypt(self, data: bytes, aad: bytes = None, encoded: bool = False) -> bytes:
        try:
            raw = base64.b64decode(data) if encoded else data
            iv, tag, ciphertext = raw[:12], raw[12:28], raw[28:]

            decryptor = Cipher(
                algorithms.AES(self.key),
                modes.GCM(iv, tag),
                backend=default_backend()
            ).decryptor()

            if aad:
                decryptor.authenticate_additional_data(aad)

            return decryptor.update(ciphertext) + decryptor.finalize()

        except InvalidTag:
            raise SaveCorruptError("Corrupted file or invalid key")
