from Cryptodome.Cipher import Blowfish
from Cryptodome.Util.Padding import pad, unpad
from Cryptodome.Random import get_random_bytes


def encrypt_file_blowfish(input_file):
    key = get_random_bytes(16)
    with open(f'downloads/{input_file}', 'rb') as file:
        data = file.read()

    cipher = Blowfish.new(key, Blowfish.MODE_ECB)
    ciphertext = cipher.encrypt(pad(data, Blowfish.block_size))

    output_file = input_file + '.enc'
    with open(f'downloads/{output_file}', 'wb') as file:
        file.write(ciphertext)

    return key.hex()


def decrypt_file_blowfish(input_file, key_hex):
    key = bytes.fromhex(key_hex)

    with open(input_file, 'rb') as file:
        ciphertext = file.read()

    cipher = Blowfish.new(key, Blowfish.MODE_ECB)
    plaintext = unpad(cipher.decrypt(ciphertext), Blowfish.block_size)

    output_file = input_file.replace('.enc', '_decrypted')
    with open(output_file, 'wb') as file:
        file.write(plaintext)

    return output_file


"""
input_file = "111.txt"
key = get_random_bytes(16)  # Генерация случайного ключа длиной 16 байтов

# Шифрование файла
encrypted_file = encrypt_file_blowfish(input_file, key)
print("Файл успешно зашифрован с использованием Blowfish:", encrypted_file)

# Расшифровка файла
decrypted_file = decrypt_file_blowfish(encrypted_file, key)
print("Файл успешно расшифрован с использованием Blowfish:", decrypted_file)

"""