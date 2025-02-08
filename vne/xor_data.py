def xor_data(data: bytes, key: bytes) -> bytes:
    """
    The `xor_data` function applies XOR operation to the input data using a given key.
    
    :param data: The `data` parameter in the `xor_data` function represents the input bytes that you
    want to apply the XOR operation to. This could be any binary data that you want to encrypt or
    decrypt using XOR
    :type data: bytes
    :param key: The `key` parameter in the `xor_data` function is a bytes object representing the key
    used for XOR encryption. It is used to XOR each byte of the `data` parameter with the corresponding
    byte of the key. The key can be of any length, and if the key is shorter than
    :type key: bytes
    :return: The function `xor_data` takes two byte strings as input - `data` and `key`, and applies XOR
    operation between each byte of `data` and the corresponding byte of `key`. If the length of `key` is
    shorter than the length of `data`, the key is repeated cyclically. The result of the XOR operation
    is stored in a `bytearray` named `out`,
    """ 
    out = bytearray(len(data))
    key_len = len(key)
    for i, b in enumerate(data):
        out[i] = b ^ key[i % key_len]
    return bytes(out)