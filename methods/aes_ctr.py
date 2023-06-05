from Crypto.Cipher import AES
from Crypto.Util import Counter
from Crypto.Random import get_random_bytes


def encrypt_file_aes_ctr(input_file):
    key = get_random_bytes(16)
    with open(f'downloads/{input_file}', 'rb') as file:
        data = file.read()

    nonce = get_random_bytes(8)
    counter = Counter.new(64, prefix=nonce)
    cipher = AES.new(key, AES.MODE_CTR, counter=counter)
    ciphertext = cipher.encrypt(data)

    output_file = input_file + '.enc'
    with open(f'downloads/{output_file}', 'wb') as file:
        file.write(nonce + ciphertext)

    return key.hex()


def decrypt_file_aes_ctr(input_file, key_hex):
    key = bytes.fromhex(key_hex)

    with open(input_file, 'rb') as file:
        encrypted_data = file.read()

    nonce = encrypted_data[:8]
    ciphertext = encrypted_data[8:]

    counter = Counter.new(64, prefix=nonce)
    cipher = AES.new(key, AES.MODE_CTR, counter=counter)
    plaintext = cipher.decrypt(ciphertext)

    output_file = input_file.replace('.enc', '_decrypted')
    with open(output_file, 'wb') as file:
        file.write(plaintext)

    return output_file


"""
input_file = "111.txt"
key = get_random_bytes(16)  # Генерация случайного ключа длиной 16 байтов

# Шифрование файла
encrypted_file = encrypt_file_aes_ctr(input_file, key)
print("Файл успешно зашифрован с использованием AES-CTR:", encrypted_file)

# Расшифровка файла
decrypted_file = decrypt_file_aes_ctr(encrypted_file, key)
print("Файл успешно расшифрован с использованием AES-CTR:", decrypted_file)
"""