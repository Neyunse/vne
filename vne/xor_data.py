def xor_data(data: bytes, key: bytes) -> bytes:
    """Aplica XOR a los datos con la clave dada."""
    out = bytearray(len(data))
    key_len = len(key)
    for i, b in enumerate(data):
        out[i] = b ^ key[i % key_len]
    return bytes(out)