import cryptography.hazmat.primitives.ciphers

class EncryptedSocket:
    def __init__ (self, real_socket, *, key, iv):
        self.real_socket = real_socket
        aes_algo = cryptography.hazmat.primitives.ciphers.algorithms.AES (key)
        aes_mode = cryptography.hazmat.primitives.ciphers.modes.CFB8 (iv)
        self.aes_cipher = cryptography.hazmat.primitives.ciphers.Cipher (aes_algo, aes_mode)
        self.aes_encryptor = self.aes_cipher.encryptor ()
        self.aes_decryptor = self.aes_cipher.decryptor ()
    def recv (self, *args, **kwargs):
        encrypted_data = self.real_socket.recv (*args, **kwargs)
        data = self.aes_decryptor.update (encrypted_data)
        return data
    def send (self, data, *args, **kwargs):
        encrypted_data = self.aes_encryptor.update (data)
        return self.real_socket.send (data, *args, **kwargs)
