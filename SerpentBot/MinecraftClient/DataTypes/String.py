from .VarInt import VarInt

class String:
    @staticmethod
    def encode (_str):
        str_as_bytes = _str.encode ("utf-8")
        return VarInt.encode (len (str_as_bytes)) + str_as_bytes
    @staticmethod
    def decode (stream):
        str_len, str_len_len = VarInt.decode (stream)
        return stream.recv (str_len).decode ("utf-8"), str_len_len + str_len
