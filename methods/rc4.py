import random


def encrypt_rc4(input_file):
    key = ''
    for x in range(16):  # Количество символов (16)
        key += random.choice(list(
            '1234567890abcdefghigklmnopqrstuvyxwzABCDEFGHIGKLMNOPQRSTUVYXWZ'))  # Символы, из которых будет составлен пароль

    with open(f'downloads/{input_file}', 'rb') as file:
        data = file.read()

    cipher = RC4(key)
    ciphertext = cipher.encrypt(data)

    output_file = input_file + '.enc'
    with open(f'downloads/{output_file}', 'wb') as file:
        file.write(ciphertext)

    return key


def decrypt_rc4(input_file, key):
    with open(input_file, 'rb') as file:
        ciphertext = file.read()

    cipher = RC4(key)
    plaintext = cipher.decrypt(ciphertext)

    output_file = input_file.replace('.enc', '_decrypted')
    with open(output_file, 'wb') as file:
        file.write(plaintext)

    return output_file


class RC4:
    def __init__(self, key):
        self.key = bytearray(key.encode())

    def _ksa(self):
        key_len = len(self.key)
        self.S = list(range(256))

        j = 0
        for i in range(256):
            j = (j + self.S[i] + self.key[i % key_len]) % 256
            self.S[i], self.S[j] = self.S[j], self.S[i]

    def _prga(self, length):
        self._ksa()
        i = 0
        j = 0
        keystream = bytearray()

        for _ in range(length):
            i = (i + 1) % 256
            j = (j + self.S[i]) % 256
            self.S[i], self.S[j] = self.S[j], self.S[i]
            keystream.append(self.S[(self.S[i] + self.S[j]) % 256])

        return keystream

    def encrypt(self, data):
        keystream = self._prga(len(data))
        return bytes(x ^ y for x, y in zip(data, keystream))

    def decrypt(self, data):
        return self.encrypt(data)
