import random


def encrypt_file_xor(input_file):
    key = random.randint(0, 256)
    with open(f'downloads/{input_file}', 'rb') as file:
        data = file.read()

    encrypted_data = bytes(x ^ key for x in data)

    output_file = input_file + '.enc'
    with open(f'downloads/{output_file}', 'wb') as file:
        file.write(encrypted_data)

    return key


def decrypt_file_xor(input_file, key):
    with open(input_file, 'rb') as file:
        encrypted_data = file.read()

    decrypted_data = bytes(x ^ key for x in encrypted_data)

    output_file = input_file.replace('.enc', '_decrypted')
    with open(output_file, 'wb') as file:
        file.write(decrypted_data)

    return output_file


"""
input_file = "111.txt"
key = 123  # Пример ключа (целое число)

# Шифрование файла
encrypted_file = encrypt_file_xor(input_file, key)
print("Файл успешно зашифрован с использованием XOR:", encrypted_file)

# Расшифровка файла
decrypted_file = decrypt_file_xor(encrypted_file, key)
print("Файл успешно расшифрован с использованием XOR:", decrypted_file)
"""