import os
from Crypto.Cipher import Blowfish
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes


def encrypt_file_blowfish(input_file):
    key = get_random_bytes(16)
    with open(f'downloads/{input_file}', 'rb') as file:
        data = file.read()

    cipher = Blowfish.new(key, Blowfish.MODE_ECB)
    ciphertext = cipher.encrypt(pad(data, Blowfish.block_size))

    file_name, file_extension = os.path.splitext(input_file)
    output_file = file_name + '_enc' + file_extension
    with open(f'downloads/{output_file}', 'wb') as file:
        file.write(ciphertext)

    return key.hex()


def decrypt_file_blowfish(input_file, key_hex):
    key = bytes.fromhex(key_hex)

    with open(input_file, 'rb') as file:
        ciphertext = file.read()

    cipher = Blowfish.new(key, Blowfish.MODE_ECB)
    plaintext = unpad(cipher.decrypt(ciphertext), Blowfish.block_size)

    name, extension = os.path.splitext(input_file)
    output_file = name.replace('_enc', '_decrypted') + extension
    with open(output_file, 'wb') as file:
        file.write(plaintext)

    return output_file
