import os
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
from base64 import b64encode, b64decode


def encrypt_sha256(input_file):
    key = get_random_bytes(16)
    cipher = AES.new(key, AES.MODE_CBC)
    input_file_path = f"downloads/{input_file}"
    name, extension = os.path.splitext(input_file_path)
    output_file = name + '_enc' + extension

    with open(input_file_path, 'rb') as file:
        data = file.read()

    ciphertext = cipher.encrypt(pad(data, AES.block_size))
    iv = b64encode(cipher.iv).decode('utf-8')
    ct = b64encode(ciphertext).decode('utf-8')

    with open(output_file, 'w') as file:
        file.write(iv)
        file.write('\n')
        file.write(ct)

    return key.hex()


def decrypt_sha256(input_file, key):
    key = bytes.fromhex(key)

    with open(input_file, 'rb') as file:
        iv = b64decode(file.readline())
        ct = b64decode(file.readline())

    cipher = AES.new(key, AES.MODE_CBC, iv=iv)
    plaintext = unpad(cipher.decrypt(ct), AES.block_size)

    name, extension = os.path.splitext(input_file)
    output_file = name.replace('_enc', '_decrypted') + extension
    with open(output_file, 'wb') as file:
        file.write(plaintext)

    return output_file
