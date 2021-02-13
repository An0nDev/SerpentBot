# WARNING: API doesn't match! decode needs custom length attrib

class ByteArray:
    @staticmethod
    def encode (_bytes): return _bytes
    @staticmethod
    def decode (stream, length): return stream.recv (length), length
